/* Endurance — motion graphics. Everything is a pure function of time: window.seek(t) */
const NS = 'http://www.w3.org/2000/svg';
const $ = s => document.querySelector(s), $$ = s => [...document.querySelectorAll(s)];
const S = (tag, attrs = {}, parent) => { const e = document.createElementNS(NS, tag); for (const k in attrs) e.setAttribute(k, attrs[k]); if (parent) parent.appendChild(e); return e; };
const H = (tag, cls, html, parent) => { const e = document.createElement(tag); if (cls) e.className = cls; if (html) e.innerHTML = html; if (parent) parent.appendChild(e); return e; };
const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
const M = window.MAP, PL = M.places, map = $('#map'), mdefs = $('#mdefs');
const DUR = 114.9; window.DUR = DUR;
const tl = gsap.timeline({ paused: true });
const st = { day: 0, out: 0, drift: 0, camp: 0, boats: 0, caird: 0, cross: 0, plan: 0, r1: 0, r2: 0, r3: 0, r4: 0, hnum: 0, d497: 0, n22: 0, depth: 0, shine: 0, sRot: 0, sY: 0, sq: 0, ridge: 0, crackA: 0, crackB: 0, lensS: .7, hRot: 0 };
const mid = (a, b) => [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2];
let seedv = 11; const rnd = () => (seedv = (seedv * 16807) % 2147483647) / 2147483647;

/* ---------------- MAP ---------------- */
S('path', { d: M.grat, class: 'grat' }, map);
S('path', { d: M.land, class: 'landglow' }, map);
const floesG = S('g', { id: 'floesG', opacity: 0 }, map);
S('path', { d: M.floes, class: 'floes' }, floesG);
const fringeG = S('g', { id: 'fringeG', opacity: 0 }, map);
S('path', { d: M.fringe, class: 'floes' }, fringeG);
// coarse land everywhere except inside the detail boxes, where the fine coastline is drawn
const holes = M.rects.map(([[x0, y0], [x1, y1]]) => `M${x0},${y0}H${x1}V${y1}H${x0}Z`).join('');
S('path', { d: 'M-3000,-3000H6000V6000H-3000Z' + holes, 'clip-rule': 'evenodd' }, S('clipPath', { id: 'coarse' }, mdefs));
S('path', { d: M.land, class: 'land', 'clip-path': 'url(#coarse)' }, map);
M.detail.forEach(d => S('path', { d, class: 'land' }, map));
const routesG = S('g', {}, map), fixG = S('g', {}, map);
const R = {}, fixes = [], rings = [];

function route(id, color, style) {
  const d = M.routes[id];
  const mask = S('mask', { id: 'm_' + id, maskUnits: 'userSpaceOnUse', x: -3000, y: -3000, width: 9000, height: 9000 }, mdefs);
  const mp = S('path', { d, fill: 'none', stroke: '#fff' }, mask);
  mp.style.strokeWidth = 'calc(34px*var(--ik))';
  const L = mp.getTotalLength(); mp.setAttribute('stroke-dasharray', L + ' ' + L); mp.setAttribute('stroke-dashoffset', L);
  const g = S('g', { mask: `url(#m_${id})`, id: 'rt_' + id }, routesG);
  if (style === 'solid') S('path', { d, class: 'rt halo', stroke: color }, g);
  S('path', { d, class: 'rt main ' + (style === 'solid' ? '' : style), stroke: color }, g);
  R[id] = { mp, L, g };
}
route('plan', '#ffffff', 'dash');
route('out', '#ffffff', 'solid');
route('drift', '#7fd6ff', 'dot');
route('camp', '#7fd6ff', 'dot');
route('boats', '#ff6b3d', 'solid');
route('caird', '#ff6b3d', 'solid');
route('cross', '#ff6b3d', 'dash');
route('r1', '#c9d8e0', 'dash'); route('r2', '#c9d8e0', 'dash'); route('r3', '#c9d8e0', 'dash');
route('r4', '#ff6b3d', 'solid');

