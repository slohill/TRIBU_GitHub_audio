const express = require('express');
const cors = require('cors');
const http = require('http');
const crypto = require('crypto');
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
const COLORS = ['#ff4fc3','#ffd92f','#6ab34c','#7ec8ff','#ff3b30'];
const PORTRAITS = ['GB_A','GB_B','R_A','R_B','Y_A','Y_B'];
const PORTRAIT_FACTION = { GB_A:0, GB_B:0, R_A:1, R_B:1, Y_A:2, Y_B:2 };
const PROVINCES = ['A','B','C','D','E','F','G','H','I'];
const PROVINCE_REGIONS = {
  A:['A1','A2','A3','A4'], B:['B1','B2','B4','B5'], C:['C1','C2','C4','C5'],
  D:['D1','D2','D3','D4'], E:['E1','E2','E3','E5'], F:['F1','F2','F4','F5'],
  G:['G1','G3','G4','G5'], H:['H1','H2','H4','H5'], I:['I1','I2','I3','I4']
};
const HOSTILE_REGIONS = new Set(['A5','B3','C3','D5','E4','F3','G2','H3','I5']);
const ALL_REGIONS = Array.from({ length: 9 }, (_, p) => {
  const letter = String.fromCharCode(65 + p);
  return Array.from({ length: 5 }, (_, n) => `${letter}${n + 1}`);
}).flat();
const CARD_COUNTS = [4,4,2,3,3,1,2,3,4,3,1,4,2,3,4,1,4,3,1,2,1,3];
const ORACLE_IDS = [0,1,2,2,3,3,4,5];
const FACTION_CAP = [3,3,2];
const TERRAIN = {};
['A1','A2','A3','A4','A5','B1','B2','C1','C2','C3'].forEach(r=>TERRAIN[r]='e');
['B3','B4','B5','C4','C5','D1','D2','D3','D4','D5','E1','E2','E3','E4','E5','F1','F2','F3','F4','F5','G1','H1','H2','H3','H4'].forEach(r=>TERRAIN[r]='t');
['G2','G3','G4','G5','H5','I1','I2','I3','I4','I5'].forEach(r=>TERRAIN[r]='d');

