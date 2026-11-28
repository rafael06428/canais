// Cartoon engine for "You Were There POV": every frame is a pure function of time.
// Scenes come from episode.json ("v" object per scene), timings from voice.json.
// Exposes window.seek(t) for the long video, window.seekShort(k, t) for Shorts, window.thumb().
(() => {
const E = window.EP, V = window.VOICE;
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const ease = x => { x = clamp(x); return x < .5 ? 2 * x * x : 1 - Math.pow(-2 * x + 2, 2) / 2; };
const back = x => { x = clamp(x); const c = 1.9; return 1 + (c + 1) * Math.pow(x - 1, 3) + c * Math.pow(x - 1, 2); };
const rnd = i => { const x = Math.sin(i * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };
const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;');
const INDOOR = ['below', 'cellar', 'room', 'desk', 'church', 'plain', 'black', 'underwater'];
const K = '#1a1a1a';
let SHORT = null;   // set while drawing a vertical Short: {x0}      // outline colour
const SW = 4;             // outline width

// ---------- palette by time of day ----------
const SKY = { day: ['#bfe3f2', '#e8f4f8'], dusk: ['#e9a77a', '#f6d5a8'], night: ['#1c2a44', '#2d3e5e'], storm: ['#5d6b78', '#8a96a0'], stormnight: ['#141c2b', '#26324a'], dawn: ['#c9b6c9', '#f1d3b5'], grey: ['#9aa3a8', '#c4c9cb'] };
const SEA = { day: '#3a8fbf', dusk: '#4d7fa0', night: '#1b3352', storm: '#40606f', stormnight: '#14263a', dawn: '#5a7f95', grey: '#59707c' };
function skyKey(v) { const tm = v.time || 'day'; if ((v.storm || 0) >= 2) return tm === 'night' ? 'stormnight' : 'storm'; return tm; }

const DEFS = `<defs>
 <filter id="bl"><feGaussianBlur stdDeviation="3.5"/></filter>
 <radialGradient id="glow"><stop offset="0" stop-color="#ffd27a"/><stop offset="1" stop-color="#ff8a2a" stop-opacity="0"/></radialGradient>
 <radialGradient id="lamp"><stop offset="0" stop-color="#fff3c0" stop-opacity=".9"/><stop offset="1" stop-color="#ffcf6a" stop-opacity="0"/></radialGradient>
 <radialGradient id="vig" cx=".5" cy=".5" r=".75"><stop offset=".55" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".5"/></radialGradient>
 <linearGradient id="uw" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2a7fa8"/><stop offset="1" stop-color="#0b2f48"/></linearGradient>
</defs>`;

// ---------- people ----------
const ROLES = {
  you:      { coat: '#2f5d8c', cap: 'knit', capc: '#b8322a', hair: '#4a2f1c', scarf: '#b8322a' },
  sailor:   { coat: '#ece6d6', stripes: 1, cap: 'knit', capc: '#3b4a5a', beard: 1 },
  sailor2:  { coat: '#6b5a48', cap: 'none', hair: '#2b2018', beard: 1 },
  officer:  { coat: '#22385c', hat: 'tricorn', wig: '#e9e4da', long: 1, cuffs: '#d9b44a' },
  admiral:  { coat: '#1d2f4f', hat: 'tricorn', wig: '#f1eee8', long: 1, cuffs: '#e2bd4e', sash: '#b8322a' },
  townsman: { coat: '#6e4b2e', hat: 'tricorn', hair: '#3a2a1c', long: 1 },
  boatman:  { coat: '#5a4a3a', cap: 'knit', capc: '#556b2f', beard: 1 },
  woman:    { dress: '#7a3b4a', bonnet: '#f3efe6' },
  maid:     { dress: '#5d6e86', bonnet: '#f3efe6' },
  queen:    { dress: '#5b2a6e', crown: 1, hair: '#6b4a2a' },
  defoe:    { coat: '#5a3d2a', wig: '#4a3626', long: 1, cuffs: '#e8e0cc' },
  winstanley:{ coat: '#3d4f3a', wig: '#d8d0c0', long: 1, hat: 'tricorn' },
  bishop:   { coat: '#1e1e22', wig: '#efece6', long: 1, bands: 1 },
  wife:     { dress: '#3a3a52', bonnet: '#f3efe6' },
  diver:    { diver: 1 },
  modern:   { coat: '#3c6e5a', hair: '#3a2a1c' },
};
const FACES = {
  calm:  (b) => b ? `<path d="M-19 -4 L-7 -4 M7 -4 L19 -4" stroke="${K}" stroke-width="4" stroke-linecap="round"/>` : `<ellipse cx="-13" cy="-4" rx="4" ry="6"/><ellipse cx="13" cy="-4" rx="4" ry="6"/>`,
  worry: (b) => (b ? `<path d="M-19 -2 L-7 -2 M7 -2 L19 -2" stroke="${K}" stroke-width="4"/>` : `<ellipse cx="-13" cy="-2" rx="4" ry="6"/><ellipse cx="13" cy="-2" rx="4" ry="6"/>`) + `<path d="M-23 -17 L-6 -12 M23 -17 L6 -12" stroke="${K}" stroke-width="4" fill="none" stroke-linecap="round"/>`,
  shock: () => `<circle cx="-13" cy="-4" r="9" fill="#fff" stroke="${K}" stroke-width="3"/><circle cx="13" cy="-4" r="9" fill="#fff" stroke="${K}" stroke-width="3"/><circle cx="-13" cy="-4" r="3.5"/><circle cx="13" cy="-4" r="3.5"/>`,
  stern: () => `<rect x="-19" y="-6" width="12" height="5" rx="2"/><rect x="7" y="-6" width="12" height="5" rx="2"/><path d="M-23 -16 L-6 -10 M23 -16 L6 -10" stroke="${K}" stroke-width="4" fill="none" stroke-linecap="round"/>`,
  sad:   (b) => (b ? `<path d="M-19 -2 L-7 -2 M7 -2 L19 -2" stroke="${K}" stroke-width="4"/>` : `<ellipse cx="-13" cy="-1" rx="4" ry="5"/><ellipse cx="13" cy="-1" rx="4" ry="5"/>`) + `<path d="M-22 -10 L-6 -15 M22 -10 L6 -15" stroke="${K}" stroke-width="4" fill="none" stroke-linecap="round"/>`,
  happy: () => `<path d="M-19 -2 Q-13 -10 -7 -2 M7 -2 Q13 -10 19 -2" stroke="${K}" stroke-width="4" fill="none" stroke-linecap="round"/>`,
  sleep: () => `<path d="M-19 -2 Q-13 3 -7 -2 M7 -2 Q13 3 19 -2" stroke="${K}" stroke-width="4" fill="none" stroke-linecap="round"/>`,
  look:  (b) => b ? FACES.calm(1) : `<ellipse cx="-6" cy="-7" rx="4" ry="6"/><ellipse cx="20" cy="-7" rx="4" ry="6"/>`,
};
const MOUTH = { calm: `<path d="M-8 18 Q0 24 8 18" stroke="${K}" stroke-width="3.5" fill="none" stroke-linecap="round"/>`, worry: `<path d="M-8 21 Q0 16 8 21" stroke="${K}" stroke-width="3.5" fill="none" stroke-linecap="round"/>`,
  shock: `<ellipse cx="0" cy="20" rx="7" ry="9"/>`, stern: `<path d="M-9 20 L9 20" stroke="${K}" stroke-width="4" stroke-linecap="round"/>`, sad: `<path d="M-9 23 Q0 15 9 23" stroke="${K}" stroke-width="3.5" fill="none" stroke-linecap="round"/>`,
  happy: `<path d="M-11 15 Q0 29 11 15 Z" fill="${K}"/>`, sleep: `<path d="M-6 19 L6 19" stroke="${K}" stroke-width="3"/>`, look: `<path d="M-6 18 Q0 22 6 18" stroke="${K}" stroke-width="3.5" fill="none"/>` };

function person(it, t, lt, wind) {
  const R = Object.assign({}, ROLES[it.role || 'sailor'] || ROLES.sailor, it.look || {});
  const s = it.s || 1, seed = it.seed ?? (it.x || 0) * .01;
  let x = it.x || 640, y = it.y || 560;
  if (it.enter) { const d = it.enterDur || 1.2, k = ease(lt / d); x += (it.enter === 'left' ? -1 : 1) * (1 - k) * 700; }
  if (it.dx) x += it.dx * ease(lt / (it.dxDur || 4));
  const walking = it.pose === 'walk' || it.pose === 'run' || (it.enter && lt < (it.enterDur || 1.2));
  const sp = it.pose === 'run' ? 13 : 8;
  const blink = ((t + seed * 7) % 3.4) < .12;
  const face = it.face || 'calm';
  const lean = (it.lean || 0) + wind * 4 * (it.flip ? -1 : 1) * (it.pose === 'sleep' ? 0 : 1) + (it.pose === 'cling' ? Math.sin(t * 3 + seed) * 4 : 0);
  const shiver = it.shiver ? Math.sin(t * 40) * 1.5 : 0;
  const bob = Math.sin((t + seed) * 2.4) * 1.6 + (walking ? -Math.abs(Math.sin(t * sp)) * 5 : 0);
  // limbs
  const P = it.pose || 'idle';
  const sw = Math.sin(t * sp) * 12;
  let legs = '', arms = '', extra = '';
  const L = (d) => `<path d="${d}" stroke="${K}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round" fill="none"/>`;
  if (P === 'sit' || P === 'write' || P === 'row') legs = L(`M-14 160 L-10 200 L-30 220 M14 160 L18 200 L0 220`);
  else if (P === 'kneel') legs = L(`M-14 160 L-40 192 L-12 206 M14 160 L28 214`);
  else if (P === 'sleep') legs = '';
  else legs = walking ? L(`M-14 160 L${-16 + sw} 220 M14 160 L${16 - sw} 220`) : L(`M-14 160 L-18 220 M14 160 L18 220`);
  const wv = Math.sin(t * 7 + seed) * 12;
  if (P === 'point') arms = L(`M-28 72 L-46 132 M28 72 L96 ${40 + Math.sin(t * 2) * 3}`);
  else if (P === 'armsup' || P === 'cheer') arms = L(`M-28 72 L${-64 + (P === 'cheer' ? wv : 0)} 14 M28 72 L${64 - (P === 'cheer' ? wv : 0)} 14`);
  else if (P === 'cling') arms = L(`M-28 72 L-34 -40 M28 72 L34 -40`);
  else if (P === 'wave') arms = L(`M-28 72 L-46 132 M28 72 L${70 + wv} 6`);
  else if (P === 'write') arms = L(`M-28 72 L-30 128 M28 72 L${66 + Math.sin(t * 9) * 8} ${126 + Math.cos(t * 13) * 3}`);
  else if (P === 'pray') arms = L(`M-28 72 L-6 112 L0 76 M28 72 L6 112 L0 76`);
  else if (P === 'hold') { arms = L(`M-28 72 L-46 132 M28 72 L70 104`); extra = lantern(70, 104, t, 1); }
  else if (P === 'row') arms = L(`M-28 72 L${40 + Math.sin(t * 3) * 25} 110 M28 72 L${60 + Math.sin(t * 3) * 25} 112`) + `<path d="M${10 + Math.sin(t * 3) * 25} 100 L${140 + Math.sin(t * 3) * 30} 190" stroke="#7a4e2d" stroke-width="8" stroke-linecap="round"/>`;
  else if (P === 'cover') arms = L(`M-28 72 L-40 0 L-6 -40 M28 72 L40 0 L6 -40`);
  else if (P === 'sleep') arms = '';
  else arms = L(walking ? `M-28 72 L${-44 - sw} 130 M28 72 L${44 + sw} 130` : `M-28 72 L-46 132 M28 72 L46 132`);
  // body
  let body;
  if (R.diver) body = `<path d="M-32 56 L32 56 L38 165 L-38 165 Z" fill="#1d1d24" stroke="${K}" stroke-width="${SW}"/><rect x="26" y="62" width="24" height="70" rx="10" fill="#e0b021" stroke="${K}" stroke-width="3"/>`;
  else if (R.dress) body = `<path d="M-28 56 L28 56 L58 172 L-58 172 Z" fill="${R.dress}" stroke="${K}" stroke-width="${SW}" stroke-linejoin="round"/><path d="M-18 56 L0 84 L18 56" fill="#f3efe6" stroke="${K}" stroke-width="3"/>`;
  else {
    const bot = R.long ? 180 : 165;
    body = `<path d="M-30 56 L30 56 L40 ${bot} L-40 ${bot} Z" fill="${R.coat}" stroke="${K}" stroke-width="${SW}" stroke-linejoin="round"/>`;
    if (R.stripes) body += [80, 104, 128, 152].map(yy => `<path d="M${-34 - (yy - 56) * .08} ${yy} L${34 + (yy - 56) * .08} ${yy}" stroke="#3b5a8a" stroke-width="7"/>`).join('');
    if (R.long) body += `<path d="M0 60 L0 ${bot}" stroke="${K}" stroke-width="2.5"/>` + [80, 100, 120, 140].map(yy => `<circle cx="7" cy="${yy}" r="3" fill="${R.cuffs || '#c9a54a'}"/>`).join('');
    if (R.scarf) body += `<path d="M-24 58 Q0 74 24 58 L20 66 Q0 82 -20 66 Z" fill="${R.scarf}" stroke="${K}" stroke-width="3"/>`;
    if (R.sash) body += `<path d="M-30 60 L36 150" stroke="${R.sash}" stroke-width="10"/>`;
    if (R.bands) body += `<path d="M-6 58 L-8 82 L0 80 L8 82 L6 58Z" fill="#fff" stroke="${K}" stroke-width="2.5"/>`;
  }
  // head
  let back = '', front = '';
  if (R.wig) back += [[-40, 10], [40, 10], [-42, 36], [42, 36], [-36, -20], [36, -20]].map(([a, b]) => `<circle cx="${a}" cy="${b}" r="17" fill="${R.wig}" stroke="${K}" stroke-width="3"/>`).join('');
  if (R.hair && !R.cap && !R.hat && !R.crown && !R.wig) front += `<path d="M-41 -12 Q-38 -48 0 -47 Q38 -48 41 -12 Q22 -30 0 -28 Q-22 -30 -41 -12Z" fill="${R.hair}" stroke="${K}" stroke-width="3"/>`;
  if (R.hair && R.crown) back += `<path d="M-46 -6 Q-50 50 -30 60 L30 60 Q50 50 46 -6 Z" fill="${R.hair}" stroke="${K}" stroke-width="3"/>`;
  if (R.cap === 'knit') front += `<path d="M-42 -14 Q-40 -58 0 -58 Q40 -58 42 -14 Z" fill="${R.capc}" stroke="${K}" stroke-width="3.5"/><rect x="-44" y="-20" width="88" height="12" rx="5" fill="${R.capc}" stroke="${K}" stroke-width="3"/>`;
  if (R.hat === 'tricorn') front += `<path d="M-62 -18 Q0 -36 62 -18 L42 -46 Q0 -74 -42 -46 Z" fill="#1f1f24" stroke="${K}" stroke-width="3.5"/><path d="M-60 -20 Q0 -36 60 -20" stroke="#d9b44a" stroke-width="3" fill="none"/>`;
  if (R.bonnet) front += `<path d="M-48 8 Q-52 -52 0 -54 Q52 -52 48 8 Q40 -30 0 -32 Q-40 -30 -48 8Z" fill="${R.bonnet}" stroke="${K}" stroke-width="3.5"/>`;
  if (R.crown) front += `<path d="M-30 -36 L-30 -64 L-15 -48 L0 -70 L15 -48 L30 -64 L30 -36 Z" fill="#e8c14a" stroke="${K}" stroke-width="3.5"/>`;
  if (R.diver) front += `<rect x="-36" y="-26" width="72" height="34" rx="12" fill="#bfe8ff" fill-opacity=".55" stroke="${K}" stroke-width="4"/><path d="M36 -4 Q60 0 54 40" stroke="${K}" stroke-width="5" fill="none"/>`;
  let beard = R.beard ? `<path d="M-36 4 Q-30 46 0 52 Q30 46 36 4 Q20 24 0 26 Q-20 24 -36 4Z" fill="${R.hair || '#5a4030'}" stroke="${K}" stroke-width="3"/>` : '';
  const eyes = (FACES[face] || FACES.calm)(blink && face !== 'shock');
  const mouth = R.beard && face === 'calm' ? '' : (MOUTH[face] || MOUTH.calm);
  const head = `<g transform="translate(0,${bob})">${back}<circle r="44" fill="#fff" stroke="${K}" stroke-width="4.5"/>${beard}<g fill="${K}">${eyes}</g>${mouth}${front}</g>`;
  const sy = (it.flip ? -1 : 1);
  if (P === 'sleep') {   // lying in bed: only the head on a pillow, body under the blanket (drawn by the bed)
    return `<g transform="translate(${x},${y}) scale(${s})"><g transform="rotate(-80)">${head}</g></g>`;
  }
  const op = it.op != null ? it.op : 1;
  return `<g opacity="${op}" transform="translate(${x + shiver},${y}) rotate(${lean}) scale(${sy * s},${s}) translate(0,-220)">${legs}<g transform="translate(0,${bob * .3})">${body}${arms}${extra}</g>${head}</g>`;
}

// ---------- props ----------
function lantern(x, y, t, s = 1) {
  const f = .85 + Math.sin(t * 17) * .08 + Math.sin(t * 7) * .07;
  return `<g transform="translate(${x},${y}) scale(${s})"><circle r="${60 * f}" fill="url(#lamp)"/><path d="M0 -24 L0 -14" stroke="${K}" stroke-width="3"/><rect x="-11" y="-14" width="22" height="28" rx="4" fill="#ffe08a" stroke="${K}" stroke-width="3"/><path d="M-13 -14 L13 -14 L8 -20 L-8 -20Z" fill="#333"/></g>`;
}
function candle(x, y, t, s = 1) {
  const f = Math.sin(t * 19) * 2;
  return `<g transform="translate(${x},${y}) scale(${s})"><circle cy="-40" r="70" fill="url(#lamp)" opacity=".8"/><rect x="-8" y="-30" width="16" height="40" fill="#f3ecd8" stroke="${K}" stroke-width="3"/><path d="M0 -32 Q${-7 + f} -46 0 ${-58 + f} Q${7 + f} -46 0 -32Z" fill="#ffb02e" stroke="#e07a10" stroke-width="2"/><rect x="-18" y="8" width="36" height="8" rx="3" fill="#b08a4a" stroke="${K}" stroke-width="3"/></g>`;
}
function ship(it, t, lt, storm) {
  const s = it.s || 1, roll = storm * 2.2 * Math.sin(t * 1.3 + (it.x || 0)) + (it.tilt || 0) * ease(lt / (it.tiltDur || .01)), heave = storm * 6 * Math.sin(t * 1.7 + (it.x || 0) * .1);
  const sink = (it.sink || 0) * ease((lt - (it.sinkAt || 0)) / (it.sinkDur || 3));
  const x = (it.x || 640) + (it.dx || 0) * ease(lt / (it.dxDur || 6)), y = (it.y || 470) + heave + sink * 200;
  const flip = it.flip ? -1 : 1, broken = it.broken || 0, sails = it.sails || 'furled', lights = it.lights;
  const hull = `<path d="M-210 -10 L-190 60 Q0 90 190 60 L230 -30 L170 -24 L170 -60 L240 -66 L236 -30 Z" fill="#6b3f22" stroke="${K}" stroke-width="${SW}" stroke-linejoin="round"/>
   <path d="M-206 6 Q0 30 214 -2" stroke="#d9b44a" stroke-width="6" fill="none"/><path d="M-200 30 Q0 58 206 24" stroke="#2b1a10" stroke-width="12" fill="none"/>
   ${[-150, -100, -50, 0, 50, 100, 150].map(gx => `<rect x="${gx - 9}" y="${34 + Math.abs(gx) * .02}" width="18" height="14" fill="${lights ? '#ffd27a' : '#1a1a1a'}" stroke="${K}" stroke-width="2"/>`).join('')}
   <path d="M-210 -10 L-260 -40" stroke="${K}" stroke-width="7"/>`;
  const mast = (mx, h, i) => {
    if (i < broken) return `<path d="M${mx} -10 L${mx + 6} ${-h * .35} L${mx - 8} ${-h * .3}" stroke="#4a3020" stroke-width="10" fill="none" stroke-linejoin="bevel"/>`;
    const sw = Math.sin(t * 2 + i) * storm;
    let sl = '';
    if (sails === 'set') sl = [0.3, 0.6].map(f => `<path d="M${mx - 52} ${-h * f - 40} L${mx + 52} ${-h * f - 40} Q${mx + 62 + sw * 3} ${-h * f} ${mx + 52} ${-h * f + 20} L${mx - 52} ${-h * f + 20} Q${mx - 42 + sw * 3} ${-h * f} ${mx - 52} ${-h * f - 40}Z" fill="#f1e6cf" stroke="${K}" stroke-width="3"/>`).join('');
    else sl = [0.35, 0.65, 0.9].map(f => `<path d="M${mx - 48 + f * 10} ${-h * f} L${mx + 48 - f * 10} ${-h * f}" stroke="#4a3020" stroke-width="6"/><path d="M${mx - 40 + f * 10} ${-h * f + 4} Q${mx} ${-h * f + 14} ${mx + 40 - f * 10} ${-h * f + 4}" stroke="#e6dcc4" stroke-width="7" fill="none"/>`).join('');
    return `<path d="M${mx} -10 L${mx} ${-h}" stroke="#4a3020" stroke-width="9"/>${sl}<path d="M${mx} ${-h} L${mx + 26 + sw * 4} ${-h - 6} L${mx} ${-h - 12}" fill="#b8322a" stroke="${K}" stroke-width="2"/>
      <path d="M${mx} ${-h} L-205 -14 M${mx} ${-h} L200 -40" stroke="#3a2a1a" stroke-width="1.6" opacity=".6"/>`;
  };
  const masts = mast(-110, 230, 0) + mast(10, 280, 1) + mast(120, 220, 2);
  const lamp = lights ? lantern(200, -80, t, .9) : '';
  return `<g transform="translate(${x},${y}) rotate(${roll * flip}) scale(${flip * s},${s})">${masts}${hull}${lamp}</g>`;
}
function boat(it, t, lt, storm) {
  const s = it.s || 1, x = (it.x || 640) + (it.dx || 0) * ease(lt / (it.dxDur || 6)), y = (it.y || 560) + Math.sin(t * 2 + (it.x || 0)) * (4 + storm * 4);
  const r = Math.sin(t * 1.6 + (it.x || 0)) * (3 + storm * 3);
  return `<g transform="translate(${x},${y}) rotate(${r}) scale(${(it.flip ? -1 : 1) * s},${s})"><path d="M-110 -10 Q0 40 110 -10 L96 22 Q0 62 -96 22Z" fill="#7a4e2d" stroke="${K}" stroke-width="${SW}"/><path d="M-100 -4 Q0 40 100 -4" stroke="#c9a06a" stroke-width="4" fill="none"/></g>`;
}
function chimneyRow(it, t, lt, storm) {   // rooftops with chimneys; some fall at given scene times
  const y = it.y || 420, n = it.n || 5, w = 1400 / n;
  let out = '';
  for (let i = 0; i < n; i++) {
    const x0 = -60 + i * w, h = 140 + (i % 3) * 40, c = ['#9a5a3e', '#8a4e36', '#a56446'][i % 3];
    out += `<path d="M${x0} ${y + 300} L${x0} ${y - h + 60} L${x0 + w / 2} ${y - h} L${x0 + w} ${y - h + 60} L${x0 + w} ${y + 300}Z" fill="${c}" stroke="${K}" stroke-width="${SW}"/>`;
    out += `<path d="M${x0} ${y - h + 60} L${x0 + w / 2} ${y - h} L${x0 + w} ${y - h + 60}" stroke="#3b3b45" stroke-width="16" fill="none"/>`;
    for (let k = 0; k < 2; k++) out += `<rect x="${x0 + 30 + k * (w / 2)}" y="${y - h + 110}" width="40" height="50" fill="${it.lit ? '#ffd27a' : '#2b3040'}" stroke="${K}" stroke-width="3"/>`;
    const fallAt = (it.fall || [])[i];
    const cx = x0 + w * .7, cy = y - h + 30;
    let ang = Math.sin(t * 6 + i) * storm * .8, dy = 0;
    if (fallAt != null && lt > fallAt) { const k = clamp((lt - fallAt) / .8); ang = 70 * k * k; dy = 260 * k * k; }
    out += `<g transform="translate(${cx},${cy + dy}) rotate(${ang})"><rect x="-22" y="-80" width="44" height="80" fill="#7a3a2a" stroke="${K}" stroke-width="3.5"/><rect x="-28" y="-92" width="56" height="14" fill="#5a2a1e" stroke="${K}" stroke-width="3"/>
      ${[-60, -40, -20].map(yy => `<path d="M-22 ${yy} L22 ${yy}" stroke="#5a2a1e" stroke-width="2"/>`).join('')}</g>`;
    if (fallAt != null && lt > fallAt) for (let b = 0; b < 8; b++) { const k = clamp((lt - fallAt - .1) / 1.2); out += `<rect x="${cx + (rnd(b + i * 9) - .5) * 160 * k}" y="${cy + 40 + 300 * k * k - rnd(b) * 40}" width="16" height="9" fill="#8a4436" stroke="${K}" stroke-width="2" transform="rotate(${rnd(b) * 360 * k} ${cx} ${cy})"/>`; }
  }
  return out;
}
function tree(it, t, lt, storm) {
  const x = it.x || 640, y = it.y || 560, s = it.s || 1;
  let ang = (storm * 6 + Math.sin(t * 3 + x) * storm * 4) * (it.flip ? -1 : 1);
  if (it.fallAt != null && lt > it.fallAt) ang = Math.max(ang, 88 * ease((lt - it.fallAt) / 1.3));
  return `<g transform="translate(${x},${y}) scale(${s}) rotate(${ang})"><path d="M-12 0 L-8 -150 L8 -150 L12 0Z" fill="#6b4226" stroke="${K}" stroke-width="${SW}"/>
   <circle cy="-200" r="72" fill="#4f7a3a" stroke="${K}" stroke-width="${SW}"/><circle cx="-50" cy="-160" r="44" fill="#5a8a42" stroke="${K}" stroke-width="${SW}"/><circle cx="52" cy="-164" r="46" fill="#5a8a42" stroke="${K}" stroke-width="${SW}"/></g>`;
}
function windmill(it, t, lt, storm) {
  const x = it.x || 640, y = it.y || 560, s = it.s || 1, sp = it.speed || (1 + storm * 3), a = (t * sp * 60) % 360;
  const fire = it.fireAt != null && lt > it.fireAt ? clamp((lt - it.fireAt) / 1.5) : 0;
  const flames = fire ? [0, 1, 2, 3, 4].map(i => { const k = (t * 1.4 + i / 5) % 1; return `<path d="M${-30 + i * 15} ${-150 - k * 90} q12 -26 0 -50 q-12 24 0 50" fill="${i % 2 ? '#ff8a2a' : '#ffd24a'}" opacity="${fire * (1 - k)}"/>`; }).join('') : '';
  return `<g transform="translate(${x},${y}) scale(${s})"><circle cy="-170" r="${130 * fire}" fill="url(#glow)" opacity="${fire}"/><path d="M-50 0 L-34 -170 L34 -170 L50 0Z" fill="#e3d2ad" stroke="${K}" stroke-width="${SW}"/><path d="M-40 -170 L0 -214 L40 -170Z" fill="#7a4a2a" stroke="${K}" stroke-width="${SW}"/>
   <rect x="-12" y="-50" width="24" height="50" fill="#5a4030" stroke="${K}" stroke-width="3"/>
   <g transform="translate(0,-170) rotate(${a})">${[0, 90, 180, 270].map(r => `<g transform="rotate(${r})"><rect x="-8" y="-150" width="16" height="150" fill="#6b4226" stroke="${K}" stroke-width="3"/><rect x="8" y="-146" width="34" height="110" fill="#f1e6cf" stroke="${K}" stroke-width="3"/></g>`).join('')}<circle r="10" fill="#333"/></g>${flames}</g>`;
}
function lighthouse(it, t, lt, storm) {
  const x = it.x || 640, y = it.y || 520, s = it.s || 1;
  const gone = it.goneAt != null && lt > it.goneAt ? clamp((lt - it.goneAt) / 1.2) : 0;
  const beam = (Math.sin(t * 1.2) + 1) / 2;
  const tower = `<g opacity="${1 - gone}" transform="translate(0,${gone * 40}) rotate(${gone * 8})">
    <path d="M-46 0 L-36 -220 L36 -220 L46 0Z" fill="#e9e1cf" stroke="${K}" stroke-width="${SW}"/>
    ${[-60, -120, -180].map(yy => `<path d="M-44 ${yy} L44 ${yy}" stroke="#8a7a62" stroke-width="3"/>`).join('')}
    <rect x="-56" y="-236" width="112" height="16" fill="#6b4226" stroke="${K}" stroke-width="3"/>
    <rect x="-30" y="-300" width="60" height="64" fill="#fff1b0" stroke="${K}" stroke-width="${SW}"/>
    <path d="M-40 -300 L0 -350 L40 -300Z" fill="#5a3a2a" stroke="${K}" stroke-width="${SW}"/>
    <path d="M-60 -236 Q-90 -260 -70 -290 M60 -236 Q90 -260 70 -290" stroke="${K}" stroke-width="4" fill="none"/>
    <circle cy="-268" r="${90 + beam * 30}" fill="url(#lamp)"/></g>`;
  return `<g transform="translate(${x},${y}) scale(${s})">${tower}<path d="M-150 30 Q-100 -20 -40 -4 Q20 -20 90 -6 Q140 0 170 34Z" fill="#4a4a50" stroke="${K}" stroke-width="${SW}"/></g>`;
}
function bed(it, t, lt) {
  const x = it.x || 640, y = it.y || 560, s = it.s || 1, w = it.w || 1;
  return `<g transform="translate(${x},${y}) scale(${s})"><rect x="${-200 * w}" y="-150" width="22" height="150" fill="#6b4226" stroke="${K}" stroke-width="${SW}"/><rect x="${178 * w}" y="-90" width="22" height="90" fill="#6b4226" stroke="${K}" stroke-width="${SW}"/>
   <rect x="${-190 * w}" y="-70" width="${380 * w}" height="34" fill="#8a5a34" stroke="${K}" stroke-width="${SW}"/>
   <rect x="${-176 * w}" y="-112" width="80" height="40" rx="14" fill="#fff" stroke="${K}" stroke-width="3"/>
   <path d="M${-110 * w} -100 Q0 ${-126 + Math.sin(t * 1.5) * 3} ${180 * w} -96 L${180 * w} -66 L${-110 * w} -66Z" fill="${it.blanket || '#7d8fb8'}" stroke="${K}" stroke-width="${SW}"/></g>`;
}
function paper(it, t, lt) {   // newspaper / book page with a headline
  const x = it.x || 640, y = it.y || 360, s = (it.s || 1) * back((lt - (it.at || 0)) / .5), r = it.rot || -3;
  if (s <= 0) return '';
  const lines = Array.from({ length: 9 }, (_, i) => `<rect x="-150" y="${-40 + i * 22}" width="${240 + rnd(i) * 60}" height="8" fill="#9a907c"/>`).join('');
  return `<g transform="translate(${x},${y}) rotate(${r}) scale(${s})"><rect x="-180" y="-150" width="360" height="330" fill="#f3ead2" stroke="${K}" stroke-width="${SW}"/>
   <text y="-100" text-anchor="middle" font-size="${it.fs || 34}" font-weight="bold" fill="#2a2018">${esc(it.title || '')}</text>
   <text y="-66" text-anchor="middle" font-size="18" fill="#2a2018">${esc(it.sub || '')}</text>${lines}</g>`;
}
function bigText(it, t, lt) {
  let sc = back((lt - (it.at || 0)) / .45);
  if (sc <= 0) return '';
  let x = it.x || 640;
  if (SHORT) { x = SHORT.x0 + 202; sc *= Math.min(1, 380 / (String(it.text).length * (it.fs || 96) * .72)); }
  return `<g transform="translate(${x},${it.y || 330}) scale(${sc})"><text text-anchor="middle" font-size="${it.fs || 96}" font-weight="bold" fill="${it.c || '#ffd21f'}" stroke="${K}" stroke-width="9" paint-order="stroke" stroke-linejoin="round" letter-spacing="3">${esc(it.text)}</text>
   ${it.sub ? `<text y="${(it.fs || 96) * .62}" text-anchor="middle" font-size="${(it.fs || 96) * .34}" font-weight="bold" fill="#fff" stroke="${K}" stroke-width="6" paint-order="stroke">${esc(it.sub)}</text>` : ''}</g>`;
}
function counter(it, t, lt) {   // animated number
  const k = ease((lt - (it.at || 0)) / (it.dur || 2));
  if (lt < (it.at || 0)) return '';
  const v = Math.round((it.from || 0) + ((it.to || 0) - (it.from || 0)) * k).toLocaleString('en-US');
  return bigText({ ...it, text: (it.pre || '') + v + (it.post || ''), at: it.at || 0 }, t, lt);
}
function gauge(it, t, lt) {    // barometer with a falling needle
  const x = it.x || 640, y = it.y || 330, s = it.s || 1, k = ease((lt - (it.at || 0)) / (it.dur || 4));
  const a = -60 + 120 * (it.from ?? .8) + 120 * ((it.to ?? .1) - (it.from ?? .8)) * k - 60;
  return `<g transform="translate(${x},${y}) scale(${s})"><circle r="120" fill="#c9a86a" stroke="${K}" stroke-width="${SW}"/><circle r="100" fill="#f3ead2" stroke="${K}" stroke-width="3"/>
   ${Array.from({ length: 13 }, (_, i) => { const r = (-150 + i * 10) * Math.PI / 180 * 1.0; return ''; }).join('')}
   <text x="-62" y="44" font-size="18" font-weight="bold" fill="#8a2a1a">STORMY</text><text x="22" y="44" font-size="18" font-weight="bold" fill="#2a5a2a">FAIR</text>
   <g transform="rotate(${a})"><path d="M0 0 L0 -82" stroke="${K}" stroke-width="6" stroke-linecap="round"/><path d="M-8 -70 L0 -90 L8 -70Z" fill="${K}"/></g><circle r="10" fill="${K}"/></g>`;
}
function rope(it, t, lt) {   // anchor cable that snaps at a given time
  const x1 = it.x1, y1 = it.y1, x2 = it.x2, y2 = it.y2, snap = it.snapAt;
  if (snap == null || lt < snap) { const tw = Math.sin(t * 20) * (lt > snap - 1.5 ? 3 : .5); return `<path d="M${x1} ${y1} Q${(x1 + x2) / 2 + tw} ${(y1 + y2) / 2 + 10} ${x2} ${y2}" stroke="#7a5a3a" stroke-width="8" fill="none"/>`; }
  const k = ease((lt - snap) / .6);
  const mx = (x1 + x2) / 2, my = (y1 + y2) / 2;
  return `<path d="M${x1} ${y1} Q${x1 + (mx - x1) * .5} ${y1 + 60 * k} ${mx - 20} ${my + 120 * k}" stroke="#7a5a3a" stroke-width="8" fill="none"/>
    <path d="M${x2} ${y2} Q${x2 - (x2 - mx) * .5} ${y2 + 40 * k} ${mx + 20} ${my + 140 * k}" stroke="#7a5a3a" stroke-width="8" fill="none"/>
    ${k < 1 ? `<g transform="translate(${mx},${my}) scale(${1 + k})" opacity="${1 - k}"><path d="M-30 0 L-10 -8 L-24 -30 L0 -12 L10 -36 L14 -10 L36 -20 L18 2 L34 22 L8 10 Z" fill="#ffd21f" stroke="${K}" stroke-width="3"/></g>` : ''}`;
}
function cannon(it) { const x = it.x || 640, y = it.y || 600, s = it.s || 1, r = it.rot || 0; return `<g transform="translate(${x},${y}) rotate(${r}) scale(${s})"><rect x="-90" y="-22" width="180" height="40" rx="18" fill="#3a3f3a" stroke="${K}" stroke-width="${SW}"/><circle cx="-90" cy="-2" r="16" fill="#3a3f3a" stroke="${K}" stroke-width="${SW}"/><path d="M90 -22 L100 -26 L100 22 L90 18" fill="#2a2f2a" stroke="${K}" stroke-width="3"/></g>`; }
function bubbleSvg(x, y, text, sc, tail) {
  if (sc <= 0) return '';
  const w = Math.max(text.length * 20 + 48, 110);
  if (SHORT) { x = Math.max(SHORT.x0 + 8 + w * .5 * Math.min(1, 385 / w), Math.min(SHORT.x0 + 397 - w * .5 * Math.min(1, 385 / w), x)); sc *= Math.min(1, 385 / w); }
  const tx = tail === 'right' ? w / 2 - 54 : tail === 'center' ? -14 : -w / 2 + 30;
  return `<g transform="translate(${x},${y}) scale(${sc})"><rect x="${-w / 2}" y="-30" width="${w}" height="60" rx="18" fill="#fff" stroke="${K}" stroke-width="4"/>
   <path d="M${tx} 28 l12 24 l16 -24" fill="#fff" stroke="${K}" stroke-width="4" stroke-linejoin="round"/><rect x="${tx - 2}" y="22" width="34" height="8" fill="#fff"/>
   <text x="0" y="11" text-anchor="middle" font-weight="bold" font-size="30" fill="${K}">${esc(text)}</text></g>`;
}

// ---------- backgrounds ----------
function waves(t, y0, storm, col, n = 8) {
  const amp = 4 + storm * 9;
  let out = '';
  for (let r = 0; r < 3; r++) {
    const yy = y0 + r * 50 + Math.sin(t + r) * storm * 3;
    let d = `M-20 ${yy}`;
    for (let x = -20; x <= 1300; x += 40) d += ` Q${x + 20} ${yy - amp * (1 + r * .4) * Math.sin(t * (1.4 + storm * .3) + x * .02 + r)} ${x + 40} ${yy}`;
    out += `<path d="${d}" stroke="${col}" stroke-width="${3 + r}" fill="none" opacity="${.55 - r * .1}"/>`;
  }
  return out;
}
function bigSwell(t, storm, y0, col) {
  if (storm < 2) return '';
  let d = `M-20 720 L-20 ${y0}`;
  for (let x = -20; x <= 1300; x += 20) d += ` L${x} ${y0 - (18 + storm * 10) * Math.sin(t * 1.3 + x * .009) - 10 * Math.sin(t * 2.1 + x * .023)}`;
  return `<path d="${d} L1300 720Z" fill="${col}" stroke="${K}" stroke-width="3" opacity=".95"/>` +
    Array.from({ length: 10 }, (_, i) => { const x = (i * 140 + t * 60) % 1400 - 60; const yy = y0 - (18 + storm * 10) * Math.sin(t * 1.3 + x * .009) - 10 * Math.sin(t * 2.1 + x * .023); return `<path d="M${x - 30} ${yy + 4} q15 -14 30 -4 q15 10 30 -2" stroke="#fff" stroke-width="5" fill="none" opacity=".8"/>`; }).join('');
}
function clouds(t, storm, key) {
  const c = storm >= 2 ? '#3d4652' : key === 'night' ? '#3a4a68' : '#ffffff';
  const op = storm >= 2 ? .9 : .75;
  return Array.from({ length: 6 }, (_, i) => { const x = ((i * 260 + t * (8 + storm * 30)) % 1600) - 200, y = 60 + (i % 3) * 50; return `<g opacity="${op}" fill="${c}"><ellipse cx="${x}" cy="${y}" rx="110" ry="34"/><ellipse cx="${x + 60}" cy="${y - 20}" rx="70" ry="34"/><ellipse cx="${x - 60}" cy="${y - 8}" rx="60" ry="26"/></g>`; }).join('');
}
function skyBg(v, t, horizon = 430) {
  const key = skyKey(v), [a, b] = SKY[key];
  const sun = key === 'day' ? `<circle cx="1040" cy="120" r="46" fill="#fff4c4"/>` : key === 'dusk' || key === 'dawn' ? `<circle cx="1000" cy="${horizon - 40}" r="56" fill="#ffe2a0"/>` : key === 'night' ? `<circle cx="1060" cy="110" r="34" fill="#f2f0dc"/>` + Array.from({ length: 40 }, (_, i) => `<circle cx="${rnd(i) * 1280}" cy="${rnd(i + 50) * horizon * .8}" r="${1 + rnd(i + 7) * 1.6}" fill="#fff" opacity="${.4 + .4 * Math.sin(t * 2 + i)}"/>`).join('') : '';
  return `<rect width="1280" height="720" fill="${a}"/><rect y="${horizon * .55}" width="1280" height="${horizon * .45}" fill="${b}" opacity=".5"/>${sun}${clouds(t, v.storm || 0, key)}`;
}
const BG = {
  sea(v, t) { const key = skyKey(v), st = v.storm || 0, hz = v.horizon || 430; return skyBg(v, t, hz) + `<rect y="${hz}" width="1280" height="${720 - hz}" fill="${SEA[key]}"/>` + waves(t, hz + 40, st, '#d6eef8'); },
  seaFront(v, t) { const key = skyKey(v); return bigSwell(t, v.storm || 0, v.swellY || 600, SEA[key]); },
  deck(v, t) {   // on a ship's deck, horizon rolling
    const st = v.storm || 0, key = skyKey(v), roll = st * 3 * Math.sin(t * 1.2);
    return `<g transform="rotate(${roll} 640 360)">${skyBg(v, t, 400)}<rect x="-200" y="400" width="1680" height="400" fill="${SEA[key]}"/>${waves(t, 430, st, '#d6eef8')}</g>
     <rect x="-20" y="470" width="1320" height="270" fill="#8a5a34" stroke="${K}" stroke-width="${SW}"/>${Array.from({ length: 8 }, (_, i) => `<path d="M-20 ${500 + i * 30} L1300 ${500 + i * 30}" stroke="#6b4226" stroke-width="3"/>`).join('')}
     <rect x="-20" y="440" width="1320" height="34" fill="#6b4226" stroke="${K}" stroke-width="${SW}"/><rect x="1000" y="-20" width="34" height="500" fill="#5a3a22" stroke="${K}" stroke-width="${SW}"/>
     <path d="M1017 40 L760 446 M1017 40 L1260 446 M1017 160 L800 446" stroke="#3a2a1a" stroke-width="3"/>`;
  },
  below(v, t) {  // between decks: hammocks, cannon, lantern
    const sw = Math.sin(t * 1.2) * (2 + (v.storm || 0) * 3);
    return `<rect width="1280" height="720" fill="#5a3d26"/>${Array.from({ length: 7 }, (_, i) => `<rect x="${i * 200 - 20}" y="0" width="30" height="720" fill="#4a3020"/>`).join('')}<rect y="0" width="1280" height="60" fill="#3d2818"/>
     <rect y="560" width="1280" height="160" fill="#6b4a2e"/>${[180, 520, 860, 1180].map((x, i) => `<path d="M${x - 120} 90 Q${x} ${170 + sw} ${x + 120} 90" stroke="#e6dcc4" stroke-width="26" fill="none"/>`).join('')}
     <rect x="1020" y="380" width="120" height="80" fill="#2b1a10"/>` ;
  },
  beach(v, t) {  // Deal: shingle beach, sea behind, houses left
    const key = skyKey(v), st = v.storm || 0;
    return skyBg(v, t, 380) + `<rect y="380" width="1280" height="200" fill="${SEA[key]}"/>${waves(t, 410, st, '#d6eef8')}
     ${[0, 1, 2, 3].map(i => `<g><path d="M${i * 120 - 30} 520 L${i * 120 - 30} ${360 - (i % 2) * 30} L${i * 120 + 30} ${320 - (i % 2) * 30} L${i * 120 + 90} ${360 - (i % 2) * 30} L${i * 120 + 90} 520Z" fill="${['#b08a62', '#c49a6c', '#a87c56', '#bd9468'][i]}" stroke="${K}" stroke-width="${SW}"/><rect x="${i * 120 + 10}" y="${400 - (i % 2) * 30}" width="34" height="40" fill="${key.includes('night') ? '#ffd27a' : '#3a3040'}" stroke="${K}" stroke-width="3"/></g>`).join('')}
     <path d="M-20 500 Q640 470 1300 520 L1300 740 L-20 740Z" fill="#a99f8e" stroke="${K}" stroke-width="${SW}"/>${Array.from({ length: 60 }, (_, i) => `<circle cx="${rnd(i) * 1280}" cy="${520 + rnd(i + 3) * 200}" r="${3 + rnd(i + 1) * 5}" fill="#8f8676"/>`).join('')}`;
  },
  london(v, t) { return skyBg(v, t, 500) + `<path d="M760 420 L760 250 L790 220 L820 250 L820 420 M880 420 L880 250 L910 220 L940 250 L940 420 M760 330 L940 330" fill="#7a7a86" stroke="#55555f" stroke-width="10" opacity=".55"/><rect y="500" width="1280" height="220" fill="#6b6258"/>`; },
  river(v, t) { const key = skyKey(v); return skyBg(v, t, 420) + `<rect y="420" width="1280" height="300" fill="${SEA[key]}"/>${waves(t, 450, v.storm || 0, '#c9dfe8')}<path d="M-20 400 L300 380 L520 400 L800 370 L1300 400 L1300 430 L-20 430Z" fill="#6a6a6e" opacity=".7"/>`; },
  cellar(v, t) { return `<rect width="1280" height="720" fill="#4a4652"/>${[0, 1, 2, 3].map(i => `<path d="M${i * 380 - 100} 720 L${i * 380 - 100} 260 Q${i * 380 + 90} 40 ${i * 380 + 280} 260 L${i * 380 + 280} 720" fill="#5a5664" stroke="#3a3642" stroke-width="10"/>`).join('')}<rect y="580" width="1280" height="140" fill="#3a3640"/>`; },
  room(v, t) {   // bedroom/interior with window; lightning flashes in the window
    const fl = flashAmt(v, t);
    return `<rect width="1280" height="720" fill="${v.wall || '#c8b08a'}"/><rect y="560" width="1280" height="160" fill="#7a5a3a"/>${Array.from({ length: 6 }, (_, i) => `<path d="M0 ${580 + i * 26} L1280 ${580 + i * 26}" stroke="#6a4a2e" stroke-width="2"/>`).join('')}
     <rect x="${v.winX ?? 900}" y="120" width="180" height="230" fill="${fl > 0 ? '#e8f0ff' : (v.time === 'day' ? '#9fd3ee' : '#1c2a44')}" stroke="#5a4030" stroke-width="12"/><path d="M${(v.winX ?? 900) + 90} 120 L${(v.winX ?? 900) + 90} 350 M${v.winX ?? 900} 235 L${(v.winX ?? 900) + 180} 235" stroke="#5a4030" stroke-width="8"/>
     ${v.fireplace ? `<rect x="120" y="360" width="240" height="200" fill="#8a6a4a" stroke="${K}" stroke-width="${SW}"/><rect x="170" y="420" width="140" height="140" fill="#2b1a10"/><circle cx="240" cy="520" r="${50 + Math.sin(t * 9) * 4}" fill="url(#glow)"/>` : ''}`;
  },
  desk(v, t) { return `<rect width="1280" height="720" fill="#8a6a4a"/>${Array.from({ length: 6 }, (_, i) => `<rect x="${60 + i * 200}" y="60" width="150" height="260" fill="#6b4a32" stroke="#4a3020" stroke-width="6"/>`).join('')}${Array.from({ length: 30 }, (_, i) => `<rect x="${70 + (i % 6) * 200 + (i % 5) * 26}" y="${80 + Math.floor(i / 6) * 50}" width="20" height="44" fill="${['#8a2a1a', '#2a4a6a', '#3a5a2a', '#6a4a1a'][i % 4]}"/>`).join('')}
     <rect x="-20" y="520" width="1320" height="220" fill="#5a3a22" stroke="${K}" stroke-width="${SW}"/>`; },
  fields(v, t) { const st = v.storm || 0; return skyBg(v, t, 470) + `<path d="M-20 470 Q320 430 640 460 Q960 490 1300 450 L1300 740 L-20 740Z" fill="#6f9a52" stroke="${K}" stroke-width="${SW}"/><path d="M-20 560 Q640 520 1300 580 L1300 740 L-20 740Z" fill="#5f8a44"/>` + (v.flood ? `<rect y="${600 - v.flood * 140 * ease((v._lt || 0) / 4)}" width="1280" height="400" fill="#5a7f95" opacity=".9"/>${waves(t, 610 - v.flood * 140, st, '#c9dfe8')}` : ''); },
  underwater(v, t) { return `<rect width="1280" height="720" fill="url(#uw)"/>${Array.from({ length: 5 }, (_, i) => `<path d="M${200 + i * 230 + Math.sin(t + i) * 20} 0 L${120 + i * 230} 720 L${200 + i * 230} 720 Z" fill="#fff" opacity=".06"/>`).join('')}
     <path d="M-20 600 Q400 560 800 600 Q1100 630 1300 590 L1300 740 L-20 740Z" fill="#c9b890" stroke="${K}" stroke-width="${SW}"/>${Array.from({ length: 20 }, (_, i) => { const k = ((t * .15 + rnd(i)) % 1); return `<circle cx="${rnd(i + 3) * 1280 + Math.sin(t * 2 + i) * 8}" cy="${700 - k * 720}" r="${3 + rnd(i) * 5}" fill="none" stroke="#dff4ff" stroke-width="2" opacity=".6"/>`; }).join('')}`; },
  sands(v, t) { const key = skyKey(v); return skyBg(v, t, 400) + `<rect y="400" width="1280" height="320" fill="${SEA[key]}"/>${waves(t, 420, v.storm || 0, '#d6eef8')}<path d="M80 600 Q400 520 760 560 Q1050 590 1240 640 L1240 660 L80 660Z" fill="#d9c99a" stroke="${K}" stroke-width="${SW}"/>`; },
  church(v, t) { return `<rect width="1280" height="720" fill="#d8cdb8"/>${[120, 400, 880, 1160].map(x => `<rect x="${x - 40}" y="0" width="80" height="620" fill="#c4b79e" stroke="#a89878" stroke-width="5"/>`).join('')}<path d="M500 420 L500 160 Q640 40 780 160 L780 420Z" fill="#9fc3e0" stroke="#a89878" stroke-width="10"/><rect y="600" width="1280" height="120" fill="#a8977a"/>`; },
  black(v, t) { return `<rect width="1280" height="720" fill="${v.color || '#0c0f14'}"/>`; },
  plain(v, t) { return `<rect width="1280" height="720" fill="${v.color || '#e9e2d0'}"/>`; },
};
function flashAmt(v, t) {
  if (!(v.fx || []).includes('lightning')) return 0;
  const p = (t + 0.37) % 4.3; return p < .09 ? 1 : p > .18 && p < .24 ? .6 : 0;
}

// ---------- items dispatcher ----------
function items(v, t, lt) {
  const st = v.storm || 0, wind = INDOOR.includes(v.bg) ? 0 : (v.fx || []).includes('wind') ? 1 : st >= 2 ? .6 : 0;
  return (v.items || []).map(it => {
    const ilt = lt - (it.from || 0);
    if (it.from != null && ilt < 0) return '';
    if (it.until != null && lt > it.until) return '';
    switch (it.k) {
      case 'p': return person(it, t, ilt, wind);
      case 'ship': return ship(it, t, ilt, st);
      case 'boat': return boat(it, t, ilt, st);
      case 'roofs': return chimneyRow(it, t, ilt, st);
      case 'tree': return tree(it, t, ilt, st);
      case 'windmill': return windmill(it, t, ilt, st);
      case 'lighthouse': return lighthouse(it, t, ilt, st);
      case 'bed': return bed(it, t, ilt);
      case 'paper': return paper(it, t, ilt);
      case 'text': return bigText(it, t, ilt);
      case 'count': return counter(it, t, ilt);
      case 'gauge': return gauge(it, t, ilt);
      case 'rope': return rope(it, t, ilt);
      case 'cannon': return cannon(it);
      case 'lantern': return lantern(it.x, it.y, t, it.s || 1);
      case 'candle': return candle(it.x, it.y, t, it.s || 1);
      case 'table': return `<rect x="${it.x - (it.w || 300) / 2}" y="${it.y}" width="${it.w || 300}" height="24" fill="#6b4226" stroke="${K}" stroke-width="${SW}"/><rect x="${it.x - (it.w || 300) / 2 + 20}" y="${it.y + 24}" width="18" height="${560 - it.y}" fill="#6b4226" stroke="${K}" stroke-width="3"/><rect x="${it.x + (it.w || 300) / 2 - 38}" y="${it.y + 24}" width="18" height="${560 - it.y}" fill="#6b4226" stroke="${K}" stroke-width="3"/>`;
      case 'wave': { const k = ease((ilt) / (it.dur || 1.4)); const x = -700 + k * 2200; return k > 0 && k < 1 ? `<path d="M${x - 900} 760 L${x - 900} 300 Q${x - 300} 180 ${x} 260 Q${x + 120} 300 ${x + 60} 380 Q${x + 160} 420 ${x + 200} 760Z" fill="#2c5e7a" stroke="${K}" stroke-width="5" opacity=".95"/><path d="M${x - 200} 250 Q${x} 220 ${x + 40} 300" stroke="#fff" stroke-width="10" fill="none"/>` : ''; }
      case 'debris': return Array.from({ length: it.n || 10 }, (_, i) => { const k = ((t * (.5 + rnd(i) * .5) + rnd(i + 5)) % 1); return `<rect x="${-80 + k * 1440}" y="${(it.y || 200) + rnd(i + 2) * (it.h || 300) + Math.sin(t * 5 + i) * 30}" width="${18 + rnd(i) * 20}" height="${8 + rnd(i + 1) * 8}" fill="${['#8a4436', '#3b3b45', '#6b4226'][i % 3]}" stroke="${K}" stroke-width="2" transform="rotate(${t * 400 * rnd(i)} ${-80 + k * 1440} ${(it.y || 200) + rnd(i + 2) * (it.h || 300)})"/>`; }).join('');
      case 'flag': return `<g transform="translate(${it.x},${it.y})"><path d="M0 0 L0 -180" stroke="${K}" stroke-width="6"/><path d="M0 -180 Q40 ${-190 + Math.sin(t * 6) * 10} 90 -175 L90 -125 Q40 ${-140 + Math.sin(t * 6) * 10} 0 -130Z" fill="${it.c || '#b8322a'}" stroke="${K}" stroke-width="3"/></g>`;
      case 'raw': return it.svg || '';
      default: return '';
    }
  }).join('');
}

// ---------- fx ----------
function fx(v, t, lt) {
  const f = v.fx || [], st = INDOOR.includes(v.bg) ? 0 : (v.storm || 0);
  let out = '';
  if (f.includes('rain') || st >= 2) { const n = 40 + st * 25; for (let i = 0; i < n; i++) { const k = (t * (1.6 + rnd(i)) + rnd(i + 9)) % 1; const x = (rnd(i) * 1500 - 100) + k * 260; const y = -40 + k * 800; out += `<path d="M${x} ${y} l${-14 - st * 6} 30" stroke="#dfe8f0" stroke-width="2.5" opacity=".55"/>`; } }
  if (f.includes('wind') || st >= 2) { for (let i = 0; i < 8 + st * 4; i++) { const k = (t * (.8 + rnd(i) * .7) + rnd(i + 3)) % 1; const x = -300 + k * 1900, y = 80 + rnd(i + 11) * 520; out += `<path d="M${x} ${y} q80 -14 160 0 q40 8 70 -6" stroke="#fff" stroke-width="3.5" fill="none" opacity="${.5 * Math.sin(k * Math.PI)}" stroke-linecap="round"/>`; } }
  if (f.includes('snow') || f.includes('ash')) for (let i = 0; i < 60; i++) out += `<circle cx="${(rnd(i) * 1280 + t * 30) % 1280}" cy="${(rnd(i + 9) * 720 + t * (30 + rnd(i) * 40)) % 720}" r="${2 + rnd(i) * 3}" fill="#e8e6e2" opacity=".75"/>`;
  if (f.includes('spray')) for (let i = 0; i < 14; i++) { const k = (t * .9 + rnd(i)) % 1; out += `<circle cx="${rnd(i + 2) * 1280}" cy="${600 - k * 300}" r="${6 + rnd(i) * 10}" fill="#fff" opacity="${.6 * (1 - k)}"/>`; }
  const fl = flashAmt(v, t); if (fl) out += `<rect width="1280" height="720" fill="#eaf2ff" opacity="${fl * .45}"/>`;
  if (f.includes('night') || (v.time === 'night')) out += `<rect width="1280" height="720" fill="#0a1530" opacity=".18"/>`;
  if (f.includes('sepia')) out += `<rect width="1280" height="720" fill="#a07a40" opacity=".18"/>`;
  return out;
}

// ---------- one scene ----------
function sceneSvg(v, t, lt, dur) {
  v._lt = lt;
  const bgf = BG[v.bg] || BG.plain;
  // camera: slow push-in by default
  const cam = v.cam || 'in', k = clamp(lt / Math.max(dur, .1));
  let z = 1, px = 0, py = 0;
  if (cam === 'in') z = 1 + .06 * k; else if (cam === 'out') z = 1.08 - .07 * k; else if (cam === 'left') px = 40 - 80 * k; else if (cam === 'right') px = -40 + 80 * k; else if (cam === 'zoom') z = 1 + .25 * ease((lt - (v.zoomAt || 0)) / 1.2);
  const cx = v.cx || 640, cy = v.cy || 380;
  const shake = (v.fx || []).includes('shake') || (v.shakeAt != null && lt > v.shakeAt && lt < v.shakeAt + 1.5) ? (Math.sin(t * 61) * 5 + Math.sin(t * 43) * 3) * ((v.storm || 1) / 2 + .5) : 0;
  const bg = bgf(v, t);
  const blurBg = v.blur !== false && !['black', 'plain', 'underwater'].includes(v.bg);
  const front = v.bg === 'sea' || v.bg === 'sands' ? BG.seaFront(v, t) : '';
  const bubble = v.bubble ? bubbleSvg(v.bubble.x || 640, v.bubble.y || 150, v.bubble.text, back((lt - (v.bubble.at || .3)) / .35), v.bubble.tail) : '';
  const bubble2 = v.bubble2 ? bubbleSvg(v.bubble2.x || 640, v.bubble2.y || 150, v.bubble2.text, back((lt - (v.bubble2.at || .8)) / .35), v.bubble2.tail) : '';
  return `<g transform="translate(${shake + px},${shake * .6 + py}) translate(${cx} ${cy}) scale(${z}) translate(${-cx} ${-cy})">
    <g ${blurBg ? 'filter="url(#bl)"' : ''}>${bg}</g>${items(v, t, lt)}${front}${fx(v, t, lt)}${bubble}${bubble2}</g>`;
}

// ---------- timeline of the long video ----------
const SC = [];
E.chapters.forEach((c, ci) => c.scenes.forEach((s, si) => SC.push({ v: s.v || { bg: 'plain' }, ci, first: si === 0, chap: c })));
const B = V.blocks;
const starts = B.map((b, i) => i === 0 ? 0 : b[0] - .2);
const DUR = V.dur;
const TC = E.title_card ? E.title_card.after_scene : -1;       // title card inserted before this scene
const TCD = 3.2;                                               // the voice has a pause there (voice.json gap)
// words of each block, relative trigger lookup: scene v.at can be "word"
function wordTime(block, word) {
  const w = V.words.find(x => x[3] === block && x[0].toLowerCase().replace(/[^a-z0-9'-]/g, '') === word.toLowerCase());
  return w ? w[1] : null;
}
function resolveAts(v, i) {   // replace {"at":"word"} with seconds relative to the scene start
  if (v._resolved) return v;
  const rel = w => { const x = wordTime(i, w); return x == null ? 0 : x - starts[i]; };
  const walk = o => { for (const k in o) { const val = o[k]; if (typeof val === 'string' && /^@/.test(val)) o[k] = rel(val.slice(1)); else if (val && typeof val === 'object') walk(val); } };
  walk(v); v._resolved = 1; return v;
}
SC.forEach((s, i) => resolveAts(s.v, i));

function captionSvg(t, vertical, words) {
  const W = words || V.words;
  // chunks of up to 6 words inside one block
  if (!captionSvg.ch || captionSvg.src !== W) {
    const ch = []; let cur = [];
    W.forEach((w, k) => { cur.push(k); const nx = W[k + 1]; if (!nx || cur.length >= (vertical ? 3 : 6) || /[.,?!;:]$/.test(w[0]) || nx[3] !== w[3]) { ch.push(cur); cur = []; } });
    captionSvg.ch = ch; captionSvg.src = W;
  }
  const ch = captionSvg.ch;
  let c = null;
  for (let i = 0; i < ch.length; i++) { const a = W[ch[i][0]][1] - .05, b = i + 1 < ch.length ? W[ch[i + 1][0]][1] - .05 : W[ch[i][ch[i].length - 1]][2] + .3; if (t >= a && t < Math.min(b, W[ch[i][ch[i].length - 1]][2] + .6)) { c = ch[i]; break; } }
  if (!c) return '';
  const spans = c.map(k => `<tspan fill="${t >= W[k][1] - .02 && t < W[k][2] + .08 ? '#ffd21f' : '#fff'}">${esc(W[k][0])} </tspan>`).join('');
  return vertical ? `<text x="540" y="1330" text-anchor="middle" font-weight="bold" font-size="76" stroke="#000" stroke-width="12" paint-order="stroke" stroke-linejoin="round">${spans}</text>`
    : `<text x="640" y="672" text-anchor="middle" font-weight="bold" font-size="38" stroke="#000" stroke-width="7" paint-order="stroke" stroke-linejoin="round">${spans}</text>`;
}
function badgeSvg(text, sub, a, vertical) {
  if (!text || a <= 0) return '';
  const w = Math.max(text.length * 17 + 40, 150);
  const x = vertical ? 540 : 1240 - w / 2, y = vertical ? 330 : 58;
  return `<g opacity="${a}" transform="translate(${x},${y})"><rect x="${-w / 2}" y="-34" width="${w}" height="${sub ? 78 : 64}" rx="8" fill="rgba(15,15,20,.9)" stroke="rgba(255,255,255,.3)" stroke-width="2"/>
   <text y="${sub ? -4 : 8}" text-anchor="middle" fill="#fff" font-size="28" font-weight="bold">${esc(text)}</text>${sub ? `<text y="28" text-anchor="middle" fill="#ffd21f" font-size="19" font-weight="bold" letter-spacing="2">${esc(sub)}</text>` : ''}</g>`;
}
function chapterSvg(title, lt) {
  if (!title || lt > 3.4) return '';
  const a = clamp(lt / .3) * clamp((3.4 - lt) / .4);
  const w = title.length * 19 + 70;
  return `<g opacity="${a}" transform="translate(${40 - (1 - clamp(lt / .35)) * 60},40)"><rect width="${w}" height="52" rx="6" fill="#b8322a" stroke="${K}" stroke-width="3"/><text x="${w / 2}" y="35" text-anchor="middle" fill="#fff" font-size="26" font-weight="bold" letter-spacing="1">${esc(title)}</text></g>`;
}
function titleCard(lt) {
  const L = E.title_card.lines, a = clamp(lt / .35), b = clamp((lt - .5) / .35);
  return `<rect width="1280" height="720" fill="#0c0f14"/><g opacity="${a}" transform="translate(640,320) scale(${.9 + .1 * ease(lt / .6)})"><text text-anchor="middle" font-size="${Math.min(62, 1750 / L[0].length)}" font-weight="bold" fill="#fff" letter-spacing="2">${esc(L[0])}</text></g>
   <g opacity="${b}"><rect x="440" y="360" width="400" height="8" fill="#b8322a"/><text x="640" y="420" text-anchor="middle" font-size="32" font-weight="bold" fill="#ffd21f">${esc(L[1] || '')}</text></g>`;
}
function badgeFor(i) { // latest badge defined at or before scene i
  for (let k = i; k >= 0; k--) if (SC[k].v.badge !== undefined) return SC[k].v.badge;
  return null;
}

function frameLong(t) {
  let i = 0; while (i + 1 < SC.length && t >= starts[i + 1]) i++;
  const s = SC[i], lt = t - starts[i], dur = (i + 1 < SC.length ? starts[i + 1] : DUR) - starts[i];
  let out = sceneSvg(s.v, t, lt, dur);
  // crossfade from previous scene
  const cf = s.v.cut ? 1 : clamp(lt / .28);
  if (i > 0 && cf < 1) out = sceneSvg(SC[i - 1].v, t, t - starts[i - 1], starts[i] - starts[i - 1]) + `<g opacity="${ease(cf)}">${out}</g>`;
  // title card sits in the pause before scene TC
  const inTC = TC > 0 && i === TC - 1 && t > B[i][1] + .15;
  if (inTC) out = titleCard(t - B[i][1] - .15);
  const bd = badgeFor(i);
  const hideOverlay = inTC || s.v.bg === 'black';
  let ov = `<rect width="1280" height="720" fill="url(#vig)"/>`;
  if (!hideOverlay) {
    ov += badgeSvg(bd && bd[0], bd && bd[1], 1, false);
    if (s.first && s.chap.title) ov += chapterSvg(s.chap.title, lt);
  }
  ov += captionSvg(t, false);
  return DEFS + out + ov;
}

// ---------- Shorts (vertical): block k shows long scene src, cropped around focus x ----------
function frameShort(k, t) {
  const S = E.shorts[k], SV = window.SHORTV[k], bl = SV.blocks, n = bl.length;
  const st = bl.map((b, i) => i === 0 ? 0 : b[0] - .12);
  let i = 0; while (i + 1 < n && t >= st[i + 1]) i++;
  const blk = i === n - 1 ? Object.assign({}, S.blocks[i], { src: S.blocks[0].src, v: S.blocks[0].v, fx: S.blocks[0].fx, offset: (S.blocks[0].offset || 0) }) : S.blocks[i], src = blk.src;
  const v = blk.v || SC[src].v, lt = t - st[i] + (blk.offset || 0);   // standalone Shorts give each block its own "v"
  const fx_ = blk.fx != null ? blk.fx : (v.fx_short != null ? v.fx_short : (v.focus || 640));
  const x0 = clamp(fx_ - 202.5, 0, 1280 - 405);
  SHORT = { x0 };
  const inner = sceneSvg(v, t, lt, 6);
  const cf = clamp((t - st[i]) / .2);
  let prev = '';
  if (i > 0 && cf < 1) { const pb = S.blocks[i - 1], pv = pb.v || SC[pb.src].v, pfx = pb.fx != null ? pb.fx : (pv.focus || 640); SHORT = { x0: clamp(pfx - 202.5, 0, 875) }; prev = `<svg x="0" y="0" width="1080" height="1920" viewBox="${clamp(pfx - 202.5, 0, 875)} 0 405 720" preserveAspectRatio="xMidYMid slice">${DEFS}${sceneSvg(pv, t, t - st[i - 1], 6)}</svg>`; }
  SHORT = { x0 }; const inner2 = inner; SHORT = null;
  const main = `<svg x="0" y="0" width="1080" height="1920" viewBox="${x0} 0 405 720" preserveAspectRatio="xMidYMid slice" opacity="${prev ? ease(cf) : 1}">${DEFS}${inner}</svg>`;
  const lab = S.label, lw = lab.length * 30 + 70;
  const ov = `<rect width="1080" height="1920" fill="url(#vig)"/><g transform="translate(540,190)"><rect x="${-lw / 2}" y="-46" width="${lw}" height="84" rx="12" fill="#b8322a" stroke="${K}" stroke-width="4"/><text y="14" text-anchor="middle" fill="#fff" font-size="46" font-weight="bold">${esc(lab)}</text></g>
    <text x="540" y="1760" text-anchor="middle" fill="#fff" font-size="38" font-weight="bold" stroke="#000" stroke-width="6" paint-order="stroke">${esc(S.footer || ('Full story: ' + E.title))}</text>` + captionSvg(t, true, SV.words);
  return DEFS + prev + main + ov;
}

// ---------- thumbnail ----------
function frameThumb() {
  const v = JSON.parse(JSON.stringify(SC[E.thumb_scene || 0].v)); (v.items || []).forEach(it => { if (it.x != null) it.x += (E.thumb_dx || 0); }); v.cam = 'none';
  const lines = (E.thumb_text || E.title).toUpperCase().split('\n');
  const tx = lines.map((l, k) => `<text x="60" y="${300 + k * 120}" font-size="${k === 0 ? 112 : 96}" font-weight="bold" fill="${k === 0 ? '#ffd21f' : '#fff'}" stroke="#000" stroke-width="14" paint-order="stroke" stroke-linejoin="round">${esc(l)}</text>`).join('');
  return DEFS + `${sceneSvg(v, E.thumb_t || 3, E.thumb_t || 3, 6)}<rect width="760" height="720" fill="url(#thg)"/><defs><linearGradient id="thg" x1="0" x2="1"><stop offset="0" stop-color="#000" stop-opacity=".75"/><stop offset="1" stop-color="#000" stop-opacity="0"/></linearGradient></defs>` + tx + `<rect x="60" y="${300 + lines.length * 120 - 70}" width="280" height="14" fill="#b8322a"/>`;
}

window.DUR = DUR;
window.seek = t => { document.getElementById('sv').innerHTML = frameLong(t); };
window.seekShort = (k, t) => { document.getElementById('sv').innerHTML = frameShort(k, t); };
window.thumb = () => { document.getElementById('sv').innerHTML = frameThumb(); };
window.SCENE_STARTS = starts;
})();