function fix(pt, id) { const g = S('g', { class: 'fix' }, fixG); if (id) g.id = id; g._p = pt; fixes.push(g); return g; }
function label(g, txt, dx, dy, anchor = 'start', cls = 'lab', size) {
  const t = S('text', { x: dx, y: dy, 'text-anchor': anchor, class: cls }, g); t.textContent = txt; if (size) t.style.fontSize = size + 'px'; return t;
}
function marker(id, pt, txt, o = {}) {
  const g = fix(pt, 'mk_' + id); g.style.opacity = o.show ? 1 : 0;
  const color = o.color || '#ff6b3d';
  if (o.pulse !== false) { const r = S('circle', { r: 8, fill: 'none', stroke: color, 'stroke-width': 3 }, g); r._ph = rings.length * .37; rings.push(r); }
  if (o.x) S('path', { d: 'M-9,-9L9,9M9,-9L-9,9', stroke: color, 'stroke-width': 5, 'stroke-linecap': 'round', fill: 'none' }, g);
  else S('circle', { r: o.r || 7, fill: color, stroke: '#071a29', 'stroke-width': 3 }, g);
  if (txt) { const lines = txt.split('|'); lines.forEach((l, i) => { const tx = label(g, l, o.dx ?? 18, (o.dy ?? 7) + i * 25, o.anchor || 'start', 'lab', i ? 15 : null); if (i) { tx.style.strokeWidth = '4px'; tx.style.fontWeight = 600; tx.style.fill = '#cfe3ee'; } }); }
  return g;
}
// geography
const gAnt = fix([1470, 1000]); label(gAnt, 'Antarctica', 0, 0, 'middle', 'geo');
const gWed = fix([PL.weddell[0] + 30, PL.weddell[1] - 20]); label(gWed, 'Weddell Sea', 0, 0, 'middle', 'sea');
const gSco = fix(PL.scotia); label(gSco, 'Scotia Sea', 0, 0, 'middle', 'sea');
const geoLabs = [gAnt, gWed, gSco]; geoLabs.forEach(g => g.style.opacity = 0);
const mkSG = marker('sg', PL.sgHarbor, 'South Georgia', { color: '#fff', dx: -18, dy: -12, anchor: 'end' });
const mkVah = marker('vah', PL.vahsel, 'Vahsel Bay|planned landing', { color: '#fff', dx: 18, dy: 6, pulse: false, r: 5 });
const mkTrap = marker('trap', PL.trapped, 'Trapped|19 Jan 1915', { color: '#7fd6ff', dx: 18, dy: 0, pulse: false, r: 5 });
const mkSink = marker('sink', PL.sink, 'Endurance lost|21 Nov 1915', { color: '#ff4a4a', x: true, dx: 20, dy: 0, pulse: false });
const mkEI = marker('ei', PL.ei, 'Elephant Island', { color: '#fff', dx: -16, dy: 34, anchor: 'end' });
const mkHaa = marker('haa', PL.haakon, 'King Haakon Bay|landing, 10 May 1916', { color: '#ff6b3d', dx: -4, dy: 44, anchor: 'middle' });
const mkStr = marker('str', PL.stromness, 'Stromness|whaling station', { color: '#fff', dx: 10, dy: -44, anchor: 'middle' });
const mkPun = marker('pun', PL.punta, 'Punta Arenas', { color: '#fff', dx: 16, dy: -12, pulse: false, r: 5 });
const mkFal = marker('fal', PL.stanley, 'Falkland Is.', { color: '#fff', dx: 16, dy: -10, pulse: false, r: 5 });
const mkX = ['r1end', 'r2end', 'r3end'].map((k, i) => marker('x' + i, PL[k], null, { color: '#ff4a4a', x: true, pulse: false }));
const shipLab = ['Southern Sky', 'Instituto de Pesca', 'Emma', 'Yelcho'];
const head = marker('head', PL.sgHarbor, null, { color: '#fff' });
const head4 = marker('head4', PL.punta, 'Yelcho', { color: '#ff6b3d', dx: 4, dy: -24, anchor: 'middle' });

