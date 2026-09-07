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
const SETUP_COLORS = ['#ff4fc3','#ffd92f','#6ab34c','#7ec8ff','#ff3b30'];
const SETUP_PORTRAITS = [
  { key: 'GB_A', faction: 0 }, { key: 'GB_B', faction: 0 },
  { key: 'R_A', faction: 1 }, { key: 'R_B', faction: 1 },
  { key: 'Y_A', faction: 2 }, { key: 'Y_B', faction: 2 }
];
const SETUP_REGIONS = {
  A: ['A1','A2','A3','A4'],
  B: ['B1','B2','B4','B5'],
  C: ['C1','C2','C4','C5'],
  D: ['D1','D2','D3','D4'],
  E: ['E1','E2','E3','E5'],
  F: ['F1','F2','F4','F5'],
  G: ['G1','G3','G4','G5'],
  H: ['H1','H2','H4','H5'],
  I: ['I1','I2','I3','I4']
};
const ALL_REGIONS = Object.values(SETUP_REGIONS).flat().concat(['A5','B3','C3','D5','E4','F3','G2','H3','I5']);
const HOSTILE_REGIONS = new Set(['A5','B3','C3','D5','E4','F3','G2','H3','I5']);
const CARD_COUNTS = [4,4,2,3,3,1,2,3,4,3,1,4,2,3,4,1,4,3,1,2,1,3];