function cleanText(value, max = 30) {
  return String(value || '').trim().replace(/\s+/g, ' ').slice(0, max);
}
function cleanCode(value) {
  return cleanText(value, 12).toUpperCase().replace(/[^A-Z0-9_-]/g, '');
}
function reconnectToken() { return crypto.randomBytes(24).toString('hex'); }
function playerId() { return crypto.randomUUID ? crypto.randomUUID() : crypto.randomBytes(16).toString('hex'); }
function randomPseudo() {
  return DEFAULT_NAMES[Math.floor(Math.random() * DEFAULT_NAMES.length)];
}
function seededRandom(seed) {
  let a = (Number(seed) >>> 0) || 0x6d2b79f5;
  return function () {
    a |= 0;
    a = (a + 0x6D2B79F5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
function shuffle(array, random = Math.random) {
  for (let i = array.length - 1; i > 0; i--) {
    const j = Math.floor(random() * (i + 1));
    [array[i], array[j]] = [array[j], array[i]];
  }
  return array;
}
function makeDeck(random) {
  const deck = [];
  CARD_COUNTS.forEach((count, id) => { for (let n = 0; n < count; n++) deck.push(id); });
  return shuffle(deck, random);
}
function drawCards(game, playerIndex, count) {
  const hand = game.players[playerIndex].hand;
  for (let i = 0; i < count && game.deck.length; i++) hand.push(game.deck.pop());
}
function ownedRegionCount(game, playerIndex) {
  return Object.values(game.board).filter(c => c.owner === playerIndex && c.units > 0).length;
}
function totalUnitsFor(game, playerIndex) {
  return Object.values(game.board).reduce((n,c)=>n+(c.owner===playerIndex?c.units:0),0);
}
function unitCapFor(game, playerIndex) {
  const faction=game.players[playerIndex].faction;
  return ownedRegionCount(game,playerIndex)*(FACTION_CAP[faction]||2);
}
function makeBoard() {
  const board = {};
  ALL_REGIONS.forEach(id => {
    board[id] = { owner: null, units: 0, hostile: HOSTILE_REGIONS.has(id), originalHostile: HOSTILE_REGIONS.has(id), building: null };
  });
  return board;
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
    players: room.players.map(p => ({ id: p.id, playerId: p.playerId, pseudo: p.pseudo, ready: p.ready, host: p.id === room.hostId, connected: p.connected !== false }))
  };
}
function publicGameView(room, socketId) {
  const game = room.game;
  if (!game) return null;
  const youIndex = game.players.findIndex(p => p.socketId === socketId);
  return {
    code: room.code,
    mode: room.mode,
    victoryPoints: room.victoryPoints,
    seed: room.seed,
    revision: game.revision,
    status: game.status,
    phase: game.phase,
    turn: game.turn,
    active: game.active,
    dragon: game.dragon,
    setup: game.setup ? {
      activePlayer: game.setup.activePlayer,
      stage: game.setup.stage,
      usedColors: game.players.map(p => p.color).filter(Boolean),
      usedPortraits: game.players.map(p => p.portrait).filter(Boolean)
    } : null,
    youIndex,
    board: game.board,
    players: game.players.map((p, i) => ({
      index: i,
      pseudo: p.pseudo,
      bot: p.bot,
      connected: p.bot ? true : p.connected !== false,
      color: p.color,
      portrait: p.portrait,
      faction: p.faction,
      province: p.province,
      regions: p.regions.slice(),
      gold: p.gold,
      pvPermanent: p.pvPermanent,
      hand: i === youIndex ? p.hand.slice() : undefined,
      handCount: p.hand.length
    }))
  };
}
function emitRoom(room) {
  io.to(room.code).emit('roomState', publicRoom(room));
}
function emitGame(room) {
  if (!room.game) return;
  room.players.forEach(p => {
    const socket = io.sockets.sockets.get(p.id);
    if (socket) socket.emit('gameState', publicGameView(room, p.id));
  });
}
function roomForSocket(socket) {
  const code = socket.data.roomCode;
  return code ? rooms.get(code) : null;
}
function humanGameIndex(room, socketId) {
  return room.game ? room.game.players.findIndex(p => !p.bot && p.socketId === socketId) : -1;
}
function currentSetupPlayer(room) {
  if (!room.game || !room.game.setup) return null;
  return room.game.players[room.game.setup.activePlayer] || null;
}
function completeSetupIfReady(room) {
  const game = room.game;
  if (!game || !game.setup) return;
  const humanCount = room.maxHumans;
  if (game.setup.activePlayer < humanCount) return;

  const random = seededRandom((room.seed ^ 0xa5a5a5a5) >>> 0);
  const freeColors = COLORS.filter(c => !game.players.some(p => p.color === c));
  const freePortraits = PORTRAITS.filter(p => !game.players.some(x => x.portrait === p));
  for (let i = humanCount; i < game.players.length; i++) {
    const bot = game.players[i];
    bot.color = freeColors.shift() || COLORS[i % COLORS.length];
    bot.portrait = freePortraits.shift() || PORTRAITS[i % PORTRAITS.length];
    bot.faction = PORTRAIT_FACTION[bot.portrait] ?? (i % 3);
    const allowed = PROVINCE_REGIONS[bot.province].slice();
    shuffle(allowed, random);
    bot.regions = allowed.slice(0, 2);
    bot.regions.forEach(r => {
      game.board[r].owner = i;
      game.board[r].units = 3;
      game.board[r].hostile = false;
    });
  }

  game.players.forEach((_, i) => drawCards(game, i, 3));
  game.setup = null;
  game.status = 'playing';
  game.phase = 'start';
  game.turn = 1;
  game.active = 0;
  game.revision++;
  emitGame(room);
}
function buildAuthoritativeGame(room) {
  const random = seededRandom(room.seed);
  const humans = room.players.map(p => ({
    socketId: p.id,
    playerId: p.playerId,
    pseudo: p.pseudo,
    bot: false,
    connected: p.connected !== false,
    color: null,
    portrait: null,
    faction: null,
    province: null,
    regions: [],
    gold: 0,
    pvPermanent: 0,
    hand: []
  }));
  shuffle(humans, random);

  const totalPlayers = Math.min(5, room.maxHumans + room.bots);
  const players = humans.slice(0, room.maxHumans);
  for (let i = players.length; i < totalPlayers; i++) {
    players.push({
      socketId: null,
      pseudo: `Bot ${i - room.maxHumans + 1}`,
      bot: true,
      connected: true,
      color: null,
      portrait: null,
      faction: null,
      province: null,
      regions: [],
      gold: 0,
      pvPermanent: 0,
      hand: []
    });
  }

  const provinces = shuffle(PROVINCES.slice(), random).slice(0, totalPlayers);
  players.forEach((p, i) => { p.province = provinces[i]; });

  return {
    revision: 1,
    status: 'setup',
    phase: 'setup',
    turn: 0,
    active: null,
    dragon: 'E4',
    board: makeBoard(),
    deck: makeDeck(random),
    discard: [],
    oracleDeck: shuffle(ORACLE_IDS.slice(), random),
    oracleDiscard: [],
    oracleActive: null,
    players,
    setup: { activePlayer: 0, stage: 'identity' }
  };
}
function leaveCurrentRoom(socket) {
  const room = roomForSocket(socket);
  if (!room) return;
  socket.leave(room.code);
  socket.data.roomCode = null;

  if (room.launched) {
    const lobbyPlayer = room.players.find(p => p.id === socket.id);
    if (lobbyPlayer) lobbyPlayer.connected = false;
    const gi = humanGameIndex(room, socket.id);
    if (gi >= 0) room.game.players[gi].connected = false;
    emitRoom(room);
    emitGame(room);
    return;
  }

  room.players = room.players.filter(p => p.id !== socket.id);
  if (!room.players.length) {
    rooms.delete(room.code);
    return;
  }
  if (room.hostId === socket.id) room.hostId = room.players[0].id;
  emitRoom(room);
}
function rejectGameAction(ack, error) {
  ack({ ok: false, error });
}

io.on('connection', socket => {
  socket.emit('serverReady', { ok: true, authority: 'server' });

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
      players: [{ id: socket.id, playerId: playerId(), reconnectToken: reconnectToken(), pseudo, ready: false, connected: true }]
    };
    rooms.set(code, room);
    socket.join(code);
    socket.data.roomCode = code;
    ack({ ok: true, room: publicRoom(room), resume: { code, pseudo, playerId: room.players[0].playerId, token: room.players[0].reconnectToken } });
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
    const joined = { id: socket.id, playerId: playerId(), reconnectToken: reconnectToken(), pseudo, ready: false, connected: true };
    room.players.push(joined);
    socket.join(code);
    socket.data.roomCode = code;
    ack({ ok: true, room: publicRoom(room), resume: { code, pseudo: joined.pseudo, playerId: joined.playerId, token: joined.reconnectToken } });
    emitRoom(room);
  });

  socket.on('resumeRoom', (payload = {}, ack = () => {}) => {
    const code = cleanCode(payload.code), pid = cleanText(payload.playerId, 80), token = cleanText(payload.token, 120);
    const room = rooms.get(code);
    if (!room || !room.launched || !room.game) return ack({ ok:false, error:'Cette partie en cours n’est plus disponible.' });
    const lobbyPlayer = room.players.find(p => p.playerId === pid && p.reconnectToken === token);
    if (!lobbyPlayer) return ack({ ok:false, error:'Impossible de vérifier votre place dans cette partie.' });
    leaveCurrentRoom(socket);
    const oldSocketId=lobbyPlayer.id; lobbyPlayer.id=socket.id; lobbyPlayer.connected=true;
    if (room.hostId===oldSocketId) room.hostId=socket.id;
    const gp=room.game.players.find(p=>!p.bot&&p.playerId===pid);
    if(!gp) return ack({ok:false,error:'Siège de jeu introuvable.'});
    gp.socketId=socket.id;gp.connected=true;socket.join(code);socket.data.roomCode=code;
    const resume={code,pseudo:lobbyPlayer.pseudo,playerId:pid,token:lobbyPlayer.reconnectToken};
    ack({ok:true,room:publicRoom(room),game:publicGameView(room,socket.id),resume});emitRoom(room);emitGame(room);
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
    room.game = buildAuthoritativeGame(room);
    ack({ ok: true });
    io.to(room.code).emit('gameLaunched', publicRoom(room));
    emitGame(room);
  });

  socket.on('requestGameState', (_payload, ack = () => {}) => {
    const room = roomForSocket(socket);
    if (!room || !room.game) return rejectGameAction(ack, 'Aucune partie active.');
    ack({ ok: true, game: publicGameView(room, socket.id) });
  });

  socket.on('setupComplete', (payload = {}, ack = () => {}) => {
    const room = roomForSocket(socket);
    if (!room || !room.game || !room.game.setup) return rejectGameAction(ack, 'Installation indisponible.');
    const game = room.game;
    const index = humanGameIndex(room, socket.id);
    if (index < 0) return rejectGameAction(ack, 'Joueur introuvable.');
    if (game.setup.activePlayer !== index) return rejectGameAction(ack, 'Ce n’est pas votre tour de vous installer.');
    const color = String(payload.color || ''), portrait = String(payload.portrait || '');
    const unique = [...new Set(Array.isArray(payload.regions) ? payload.regions.map(String) : [])];
    const player = game.players[index], allowed = PROVINCE_REGIONS[player.province] || [];
    if (!COLORS.includes(color)) return rejectGameAction(ack, 'Couleur invalide.');
    if (!PORTRAITS.includes(portrait)) return rejectGameAction(ack, 'Faction invalide.');
    if (game.players.some((p, i) => i !== index && p.color === color)) return rejectGameAction(ack, 'Cette couleur est déjà prise.');
    if (game.players.some((p, i) => i !== index && p.portrait === portrait)) return rejectGameAction(ack, 'Cet encart de faction est déjà pris.');
    if (unique.length !== 2 || !unique.every(r => allowed.includes(r))) return rejectGameAction(ack, 'Choisissez exactement deux régions valides de votre province.');
    player.color=color; player.portrait=portrait; player.faction=PORTRAIT_FACTION[portrait]; player.regions=unique;
    unique.forEach(r => { game.board[r].owner=index; game.board[r].units=3; game.board[r].hostile=false; });
    game.setup.activePlayer++; game.setup.stage='identity'; game.revision++;
    ack({ok:true}); completeSetupIfReady(room); if(game.setup) emitGame(room);
  });

  socket.on('setupIdentity', (payload = {}, ack = () => {}) => {
    const room = roomForSocket(socket);
    if (!room || !room.game || !room.game.setup) return rejectGameAction(ack, 'Installation indisponible.');
    const game = room.game;
    const index = humanGameIndex(room, socket.id);
    if (index < 0) return rejectGameAction(ack, 'Joueur introuvable.');
    if (game.setup.activePlayer !== index || game.setup.stage !== 'identity') return rejectGameAction(ack, 'Ce n’est pas votre tour de choisir votre identité.');

    const color = String(payload.color || '');
    const portrait = String(payload.portrait || '');
    if (!COLORS.includes(color)) return rejectGameAction(ack, 'Couleur invalide.');
    if (!PORTRAITS.includes(portrait)) return rejectGameAction(ack, 'Faction invalide.');
    if (game.players.some((p, i) => i !== index && p.color === color)) return rejectGameAction(ack, 'Cette couleur est déjà prise.');
    if (game.players.some((p, i) => i !== index && p.portrait === portrait)) return rejectGameAction(ack, 'Cet encart de faction est déjà pris.');

    const player = game.players[index];
    player.color = color;
    player.portrait = portrait;
    player.faction = PORTRAIT_FACTION[portrait];
    game.setup.stage = 'regions';
    game.revision++;
    ack({ ok: true });
    emitGame(room);
  });

  socket.on('setupRegions', (payload = {}, ack = () => {}) => {
    const room = roomForSocket(socket);
    if (!room || !room.game || !room.game.setup) return rejectGameAction(ack, 'Installation indisponible.');
    const game = room.game;
    const index = humanGameIndex(room, socket.id);
    if (index < 0) return rejectGameAction(ack, 'Joueur introuvable.');
    if (game.setup.activePlayer !== index || game.setup.stage !== 'regions') return rejectGameAction(ack, 'Ce n’est pas votre tour de choisir vos régions.');

    const regions = Array.isArray(payload.regions) ? payload.regions.map(String) : [];
    const unique = [...new Set(regions)];
    const allowed = PROVINCE_REGIONS[game.players[index].province] || [];
    if (unique.length !== 2 || !unique.every(r => allowed.includes(r))) return rejectGameAction(ack, 'Choisissez exactement deux régions valides de votre province.');

    const player = game.players[index];
    player.regions = unique;
    unique.forEach(r => {
      game.board[r].owner = index;
      game.board[r].units = 3;
      game.board[r].hostile = false;
    });
    game.setup.activePlayer++;
    game.setup.stage = 'identity';
    game.revision++;
    ack({ ok: true });
    completeSetupIfReady(room);
    if (game.setup) emitGame(room);
  });

  socket.on('gameAction', (payload = {}, ack = () => {}) => {
    const room = roomForSocket(socket);
    if (!room || !room.game || room.game.status !== 'playing') return rejectGameAction(ack, 'La partie n’est pas en cours.');
    const game = room.game;
    const index = humanGameIndex(room, socket.id);
    if (index < 0) return rejectGameAction(ack, 'Joueur introuvable.');
    if (game.active !== index) return rejectGameAction(ack, 'Ce n’est pas votre tour.');

    const type = String(payload.type || '');
    if (type === 'DRAW_START') {
      if (game.phase !== 'start') return rejectGameAction(ack, 'Vous ne pouvez pas piocher maintenant.');
      drawCards(game, index, 2); game.phase = 'play'; game.revision++; ack({ ok: true }); emitGame(room); return;
    }
    if (type === 'HARVEST_START') {
      if (game.phase !== 'start') return rejectGameAction(ack, 'Vous ne pouvez pas récolter maintenant.');
      game.players[index].gold += ownedRegionCount(game,index)*2; game.phase='play'; game.revision++; ack({ok:true}); emitGame(room); return;
    }
    if (type === 'RECRUIT_START') {
      if (game.phase !== 'start') return rejectGameAction(ack, 'Vous ne pouvez pas recruter maintenant.');
      game.recruitSnapshot={player:index,gold:game.players[index].gold,units:Object.fromEntries(Object.entries(game.board).map(([r,c])=>[r,c.units]))};
      game.phase='recruit'; game.revision++; ack({ok:true}); emitGame(room); return;
    }
    if (type === 'RESET_RECRUIT') {
      if (game.phase !== 'recruit' || !game.recruitSnapshot || game.recruitSnapshot.player!==index) return rejectGameAction(ack, 'Aucun recrutement à recommencer.');
      game.players[index].gold=game.recruitSnapshot.gold; Object.entries(game.recruitSnapshot.units).forEach(([r,u])=>{game.board[r].units=u}); game.revision++; ack({ok:true}); emitGame(room); return;
    }
    if (type === 'RECRUIT_AT') {
      if (game.phase !== 'recruit') return rejectGameAction(ack, 'Vous n’êtes pas en phase de recrutement.');
      const r=String(payload.region||''),cell=game.board[r],player=game.players[index];
      if (!cell || cell.owner!==index) return rejectGameAction(ack, 'Choisissez une de vos régions.');
      if (player.gold<1) return rejectGameAction(ack, 'Pas assez d’Or.');
      if (totalUnitsFor(game,index)>=unitCapFor(game,index)) return rejectGameAction(ack, 'Plafond d’unités atteint.');
      const terrain=TERRAIN[r],faction=player.faction;
      if(faction===0&&terrain==='d')return rejectGameAction(ack,'Les Griffes-Blanches ne recrutent pas dans le désert.');
      if(faction===1&&terrain==='e')return rejectGameAction(ack,'Les Reptones ne recrutent pas dans la neige.');
      let q=(faction===0&&terrain==='e')||(faction===1&&terrain==='d')?2:1; q=Math.min(q,unitCapFor(game,index)-totalUnitsFor(game,index));
      player.gold--; cell.units+=q; game.revision++; ack({ok:true}); emitGame(room); return;
    }
    if (type === 'END_RECRUIT') {
      if (game.phase !== 'recruit') return rejectGameAction(ack, 'Vous n’êtes pas en phase de recrutement.');
      game.recruitSnapshot=null; game.phase='play'; game.revision++; ack({ok:true}); emitGame(room); return;
    }
    return rejectGameAction(ack, 'Action Online pas encore migrée vers le serveur.');
  });

  socket.on('leaveRoom', () => leaveCurrentRoom(socket));
  socket.on('disconnect', () => leaveCurrentRoom(socket));
});

server.listen(PORT, () => console.log(`TRIBU Online server listening on ${PORT}`));