/* camera */
const camSegs = []; let camEnd = { c: [792, 585], k: .9 };
function camTo(t0, dur, target, k, ox = 0, oy = 0, ease = 'power2.inOut') {
  const prev = camEnd, c1 = [target[0] - ox / k, target[1] - oy / k]; let F, s0, s1;
  if (k >= prev.k) { F = target; s0 = [(F[0] - prev.c[0]) * prev.k, (F[1] - prev.c[1]) * prev.k]; s1 = [ox, oy]; }
  else { F = prev.c; s0 = [0, 0]; s1 = [(F[0] - c1[0]) * k, (F[1] - c1[1]) * k]; }
  camSegs.push({ t0, dur, F, s0, s1, z0: Math.log2(prev.k), z1: Math.log2(k), ease: gsap.parseEase(ease) });
  camEnd = { c: c1, k };
}
function camAt(t) {
  let seg = null; for (const s of camSegs) { if (s.t0 <= t) seg = s; else break; }
  if (!seg) return { c: [792, 585], k: .9 };
  const u = seg.ease(clamp((t - seg.t0) / seg.dur));
  const k = 2 ** (seg.z0 + (seg.z1 - seg.z0) * u), sx = seg.s0[0] + (seg.s1[0] - seg.s0[0]) * u, sy = seg.s0[1] + (seg.s1[1] - seg.s0[1]) * u;
  return { c: [seg.F[0] - sx / k, seg.F[1] - sy / k], k };
}
camTo(12.0, 12.2, [1070, 585], .95, 250, 0, 'sine.inOut');
camTo(26.0, 3.4, PL.trapped, 2.6, 300, 40);
camTo(35.1, 2.8, mid(PL.trapped, PL.sink), 1.75, 320, 0);
camTo(40.0, 1.0, PL.sink, 2.6, 300, 60);
camTo(49.5, 5.4, PL.launch, 3.0, 300, 150, 'sine.inOut');
camTo(55.3, 2.6, mid(PL.launch, PL.ei), 6.5, 320, 20);
camTo(65.9, 2.4, mid(PL.ei, PL.sg), 2.0, 330, 40);
camTo(81.3, 2.3, mid(PL.haakon, PL.stromness), 24, 300, 30);
camTo(89.5, 2.0, [569, 270], 1.7, 0, 0);
camTo(96.2, 1.8, PL.ei, 6, 300, 0);

/* HUD timeline */
const EV = [[45, 'TRAPPED'], [351, 'SHIP LOST'], [497, 'LAND'], [634, 'RESCUE']];
const evEls = EV.map(([d, n]) => { const e = H('div', 'ev', n, $('#tlbar')); e.style.left = (d / 634 * 100) + '%'; e._d = d; return e; });
const MON = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'], D0 = Date.UTC(1914, 11, 5);

/* cards */
function card(id, y, html, tin, tout) {
  const el = H('div', 'card', html, $('#cards')); el.id = id; el.style.top = y + 'px';
  tl.fromTo(el, { opacity: 0, x: -50 }, { opacity: 1, x: 0, duration: .6, ease: 'power3.out' }, tin);
  if (tout != null) tl.to(el, { opacity: 0, x: -30, duration: .35, ease: 'power2.in' }, tout);
  return el;
}
const K = (k, t, s) => `<div class="k">${k}</div><div class="t">${t}</div>` + (s ? `<div class="s">${s}</div>` : '');
card('cA', 330, K('December 1914', 'Shackleton<br>sails south', 'The ship <b>Endurance</b> · 28 men aboard'), 12.3, 19.0);
card('cB', 330, K('The plan', 'Cross Antarctica<br>on foot', '1,800 miles, coast to coast, by way of the South Pole'), 19.5, 22.0);
card('cB2', 330, K('The reality', 'He never<br>reaches land', 'The ship stops one day’s sail short of the coast'), 22.35, 24.4);
card('cC', 330, K('19 January 1915', 'Frozen in', '76°34′ S · the pack ice of the Weddell Sea closes around the hull'), 27.7, 30.7);
card('cQ', 350, `<div class="q">“Frozen, like an almond in the middle of a chocolate bar.”</div><div class="s">— Thomas Orde-Lees, storekeeper</div>`, 31.0, 34.9);
card('cD', 330, K('February – November 1915', '10 months<br>adrift', 'The ice carries the trapped ship slowly north'), 35.4, 38.5);
card('cE', 330, K('November 1915 – April 1916', '5 months<br>on the floes', 'The crew camps on drifting ice: Ocean Camp, then Patience Camp'), 49.6, 54.9);
card('cE2', 330, K('9 April 1916', 'Three<br>lifeboats', 'Nearly a week of rowing through ice and open sea'), 55.4, 61.4);
card('cF', 290, `<div class="k">Elephant Island · 15 April 1916</div><div class="big"><span id="n497">0</span></div><div class="s">days since they last stood on solid ground</div>`, 61.8, 65.7);
card('cG0', 330, K('The problem', 'No ship will<br>ever pass here', 'Elephant Island lies far from every shipping lane'), 66.1, 67.85);
card('cG', 300, K('The James Caird', '22.5 feet<br>of lifeboat',
  `<svg viewBox="0 0 560 120" width="560" height="120" style="margin:6px 0 2px"><path d="M10,58 C40,104 440,108 540,50 L500,58 L40,60Z" fill="#e6f1f6"/><path d="M200,58 L200,4 M330,58 L330,14" stroke="#e6f1f6" stroke-width="5"/><path d="M204,8 L290,52 L204,52Z M334,18 L400,52 L334,52Z" fill="rgba(230,241,246,.55)"/>${[0, 1, 2, 3, 4, 5].map(i => `<use href="#man" x="${70 + i * 66}" y="30" width="15" height="28" fill="#ff6b3d"/>`).join('')}</svg>Shackleton and five men`), 68.1, 72.6);
