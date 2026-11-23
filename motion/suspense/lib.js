/* Shared engine for the suspense tests. Everything is a pure function of time: window.seek(t).
   No animation library: tracks (keyframed numbers) + render hooks. */
const NS = 'http://www.w3.org/2000/svg';
const $ = s => document.querySelector(s), $$ = s => [...document.querySelectorAll(s)];
const S = (tag, attrs = {}, parent) => { const e = document.createElementNS(NS, tag); for (const k in attrs) e.setAttribute(k, attrs[k]); if (parent) parent.appendChild(e); return e; };
const H = (tag, cls, html, parent) => { const e = document.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html; if (parent) parent.appendChild(e); return e; };
const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
const lerp = (a, b, u) => a + (b - a) * u;
const E = {
  lin: u => u, in2: u => u * u, out2: u => 1 - (1 - u) ** 2, io2: u => u < .5 ? 2 * u * u : 1 - 2 * (1 - u) ** 2,
  out3: u => 1 - (1 - u) ** 3, in3: u => u ** 3, io3: u => u < .5 ? 4 * u ** 3 : 1 - 4 * (1 - u) ** 3,
  sine: u => .5 - .5 * Math.cos(Math.PI * u), back: u => { const c = 1.9; return 1 + (c + 1) * (u - 1) ** 3 + c * (u - 1) ** 2; },
};
let _seed = 7; const rnd = () => (_seed = (_seed * 16807) % 2147483647) / 2147483647; const reseed = s => _seed = s;
const fmt = n => Math.round(n).toLocaleString('en-US');

/* timing from the narration */
const TM = window.TIMING, DUR = TM.dur; window.DUR = DUR;
const _norm = s => s.toLowerCase().replace(/[^a-z0-9]/g, '');
const B = i => TM.blocks[i][0], BE = i => TM.blocks[i][1];
function W(b, word, nth = 0) { // start time of the nth occurrence of `word` in block b
  let n = 0; for (const [w, t0, , bi] of TM.words) if (bi === b && _norm(w).startsWith(_norm(word))) { if (n++ === nth) return t0; }
  console.log('WORD NOT FOUND', b, word, nth); return B(b);
}

/* tracks: st.name = keyframed value */
const st = {}, _tracks = [], _hooks = [];
function track(name, v0, keys) { // keys: [[t0, dur, v1, ease?], ...] in time order
  st[name] = v0; _tracks.push({ name, v0, keys: keys.map(([t0, d, v1, e]) => ({ t0, d, v1, e: E[e || 'io2'] })) });
}
function _evalTracks(t) {
  for (const tr of _tracks) { let v = tr.v0; for (const k of tr.keys) { if (t <= k.t0) break; const u = k.d <= 0 ? 1 : clamp((t - k.t0) / k.d); v = lerp(v, k.v1, k.e(u)); if (u < 1) break; } st[tr.name] = v; }
}
const onRender = fn => _hooks.push(fn);
window.seek = t => { t = Math.min(t, DUR); _evalTracks(t); for (const f of _hooks) f(t); };
const ramp = (t, a, b) => clamp((t - a) / (b - a));

/* scenes and elements */
function scene(sel, tin, tout, fi = .5, fo = .5) { // layer visible in [tin, tout]; display:none when hidden
  const el = typeof sel === 'string' ? $(sel) : sel;
  onRender(t => { const a = (fi <= 0 ? (t >= tin ? 1 : 0) : clamp((t - tin) / fi)) * (1 - (fo <= 0 ? (t >= tout ? 1 : 0) : clamp((t - tout) / fo))); el.style.opacity = a; el.style.display = a <= 0 ? 'none' : ''; });
  return el;
}
function show(el, tin, tout = 1e9, o = {}) { // fade/slide an element in and out
  if (typeof el === 'string') el = $(el);
  const { dx = 0, dy = 0, din = .55, dout = .35, s0 = 1, max = 1, ease = 'out3' } = o;
  onRender(t => { const a = E[ease](clamp((t - tin) / din)), b = clamp((t - tout) / dout); el.style.opacity = max * clamp(a) * (1 - b); if (dx || dy || s0 !== 1) el.style.transform = `translate(${dx * (1 - a)}px,${dy * (1 - a)}px) scale(${s0 + (1 - s0) * a})`; });
  return el;
}
function showS(el, tin, tout = 1e9, din = .5, dout = .35, max = 1) { // opacity for SVG nodes
  if (typeof el === 'string') el = $(el);
  onRender(t => el.setAttribute('opacity', max * clamp((t - tin) / din) * (1 - clamp((t - tout) / dout)))); return el;
}
function card(parent, y, o, tin, tout, x = 110) {
  const html = (o.k ? `<div class="k">${o.k}</div>` : '') + (o.t ? `<div class="t">${o.t}</div>` : '') + (o.html || '') + (o.s ? `<div class="s">${o.s}</div>` : '');
  const el = H('div', 'card' + (o.cls ? ' ' + o.cls : ''), html, typeof parent === 'string' ? $(parent) : parent); el.style.top = y + 'px'; el.style.left = x + 'px';
  show(el, tin, tout, { dx: -50 }); return el;
}
function typer(el, text, t0, dur, caret = false) { // typewriter
  if (typeof el === 'string') el = $(el);
  onRender(t => { const n = Math.floor(text.length * clamp((t - t0) / dur)); el.textContent = text.slice(0, n) + (caret && t > t0 - .3 && (n < text.length || Math.floor(t * 2.5) % 2 === 0) ? '▌' : ''); });
  return el;
}
function counter(el, name, f = fmt) { if (typeof el === 'string') el = $(el); onRender(() => el.textContent = f(st[name])); }
function draw(path, name) { // stroke draw-on driven by track `name` (0..1)
  if (typeof path === 'string') path = $(path);
  const L = path.getTotalLength(); path.setAttribute('stroke-dasharray', L + ' ' + L);
  onRender(() => path.setAttribute('stroke-dashoffset', L * (1 - clamp(st[name])))); return path;
}
function drawT(path, t0, dur, ease = 'io2') { if (typeof path === 'string') path = $(path); const L = path.getTotalLength(); path.setAttribute('stroke-dasharray', L + ' ' + L); onRender(t => path.setAttribute('stroke-dashoffset', L * (1 - E[ease](clamp((t - t0) / dur))))); return path; }
function stamp(el, t0, rot = -8) { // rubber-stamp slam
  if (typeof el === 'string') el = $(el);
  onRender(t => { const u = clamp((t - t0) / .22); el.style.opacity = u > 0 ? 1 : 0; el.style.transform = `rotate(${rot}deg) scale(${lerp(2.4, 1, E.out3(u))})`; }); return el;
}
function shakeOf(t, hits) { let a = 0; for (const [t0, amp, d = .6] of hits) { const u = t - t0; if (u > 0 && u < d) a += amp * (1 - u / d) ** 2; } return [Math.sin(t * 83) * a, Math.cos(t * 67) * a * .6]; }
function fadeBlack(t0, dur) { const el = $('#black'); onRender(t => el.style.opacity = E.in2(clamp((t - t0) / dur))); }