function cleanText(value, max = 30) {
  return String(value || '').trim().replace(/\s+/g, ' ').slice(0, max);
}
function cleanCode(value) {
  return cleanText(value, 12).toUpperCase().replace(/[^A-Z0-9_-]/g, '');
}
function randomPseudo() {
  return DEFAULT_NAMES[Math.floor(Math.random() * DEFAULT_NAMES.length)];
}
function seededRandom(seed) {
  let x = (Number(seed) || 1) >>> 0;
  return () => {
    x = (x + 0x6D2B79F5) >>> 0;
    let t = x;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
function shuffle(list, rng = Math.random) {
  for (let i = list.length - 1; i > 0; i--) {
    const j = Math.floor(rng() * (i + 1));
    [list[i], list[j]] = [list[j], list[i]];
  }
  return list;
}
function makeDeck(rng) {
  const deck = [];
  CARD_COUNTS.forEach((count, cardId) => {
    for (let n = 0; n < count; n++) deck.push(cardId);
  });
  return shuffle(deck, rng);
}
function drawCards(game, seat, count) {
  const player = game.players[seat];
  if (!player) return;
  for (let i = 0; i < count && game.deck.length; i++) player.hand.push(game.deck.pop());
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
function gameSeatForSocket(room, socketId) {
  if (!room || !room.game) return -1;
  return room.game.players.findIndex(p => !p.bot && p.socketId === socketId);
}
function gamePermissions(room, socketId) {
  const game = room && room.game;
  if (!game) return {};
  const seat = gameSeatForSocket(room, socketId);
  const ownTurn = seat >= 0 && game.activeSeat === seat;
  return {
    seat,
    canSetup: game.phase === 'setup' && game.setup.activeSeat === seat,
    canDraw: game.phase === 'start' && ownTurn,
    canHarvest: false,
    canRecruit: false,
    canAct: game.phase === 'play' && ownTurn,
    canOracle: game.phase === 'oracle' && ownTurn
  };
}
function publicGameFor(room, socketId) {
  const game = room.game;
  const seat = gameSeatForSocket(room, socketId);
  return {
    code: room.code,
    mode: room.mode,
    victoryPoints: room.victoryPoints,
    revision: game.revision,
    phase: game.phase,
    activeSeat: game.activeSeat,
    dragon: game.dragon,
    setup: game.phase === 'setup' ? {
      activeSeat: game.setup.activeSeat,
      usedColors: game.players.map(p => p.color).filter(Boolean),
      usedPortraits: game.players.map(p => p.portrait).filter(Boolean)
    } : null,
    players: game.players.map((p, i) => ({
      seat: i,
      pseudo: p.pseudo,
      bot: p.bot,
      color: p.color,
      portrait: p.portrait,
      faction: p.faction,
      province: p.province,
      regions: p.regions.slice(),
      gold: p.gold,
      handCount: p.hand.length,
      hand: i === seat ? p.hand.slice() : undefined
    })),
    board: game.board,
    permissions: gamePermissions(room, socketId)
  };
}
function emitGame(room) {
  if (!room.game) return;
  room.players.forEach(p => {
    const socket = io.sockets.sockets.get(p.id);
    if (socket) socket.emit('gameState', publicGameFor(room, p.id));
  });
}
function autoConfigureBot(game, seat, rng) {
  const player = game.players[seat];
  const usedColors = new Set(game.players.map(p => p.color).filter(Boolean));
  const usedPortraits = new Set(game.players.map(p => p.portrait).filter(Boolean));
  const color = SETUP_COLORS.find(c => !usedColors.has(c));
  const portrait = SETUP_PORTRAITS.find(p => !usedPortraits.has(p.key));
  const eligible = SETUP_REGIONS[player.province].slice();
  shuffle(eligible, rng);
  applySetupChoice(game, seat, color, portrait.key, eligible.slice(0, 2));
}
function applySetupChoice(game, seat, color, portraitKey, regions) {
  const player = game.players[seat];
  const portrait = SETUP_PORTRAITS.find(p => p.key === portraitKey);
  player.color = color;
  player.portrait = portraitKey;
  player.faction = portrait.faction;
  player.regions = regions.slice();
  regions.forEach(region => {
    game.board[region].owner = seat;
    game.board[region].units = 3;
    game.board[region].hostile = false;
  });
}
function finishSetupIfReady(game) {
  if (game.phase !== 'setup') return false;
  if (game.players.some(p => !p.color || !p.portrait || p.regions.length !== 2)) return false;
  game.phase = 'start';
  game.setup.activeSeat = null;
  game.activeSeat = 0;
  game.players.forEach((_p, seat) => drawCards(game, seat, 3));
  game.revision++;
  return true;
}
function advanceSetup(game) {
  if (finishSetupIfReady(game)) return;
  let next = game.setup.activeSeat === null ? 0 : game.setup.activeSeat + 1;
  while (next < game.players.length && game.players[next].color) next++;
  game.setup.activeSeat = next < game.players.length ? next : null;
}
function resolveAutomaticSetup(game) {
  const rng = game.rng;
  while (game.phase === 'setup' && game.setup.activeSeat !== null && game.players[game.setup.activeSeat].bot) {
    autoConfigureBot(game, game.setup.activeSeat, rng);
    game.revision++;
    advanceSetup(game);
  }
  finishSetupIfReady(game);
}
function createAuthoritativeGame(room) {
  const rng = seededRandom(room.seed);
  const humans = room.players.map(p => ({ socketId: p.id, pseudo: p.pseudo, bot: false }));
  const bots = Array.from({ length: room.bots }, (_, i) => ({ socketId: null, pseudo: `Bot ${i + 1}`, bot: true }));
  const participants = shuffle(humans, rng).concat(bots);
  const provinces = shuffle(Object.keys(SETUP_REGIONS), rng).slice(0, participants.length);
  const board = {};
  ALL_REGIONS.forEach(region => {
    board[region] = { owner: null, units: 0, hostile: HOSTILE_REGIONS.has(region) };
  });
  const game = {
    revision: 1,
    phase: 'setup',
    activeSeat: 0,
    dragon: 'E4',
    rng,
    deck: makeDeck(rng),
    discard: [],
    board,
    setup: { activeSeat: 0 },
    players: participants.map((p, seat) => ({
      seat,
      socketId: p.socketId,
      pseudo: p.pseudo,
      bot: p.bot,
      province: provinces[seat],
      color: null,
      portrait: null,
      faction: null,
      regions: [],
      hand: [],
      gold: 0
    }))
  };
  resolveAutomaticSetup(game);
  return game;
}
function validateSetupChoice(room, socket, payload) {
  const game = room.game;
  if (!game || game.phase !== 'setup') return 'La phase de création est terminée.';
  const seat = gameSeatForSocket(room, socket.id);
  if (seat < 0) return 'Joueur introuvable dans la partie.';
  if (game.setup.activeSeat !== seat) return "Ce n'est pas votre tour de choisir.";
  const player = game.players[seat];
  const color = cleanText(payload.color, 20);
  const portraitKey = cleanText(payload.portrait, 10);
  const regions = Array.isArray(payload.regions) ? payload.regions.map(r => cleanText(r, 3)) : [];
  if (!SETUP_COLORS.includes(color)) return 'Couleur invalide.';
  if (game.players.some((p, i) => i !== seat && p.color === color)) return 'Cette couleur est déjà prise.';
  if (!SETUP_PORTRAITS.some(p => p.key === portraitKey)) return 'Faction invalide.';
  if (game.players.some((p, i) => i !== seat && p.portrait === portraitKey)) return 'Cet encart de faction est déjà pris.';
  if (regions.length !== 2 || new Set(regions).size !== 2) return 'Choisissez exactement 2 régions différentes.';
  const eligible = SETUP_REGIONS[player.province] || [];
  if (!regions.every(r => eligible.includes(r))) return 'Une région choisie ne fait pas partie de votre province attribuée.';
  return null;
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
  if (room.launched && room.game) emitGame(room);
}

io.on('connection', socket => {
  socket.emit('serverReady', { ok: true, authority: 'server-v1' });

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
      game: null,
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
    room.game = createAuthoritativeGame(room);
    ack({ ok: true });
    io.to(room.code).emit('gameLaunched', publicRoom(room));
    emitGame(room);
  });

  socket.on('setupChoice', (payload = {}, ack = () => {}) => {
    const room = roomForSocket(socket);
    if (!room || !room.launched || !room.game) return ack({ ok: false, error: 'Partie indisponible.' });
    const error = validateSetupChoice(room, socket, payload);
    if (error) return ack({ ok: false, error });
    const game = room.game;
    const seat = gameSeatForSocket(room, socket.id);
    applySetupChoice(game, seat, payload.color, payload.portrait, payload.regions);
    game.revision++;
    advanceSetup(game);
    resolveAutomaticSetup(game);
    ack({ ok: true, game: publicGameFor(room, socket.id) });
    emitGame(room);
  });

  socket.on('gameAction', (payload = {}, ack = () => {}) => {
    const room = roomForSocket(socket);
    if (!room || !room.launched || !room.game) return ack({ ok: false, error: 'Partie indisponible.' });
    const game = room.game;
    const seat = gameSeatForSocket(room, socket.id);
    const type = cleanText(payload.type, 24).toUpperCase();
    if (seat < 0) return ack({ ok: false, error: 'Joueur introuvable.' });
    if (game.activeSeat !== seat) return ack({ ok: false, error: "Ce n'est pas votre tour." });
    if (type === 'DRAW') {
      if (game.phase !== 'start') return ack({ ok: false, error: 'Vous ne pouvez pas piocher maintenant.' });
      drawCards(game, seat, 2);
      game.phase = 'play';
      game.revision++;
      ack({ ok: true });
      emitGame(room);
      return;
    }
    ack({ ok: false, error: 'Action Online non encore disponible.' });
  });

  socket.on('requestGameState', (_payload, ack = () => {}) => {
    const room = roomForSocket(socket);
    if (!room || !room.game) return ack({ ok: false, error: 'Partie indisponible.' });
    ack({ ok: true, game: publicGameFor(room, socket.id) });
  });

  socket.on('leaveRoom', () => leaveCurrentRoom(socket));
  socket.on('disconnect', () => leaveCurrentRoom(socket));
});

server.listen(PORT, () => console.log(`TRIBU Online server listening on ${PORT}`));