card('cH', 290, `<div class="k">24 April – 10 May 1916</div><div class="big"><span id="nm">0</span></div><div class="s">nautical miles across the stormiest ocean on Earth</div><div class="t" id="d16" style="opacity:0;font-size:70px;color:var(--acc);margin-top:18px">16 days at sea</div>`, 73.0, 81.0);
card('cI', 330, K('South Georgia', 'The wrong side<br>of the island', 'The whaling stations are all on the north coast'), 81.6, 83.6);
card('cJ', 330, K('Shackleton · Worsley · Crean', '36 hours', 'on foot across unmapped mountains and glaciers, without a tent'), 83.9, 89.3);
card('cK', 310, K('May – August 1916', '4 rescue<br>attempts', 'Three ships are turned back by the pack ice') + `<div class="pips"><span>✕</span><span>✕</span><span>✕</span><span>✓</span></div>`, 89.9, 96.0);
card('cL', 330, K('30 August 1916', 'He counts<br>the figures', '<b><span id="n22">0</span> of 22</b> men on the beach'), 96.3, 98.5);
const pips = $$('.pips span');

/* ---------------- HOOK ---------------- */
const manSVG = c => `<svg viewBox="0 0 24 46"><use href="#man" fill="${c}"/></svg>`;
for (let i = 0; i < 28; i++) H('div', 'man', manSVG('#e6f1f6'), $('#h_men'));
for (let i = 0; i < 28; i++) H('div', 'man', manSVG('#e6f1f6'), $('#e_men'));
$('#e_sub').textContent = '634 DAYS AFTER LEAVING SOUTH GEORGIA · NOT ONE MAN LOST';

tl.fromTo('#h_title', { opacity: 0, y: 40 }, { opacity: 1, y: 0, duration: .7, ease: 'power3.out' }, .45)
  .fromTo('#h_title span', { opacity: 0 }, { opacity: 1, duration: .4 }, 1.35)
  .to('#h_title', { scale: .36, y: -70, transformOrigin: '0 0', duration: .7, ease: 'power3.inOut' }, 2.55)
  .fromTo('#h_men .man', { opacity: 0, scale: .4 }, { opacity: 1, scale: 1, duration: .35, ease: 'back.out(2)', stagger: .042 }, 2.9)
  .fromTo('#h_menlab', { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: .5, ease: 'power2.out' }, 3.5)
  .fromTo('#h_ship', { opacity: 0, x: 60 }, { opacity: 1, x: 0, duration: .9, ease: 'power2.out' }, 5.0)
  .to(st, { hRot: -14, duration: 5.2, ease: 'power1.inOut' }, 5.3)
  .fromTo('#h_dist', { opacity: 0 }, { opacity: 1, duration: .4 }, 6.85)
  .fromTo('#h_dist .ln', { scaleX: 0, transformOrigin: '0 50%' }, { scaleX: 1, duration: 2.0, ease: 'power2.inOut' }, 6.95)
  .to(st, { hnum: 1000, duration: 2.0, ease: 'power2.inOut' }, 6.95)
  .fromTo('#h_cap2,#h_dist .b', { opacity: 0 }, { opacity: 1, duration: .3 }, 8.8)
  .to('#h_title,#h_men,#h_menlab,#h_ship,#h_dist', { opacity: .05, duration: .5 }, 9.7)
  .fromTo('#h_last', { opacity: 0, scale: 1.08 }, { opacity: 1, scale: 1, duration: .7, ease: 'power3.out' }, 9.9)
  .to('#hook', { opacity: 0, duration: .65, ease: 'power1.inOut' }, 11.35);