/* particles canvas (#fx): snow | rain | dust, alpha(t) */
function particles(mode, alphaFn, n = 160) {
  const cv = $('#fx'), ctx = cv.getContext('2d'); reseed(99);
  const P = Array.from({ length: n }, () => ({ x: rnd() * 1920, y: rnd() * 1080, r: .7 + rnd() * 2.2, vx: rnd(), vy: rnd(), a: .2 + rnd() * .6, ph: rnd() * 6.28 }));
  onRender(t => {
    ctx.clearRect(0, 0, 1920, 1080); const A = alphaFn(t); if (A <= .005) return;
    for (const p of P) {
      ctx.globalAlpha = p.a * A; ctx.fillStyle = ctx.strokeStyle = '#fff';
      if (mode === 'rain') { const x = ((p.x - t * (260 + p.vx * 160)) % 1980 + 1980) % 1980 - 30, y = (p.y + t * (1100 + p.vy * 500)) % 1120 - 20; ctx.lineWidth = 1.4; ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x - 9, y + 34); ctx.stroke(); }
      else if (mode === 'snow') { const x = ((p.x + t * (20 + p.vx * 50) + Math.sin(t * .8 + p.ph) * 24) % 1960 + 1960) % 1960 - 20, y = (p.y + t * (25 + p.vy * 60)) % 1100 - 10; ctx.beginPath(); ctx.arc(x, y, p.r, 0, 6.3); ctx.fill(); }
      else { const x = p.x + Math.sin(t * .3 + p.ph) * 30, y = ((p.y - t * (6 + p.vy * 12)) % 1100 + 1100) % 1100 - 10; ctx.beginPath(); ctx.arc(x, y, p.r * .8, 0, 6.3); ctx.fill(); }
    }
  });
}

/* map camera: animates an svg viewBox; .fix groups keep screen size; CSS var --ik = 1/zoom */
function makeCam(svg, c0, k0) {
  const segs = []; let end = { c: c0, k: k0 }; const fixes = [];
  const cam = {
    to(t0, dur, target, k, ox = 0, oy = 0, ease = 'io2') {
      const prev = end, c1 = [target[0] - ox / k, target[1] - oy / k]; let F, s0, s1;
      if (k >= prev.k) { F = target; s0 = [(F[0] - prev.c[0]) * prev.k, (F[1] - prev.c[1]) * prev.k]; s1 = [ox, oy]; }
      else { F = prev.c; s0 = [0, 0]; s1 = [(F[0] - c1[0]) * k, (F[1] - c1[1]) * k]; }
      segs.push({ t0, dur, F, s0, s1, z0: Math.log2(prev.k), z1: Math.log2(k), e: E[ease] }); end = { c: c1, k };
    },
    at(t) { let s = null; for (const g of segs) { if (g.t0 <= t) s = g; else break; } if (!s) return { c: c0, k: k0 }; const u = s.e(clamp((t - s.t0) / s.dur)), k = 2 ** lerp(s.z0, s.z1, u); return { c: [s.F[0] - lerp(s.s0[0], s.s1[0], u) / k, s.F[1] - lerp(s.s0[1], s.s1[1], u) / k], k }; },
    fix(pt, parent) { const g = S('g', {}, parent); g._p = pt; fixes.push(g); return g; },
    k: k0,
  };
  cam._hook = t => { const { c, k } = cam.at(t), ik = 1 / k; cam.k = k; svg.setAttribute('viewBox', `${c[0] - 960 * ik} ${c[1] - 540 * ik} ${1920 * ik} ${1080 * ik}`); svg.style.setProperty('--ik', ik); for (const g of fixes) g.setAttribute('transform', `translate(${g._p[0]},${g._p[1]}) scale(${ik})`); };
  onRender(cam._hook); cam.last = () => { _hooks.push(_hooks.splice(_hooks.indexOf(cam._hook), 1)[0]); };
  return cam;
}
const ptAt = (path, p) => { const q = path.getPointAtLength(path.getTotalLength() * clamp(p)); return [q.x, q.y]; };
