const express = require('express');
const cors = require('cors');
const http = require('http');
const { Server } = require('socket.io');

const PORT = process.env.PORT || 3000;
const CLIENT_ORIGIN = process.env.CLIENT_ORIGIN || '*';
const app = express();
app.use(cors({ origin: CLIENT_ORIGIN }));
app.get('/', (_req, res) => res.json({ ok: true, service: 'TRIBU Online beta', rooms: rooms.size }));
app.get('/health', (_req, res) => res.json({ ok: true }));

const server = http.createServer(app);
const io = new Server(server, {
  cors: { origin: CLIENT_ORIGIN, methods: ['GET', 'POST'] }
});

const rooms = new Map();
const DEFAULT_NAMES = ['Aube','Brume','Croc','Dune','Écorce','Faucon','Givre','Lune','Silex','Torrent'];

function cleanText(value, max = 30) {
  return String(value || '').trim().replace(/\s+/g, ' ').slice(0, max);
}
function cleanCode(value) {
  return cleanText(value, 12).toUpperCase().replace(/[^A-Z0-9_-]/g, '');
}
function randomPseudo() {
  return DEFAULT_NAMES[Math.floor(Math.random() * DEFAULT_NAMES.length)];
}
function publicRoom(room) {
  return {
    code: room.code,
    name: room.name,
    mode: room.mode,
    maxHumans: room.maxHumans,
    bots: room.bots,
    victoryPoints: room.victoryPoints,
    hostId: room.hostId,
    launched: room.launched,
    seed: room.launched ? room.seed : null,
    players: room.players.map(p => ({ id: p.id, pseudo: p.pseudo, ready: p.ready, host: p.id === room.hostId }))
  };
}
function emitRoom(room) {
  io.to(room.code).emit('roomState', publicRoom(room));
}
function roomForSocket(socket) {
  const code = socket.data.roomCode;
  return code ? rooms.get(code) : null;
}
function leaveCurrentRoom(socket) {
  const room = roomForSocket(socket);
  if (!room) return;
  room.players = room.players.filter(p => p.id !== socket.id);
  socket.leave(room.code);
  socket.data.roomCode = null;
  if (!room.players.length) {
    rooms.delete(room.code);
    return;
  }
  if (room.hostId === socket.id) room.hostId = room.players[0].id;
  emitRoom(room);
}

io.on('connection', socket => {
  socket.emit('serverReady', { ok: true });

  socket.on('createRoom', (payload = {}, ack = () => {}) => {
    leaveCurrentRoom(socket);
    const code = cleanCode(payload.code);
    if (code.length < 3) return ack({ ok: false, error: 'Le code doit contenir au moins 3 caractères.' });
    if (rooms.has(code)) return ack({ ok: false, error: 'Ce code de partie existe déjà.' });
    const maxHumans = Math.max(2, Math.min(5, Number(payload.maxHumans) || 3));
    const bots = Math.max(0, Math.min(4, Number(payload.bots) || 0));
    const victoryPoints = [3,4,5].includes(Number(payload.victoryPoints)) ? Number(payload.victoryPoints) : 3;
    const pseudo = cleanText(payload.pseudo, 24) || randomPseudo();
    const room = {
      code,
      name: cleanText(payload.name, 30) || `Partie ${code}`,
      mode: cleanText(payload.mode, 20),
      maxHumans,
      bots,
      victoryPoints,
      hostId: socket.id,
      launched: false,
      seed: null,
      players: [{ id: socket.id, pseudo, ready: false }]
    };
    rooms.set(code, room);
    socket.join(code);
    socket.data.roomCode = code;
    ack({ ok: true, room: publicRoom(room) });
    emitRoom(room);
  });

  socket.on('joinRoom', (payload = {}, ack = () => {}) => {
    leaveCurrentRoom(socket);
    const code = cleanCode(payload.code);
    const room = rooms.get(code);
    if (!room) return ack({ ok: false, error: 'Partie introuvable.' });
    if (room.launched) return ack({ ok: false, error: 'Cette partie a déjà commencé.' });
    if (room.players.length >= room.maxHumans) return ack({ ok: false, error: 'Cette partie est complète.' });
    const pseudo = cleanText(payload.pseudo, 24) || randomPseudo();
    room.players.push({ id: socket.id, pseudo, ready: false });
    socket.join(code);
    socket.data.roomCode = code;
    ack({ ok: true, room: publicRoom(room) });
    emitRoom(room);
  });

  socket.on('setReady', (ready, ack = () => {}) => {
    const room = roomForSocket(socket);
    if (!room || room.launched) return ack({ ok: false, error: 'Salon indisponible.' });
    const player = room.players.find(p => p.id === socket.id);
    if (!player) return ack({ ok: false, error: 'Joueur introuvable.' });
    player.ready = !!ready;
    ack({ ok: true });
    emitRoom(room);
  });

  socket.on('launchGame', (_payload, ack = () => {}) => {
    const room = roomForSocket(socket);
    if (!room) return ack({ ok: false, error: 'Salon introuvable.' });
    if (room.hostId !== socket.id) return ack({ ok: false, error: 'Seul le créateur peut lancer la partie.' });
    if (room.players.length !== room.maxHumans) return ack({ ok: false, error: 'Il manque encore des joueurs ou des joueuses.' });
    if (!room.players.every(p => p.ready)) return ack({ ok: false, error: 'Tout le monde doit être prêt·e.' });
    room.seed = Math.floor(Math.random() * 0x100000000) >>> 0;
    room.launched = true;
    ack({ ok: true });
    io.to(room.code).emit('gameLaunched', publicRoom(room));
  });

  socket.on('leaveRoom', () => leaveCurrentRoom(socket));
  socket.on('disconnect', () => leaveCurrentRoom(socket));
});

server.listen(PORT, () => console.log(`TRIBU Online server listening on ${PORT}`));