/* ---------------- MAP SCENES ---------------- */
tl.fromTo(geoLabs, { opacity: 0 }, { opacity: 1, duration: 1, stagger: .15 }, 12.2)
  .to(mkSG, { opacity: 1, duration: .5 }, 12.3)
  .to(head, { opacity: 1, duration: .4 }, 15.5)
  .to(st, { out: 1, duration: 6.9, ease: 'power1.inOut' }, 15.7)
  .to(st, { day: 45, duration: 6.9, ease: 'power1.inOut' }, 15.7)
  .to(mkVah, { opacity: 1, duration: .4 }, 19.6)
  .to(st, { plan: 1, duration: 1.6, ease: 'power1.inOut' }, 19.8)
  .to('#rt_plan', { opacity: .28, duration: .5 }, 22.4)
  .to(mkVah, { opacity: .45, duration: .5 }, 22.4)
  // S2 trapped
  .to([floesG, fringeG], { opacity: 1, duration: 2.6, ease: 'power1.inOut' }, 25.5)
  .to(mkTrap, { opacity: 1, duration: .5 }, 28.0)
  .to(mkVah, { opacity: 0, duration: .5 }, 34.8).to('#rt_plan', { opacity: 0, duration: .5 }, 34.8)
  // S3 drift
  .to(st, { drift: 1, duration: 3.2, ease: 'power1.inOut' }, 35.4)
  .to(st, { day: 326, duration: 3.2, ease: 'power1.inOut' }, 35.4)
  .to(mkSink, { opacity: 1, duration: .3 }, 40)
  .to(st, { day: 351, duration: 3.2, ease: 'none' }, 43.1)
  // S4 camps and boats
  .to(st, { camp: 1, duration: 5.0, ease: 'sine.inOut' }, 49.7)
  .to(st, { day: 491, duration: 5.0, ease: 'sine.inOut' }, 49.7)
  .to(fringeG, { opacity: .3, duration: 1.6 }, 53.0)
  .to(st, { boats: 1, duration: 3.5, ease: 'power1.inOut' }, 57.3)
  .to(st, { day: 497, duration: 3.5, ease: 'power1.inOut' }, 57.3)
  .to(mkEI, { opacity: 1, duration: .4 }, 60.3)
  .to(st, { d497: 497, duration: 2.5, ease: 'power2.out' }, 61.9)
  // S5 James Caird
  .to('#rt_out', { opacity: 0, duration: .5 }, 65.9).to(mkTrap, { opacity: 0, duration: .5 }, 65.9)
  .to(geoLabs, { opacity: .0, duration: .4 }, 65.9).to([gSco], { opacity: 1, duration: .6 }, 67)
  .to(st, { day: 506, duration: 4, ease: 'none' }, 68.2)
  .to(st, { caird: 1, duration: 6.1, ease: 'power1.inOut' }, 72.9)
  .to(st, { day: 522, duration: 6.1, ease: 'power1.inOut' }, 72.9)
  .to('#d16', { opacity: 1, duration: .4 }, 77.6)
  // S6 South Georgia
  .to(mkSG, { opacity: 0, duration: .4 }, 81.3).to(gSco, { opacity: 0, duration: .4 }, 81.3)
  .to(mkHaa, { opacity: 1, duration: .4 }, 81.9)
  .to(mkStr, { opacity: .55, duration: .4 }, 82.6)
  .to(st, { cross: 1, duration: 3.6, ease: 'power1.inOut' }, 83.9)
  .to(st, { day: 532, duration: 3.6, ease: 'power1.inOut' }, 83.9)
  .to(mkStr, { opacity: 1, duration: .3 }, 87.6)
  // rescue attempts
  .to('#rt_caird,#rt_boats', { opacity: .3, duration: .4 }, 89.4)
  .to([mkHaa, mkStr, head], { opacity: 0, duration: .4 }, 89.4).to('#rt_cross', { opacity: 0, duration: .4 }, 89.4)
  .to([mkSG, mkPun, mkFal], { opacity: 1, duration: .5 }, 90.0).to(fringeG, { opacity: .9, duration: .8 }, 89.6)
  .to(st, { day: 634, duration: 6.4, ease: 'none' }, 89.8)
  .to(st, { r1: 1, duration: .9, ease: 'power1.out' }, 90.6).to(mkX[0], { opacity: 1, duration: .2 }, 91.45)
  .to(st, { r2: 1, duration: .8, ease: 'power1.out' }, 91.5).to(mkX[1], { opacity: 1, duration: .2 }, 92.25)
  .to(st, { r3: 1, duration: .8, ease: 'power1.out' }, 92.3).to(mkX[2], { opacity: 1, duration: .2 }, 93.05)
  .to('#rt_r1,#rt_r2,#rt_r3', { opacity: .45, duration: .4 }, 93.2)
  .to(head4, { opacity: 1, duration: .3 }, 93.4)
  .to(st, { r4: 1, duration: 2.7, ease: 'power1.inOut' }, 93.5)
  .to(mkX, { opacity: 0, duration: .4 }, 96.2).to('#rt_r1,#rt_r2,#rt_r3', { opacity: 0, duration: .4 }, 96.2)
  .to(st, { n22: 22, duration: 1.5, ease: 'none' }, 96.75);

/* ---------------- SHIP SCENE ---------------- */
const stars = $('#stars'); for (let i = 0; i < 70; i++) S('circle', { cx: rnd() * 1920, cy: rnd() * 420, r: .8 + rnd() * 1.6, opacity: .25 + rnd() * .6 }, stars);
const crackD = [['M610,800 L560,838 L590,872 L520,930 L548,968', 'A'], ['M700,760 L742,812 L716,858 L770,918', 'A'], ['M1330,800 L1392,842 L1360,884 L1432,940', 'A'],
  ['M1240,764 L1196,818 L1228,866 L1170,930 L1196,984', 'B'], ['M300,880 L352,930 L318,978 L372,1040', 'B'], ['M1500,868 L1452,926 L1492,972 L1440,1040', 'B'], ['M900,860 L940,910 L908,956 L960,1020', 'B']];
const cracks = crackD.map(([d, grp]) => { const p = S('path', { d }, $('#s_cracks')); p._L = p.getTotalLength(); p._g = grp; p.setAttribute('stroke-dasharray', p._L + ' ' + p._L); return p; });
const shipWrap = $('#s_ship');
tl.to('#shipL', { opacity: 1, duration: .5 }, 38.5)
  .to(st, { sq: .35, duration: 1.3, ease: 'power2.inOut' }, 39.3).to(st, { sRot: -4, duration: 1.3, ease: 'power2.inOut' }, 39.3)
  .to(st, { sq: .6, sRot: -10, ridge: .5, crackA: 1, duration: .5, ease: 'power3.out' }, 40.85)
  .to(st, { sq: 1, sRot: -17, ridge: 1, crackB: 1, duration: .6, ease: 'power3.out' }, 42.05)
  .to(st, { sRot: -21, duration: 3.4, ease: 'sine.inOut' }, 42.7)
  .fromTo('#s_words div:nth-child(1)', { opacity: 0, x: 40 }, { opacity: 1, x: 0, duration: .3 }, 40.5)
  .fromTo('#s_words div:nth-child(2)', { opacity: 0, x: 40 }, { opacity: 1, x: 0, duration: .3 }, 41.8)
  .to('#s_words', { opacity: 0, duration: .4 }, 43.0)
  .fromTo('#s_date', { opacity: 0, x: -50 }, { opacity: 1, x: 0, duration: .6, ease: 'power3.out' }, 43.1)
  .to(st, { sY: 560, sRot: -33, duration: 2.6, ease: 'power2.in' }, 46.0)
  .to(st, { sq: 1.9, duration: 2.0, ease: 'power2.inOut' }, 46.8)
  .to('#shipL', { opacity: 0, duration: .6 }, 48.7);

/* ---------------- END ---------------- */
const eMen = $$('#e_men .man');
tl.to('#endL', { opacity: 1, duration: .55 }, 98.2)
  .to('#e_k', { opacity: 1, duration: .4 }, 98.6)
  .to(eMen.slice(0, 22), { opacity: 1, duration: .25, stagger: .036 }, 98.8)
  .to(eMen.slice(22), { opacity: 1, duration: .3, stagger: .05 }, 100.5)
  .fromTo('#e_big', { opacity: 0, scale: 1.12 }, { opacity: 1, scale: 1, duration: .6, ease: 'power3.out' }, 100.6)
  .to('#e_sub', { opacity: 1, duration: .5 }, 101.2)
  .to('#deep', { opacity: 1, duration: .9, ease: 'power1.inOut' }, 102.3)
  .fromTo('#d_txt', { opacity: 0, x: 40 }, { opacity: 1, x: 0, duration: .6, ease: 'power3.out' }, 103.9)
  .to(st, { depth: 3008, duration: 5.0, ease: 'power1.inOut' }, 103.9)
  .fromTo('#d_up', { opacity: 0, x: 40 }, { opacity: 1, x: 0, duration: .5, ease: 'power3.out' }, 105.9)
  .to('#lens', { opacity: 1, duration: .5 }, 109.6).to(st, { lensS: 1, duration: .7, ease: 'back.out(1.6)' }, 109.6)
  .to(st, { shine: 1, duration: 2.2, ease: 'power1.inOut' }, 110.4)
  .to('#black', { opacity: 1, duration: 1.3, ease: 'power1.in' }, 113.4);
// depth gauge
const gauge = $('#gauge'), GY0 = 110, GY1 = 905;
S('line', { x1: 260, y1: GY0, x2: 260, y2: GY1, stroke: 'rgba(255,255,255,.3)', 'stroke-width': 2 }, gauge);
for (let d = 0; d <= 3000; d += 500) { const y = GY0 + d / 3008 * (GY1 - GY0); S('line', { x1: 246, y1: y, x2: 274, y2: y, stroke: 'rgba(255,255,255,.5)', 'stroke-width': 2 }, gauge); const t = S('text', { x: 232, y: y + 7, 'text-anchor': 'end' }, gauge); t.textContent = d ? d.toLocaleString('en-US') + ' m' : 'SURFACE'; }

/* ---------------- SNOW ---------------- */
const cv = $('#snow'), ctx = cv.getContext('2d');
const flakes = Array.from({ length: 260 }, (_, i) => ({ x: rnd() * 1920, y: rnd() * 1080, r: .8 + rnd() * 2.4, vx: 20 + rnd() * 50, vy: 25 + rnd() * 60, a: .2 + rnd() * .6, ph: rnd() * 6.28, fast: i >= 130 }));
function snow(t, base, storm) {
  ctx.clearRect(0, 0, 1920, 1080);
  for (const f of flakes) {
    const al = f.a * (f.fast ? storm : base); if (al < .01) continue;
    const m = f.fast ? 6 : 1;
    const x = ((f.x + t * f.vx * m + Math.sin(t * .8 + f.ph) * 24) % 1960 + 1960) % 1960 - 20, y = ((f.y + t * f.vy * (f.fast ? 2.2 : 1)) % 1100) - 10;
    ctx.globalAlpha = al; ctx.fillStyle = '#fff'; ctx.beginPath();
    if (f.fast) ctx.ellipse(x, y, f.r * 3.2, f.r * .8, .32, 0, 6.3); else ctx.arc(x, y, f.r, 0, 6.3);
    ctx.fill();
  }
}

/* ---------------- RENDER (pure function of t) ---------------- */
const ptOn = (id, p) => { const r = R[id]; const q = r.mp.getPointAtLength(r.L * clamp(p)); return [q.x, q.y]; };
const fmt = n => Math.round(n).toLocaleString('en-US');
function render(t) {
  // skip painting layers that are fully covered
  $('#mapL').style.display = (t < 11.3 || (t > 39.05 && t < 48.65) || t > 98.8) ? 'none' : '';
  $('#hook').style.display = t > 12.05 ? 'none' : '';
  $('#shipL').style.display = (t < 38.45 || t > 49.35) ? 'none' : '';
  $('#endL').style.display = t < 98.15 ? 'none' : '';
  // camera
  const cam = camAt(t), k = cam.k, ik = 1 / k;
  map.setAttribute('viewBox', `${cam.c[0] - 960 * ik} ${cam.c[1] - 540 * ik} ${1920 * ik} ${1080 * ik}`);
  map.style.setProperty('--ik', ik);
  // routes
  for (const id in R) R[id].mp.setAttribute('stroke-dashoffset', R[id].L * (1 - clamp(st[id])));
  // moving head: last started leg
  let hp = PL.sgHarbor; for (const id of ['out', 'drift', 'camp', 'boats', 'caird', 'cross']) if (st[id] > 0) hp = ptOn(id, st[id]);
  head._p = hp; head4._p = ptOn('r4', st.r4);
  for (const g of fixes) g.setAttribute('transform', `translate(${g._p[0]},${g._p[1]}) scale(${ik})`);
  for (const r of rings) { const ph = (t * .75 + r._ph) % 1; r.setAttribute('r', 8 + 34 * ph); r.setAttribute('opacity', 1 - ph); }
  // hud
  const d = new Date(D0 + Math.round(st.day) * 864e5);
  $('#date').textContent = d.getUTCDate() + ' ' + MON[d.getUTCMonth()] + ' ' + d.getUTCFullYear();
  $('#day').textContent = 'DAY ' + String(Math.round(st.day)).padStart(3, '0');
  const fr = st.day / 634 * 100; $('#tlbar .fill').style.width = fr + '%'; $('#tlbar .knob').style.left = fr + '%';
  evEls.forEach(e => e.classList.toggle('on', st.day >= e._d - .5));
  // counters
  $('#h_num').textContent = '≈ ' + fmt(st.hnum);
  $('#n497').textContent = fmt(st.d497); $('#nm').textContent = fmt(st.caird * 800); $('#n22').textContent = fmt(st.n22);
  pips[0].className = t >= 91.45 ? 'x' : ''; pips[1].className = t >= 92.25 ? 'x' : ''; pips[2].className = t >= 93.05 ? 'x' : ''; pips[3].className = t >= 96.1 ? 'ok' : '';
  // hook ship
  $('#h_shipg').setAttribute('transform', `rotate(${st.hRot})`);
  // ship scene
  const sh = (t0, amp) => { const u = t - t0; return u > 0 && u < .7 ? amp * (1 - u / .7) ** 2 : 0; };
  const A = sh(40.85, 10) + sh(42.05, 14) + sh(46.0, 6);
  $('#s_shake').setAttribute('transform', `translate(${(Math.sin(t * 83) * A).toFixed(2)},${(Math.cos(t * 67) * A * .6).toFixed(2)})`);
  shipWrap.setAttribute('transform', `translate(960,${716 + st.sY}) scale(1.15) rotate(${st.sRot})`);
  $('#s_iceL').setAttribute('transform', `translate(${st.sq * 92},0)`); $('#s_iceR').setAttribute('transform', `translate(${-st.sq * 92},0)`);
  const ry = .35 + st.ridge * .95; $('#s_ridgeL').setAttribute('transform', `translate(0,750) scale(1,${ry}) translate(0,-750)`); $('#s_ridgeR').setAttribute('transform', `translate(0,750) scale(1,${ry}) translate(0,-750)`);
  for (const c of cracks) c.setAttribute('stroke-dashoffset', c._L * (1 - (c._g === 'A' ? st.crackA : st.crackB)));
  // depth scene
  const ry2 = GY0 + st.depth / 3008 * (GY1 - GY0);
  $('#rov').setAttribute('transform', `translate(260,${ry2})`);
  $('#rovbeam').setAttribute('opacity', .35 + .65 * clamp((st.depth - 1500) / 1200));
  $('#d_ship').setAttribute('opacity', .1 + .9 * clamp((st.depth - 2100) / 800));
  $('#d_num').textContent = fmt(st.depth); $('#d_ft').textContent = fmt(st.depth * 3.28084);
  $('#lens').setAttribute('transform', `translate(600,500) scale(${st.lensS})`);
  $('#brass').setAttribute('gradientTransform', `translate(${-480 + 960 * st.shine},0)`);
  // snow intensity per scene
  const ramp = (a, b) => clamp((t - a) / (b - a));
  const inShip = ramp(38.5, 39) * (1 - ramp(48.7, 49.3)), inMap = ramp(11.35, 12) * (1 - ramp(98.2, 98.75)), inDeep = ramp(102.3, 103.2);
  snow(t, (1 - inMap * .72) * (1 - inDeep * .55) * .9, inShip);
}
window.seek = t => { tl.seek(Math.min(t, DUR), false); render(t); };
window.seek(0);
