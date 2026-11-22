// Precomputes the map geometry (projected to a 1920x1080 "home" view) into data.js
import fs from 'fs';
import { geoStereographic, geoPath, geoGraticule } from 'd3-geo';
import { feature } from 'topojson-client';
import { Delaunay } from 'd3-delaunay';

const W = 1920, H = 1080;
const proj = geoStereographic().rotate([42, 66]).translate([960, 575]).scale(4200)
  .clipExtent([[-900, -500], [W + 900, H + 900]]).precision(0.3);
const path = geoPath(proj);
const r1 = s => s.replace(/(\d+\.\d\d)\d+/g, '$1');

const mk = ext => geoStereographic().rotate([42, 66]).translate([960, 575]).scale(4200).clipExtent(ext).precision(0.3);
const topo50 = JSON.parse(fs.readFileSync('node_modules/world-atlas/land-50m.json'));
const landD = r1(path(feature(topo50, topo50.objects.land)));
const topo = JSON.parse(fs.readFileSync('node_modules/world-atlas/land-10m.json'));
const land10 = feature(topo, topo.objects.land);
const box = (l0, l1, a0, a1) => { const q = [[l0, a0], [l1, a0], [l0, a1], [l1, a1], [(l0 + l1) / 2, a0], [(l0 + l1) / 2, a1]].map(c => proj(c)); const xs = q.map(c => c[0]), ys = q.map(c => c[1]); return [[Math.floor(Math.min(...xs)), Math.floor(Math.min(...ys))], [Math.ceil(Math.max(...xs)), Math.ceil(Math.max(...ys))]]; };
const boxes = [[-56.6, -53.3, -61.9, -60.6], [-39, -35, -55.3, -53.3]];
const rects = boxes.map(b => box(...b));
const polys = land10.features ? land10.features.flatMap(f => f.geometry.coordinates) : land10.geometry.coordinates;
const detail = boxes.map(([l0, l1, a0, a1]) => {
  const sel = polys.filter(pg => { const r = pg[0]; if (r.length > 4000) return false; const cx = r.reduce((s, c) => s + c[0], 0) / r.length, cy = r.reduce((s, c) => s + c[1], 0) / r.length; return cx > l0 && cx < l1 && cy > a0 && cy < a1; });
  console.log('detail polygons', sel.length);
  return r1(path({ type: 'MultiPolygon', coordinates: sel }));
});
const grat = r1(path(geoGraticule().step([10, 5]).extent([[-130, -89], [40, -40]])()));

const P = (lon, lat) => proj([lon, lat]).map(v => +v.toFixed(2));

// Catmull-Rom spline through projected points -> cubic bezier path
function spline(pts, tension = 0.5) {
  const p = pts.map(([a, b]) => proj([a, b]));
  let d = `M${p[0][0].toFixed(2)},${p[0][1].toFixed(2)}`;
  for (let i = 0; i < p.length - 1; i++) {
    const p0 = p[i - 1] || p[i], p1 = p[i], p2 = p[i + 1], p3 = p[i + 2] || p2;
    const c1 = [p1[0] + (p2[0] - p0[0]) * tension / 3, p1[1] + (p2[1] - p0[1]) * tension / 3];
    const c2 = [p2[0] - (p3[0] - p1[0]) * tension / 3, p2[1] - (p3[1] - p1[1]) * tension / 3];
    d += `C${c1[0].toFixed(2)},${c1[1].toFixed(2)} ${c2[0].toFixed(2)},${c2[1].toFixed(2)} ${p2[0].toFixed(2)},${p2[1].toFixed(2)}`;
  }
  return d;
}

const routes = {
  out: spline([[-36.5, -54.28], [-30, -57], [-22, -59.8], [-18, -63], [-17, -67], [-17.5, -70.5], [-20, -72.5], [-24, -74.5], [-28, -76], [-31.5, -76.57]]),
  drift: spline([[-31.5, -76.57], [-35, -77.0], [-39, -76.3], [-43.5, -75.2], [-47, -73.3], [-49.5, -71.3], [-51, -69.6], [-51.5, -69.08], [-52.44, -68.65]]),
  camp: spline([[-52.44, -68.65], [-52.8, -67.5], [-53.5, -66], [-54.3, -64.5], [-54.2, -63], [-54.0, -61.93]]),
  boats: spline([[-54.0, -61.93], [-53.6, -61.5], [-54.2, -61.2], [-54.87, -61.1]]),
  caird: spline([[-54.87, -61.1], [-52.5, -59.2], [-47.5, -57.2], [-42, -55.4], [-37.28, -54.15]]),
  cross: spline([[-37.28, -54.15], [-37.16, -54.115], [-37.02, -54.165], [-36.86, -54.13], [-36.71, -54.16]]),
  plan: spline([[-35, -77.9], [-36, -81], [-40, -85], [-60, -88.5]]),
  // rescue attempts toward Elephant Island
  r1: spline([[-36.5, -54.28], [-41, -56.2], [-46.5, -58.2], [-50.6, -59.5]]),
  r2: spline([[-57.85, -51.7], [-57.3, -54.5], [-56.4, -57.5], [-55.6, -59.7]]),
  r3: spline([[-70.9, -53.15], [-67.5, -55.8], [-63.5, -58], [-59.8, -59.5]]),
  r4: spline([[-70.9, -53.15], [-66.5, -57], [-60.5, -59.8], [-54.87, -61.1]]),
};

const places = {
  sg: P(-36.6, -54.35), sgHarbor: P(-36.5, -54.28), haakon: P(-37.28, -54.15), stromness: P(-36.71, -54.16),
  ei: P(-54.87, -61.1), trapped: P(-31.5, -76.57), sink: P(-52.44, -68.65), launch: P(-54.0, -61.93),
  vahsel: P(-35, -77.9), weddell: P(-40, -70), antarctica: P(-28, -80.6), peninsula: P(-64.5, -69.5),
  samerica: P(-69.5, -50.2), falklands: P(-59, -51.75), stanley: P(-57.85, -51.7), punta: P(-70.9, -53.15),
  drake: P(-63, -58.3), scotia: P(-44, -57.6), r1end: P(-50.6, -59.5), r2end: P(-55.6, -59.7), r3end: P(-59.8, -59.5),
};

// Pack ice: tessellated floes inside a hand-drawn extent
const ice = [[-57, -63.4], [-54.6, -61.75], [-48, -60.7], [-40, -60.6], [-30, -61.6], [-22, -63.5], [-16, -66.5], [-12, -70], [-12, -73.5], [-18, -77], [-30, -80], [-50, -81], [-66, -77], [-64, -70], [-61, -66]];
const poly = ice.map(([a, b]) => proj([a, b]));
const inside = (x, y) => { let c = false; for (let i = 0, j = poly.length - 1; i < poly.length; j = i++) { const [xi, yi] = poly[i], [xj, yj] = poly[j]; if ((yi > y) !== (yj > y) && x < (xj - xi) * (y - yi) / (yj - yi) + xi) c = !c; } return c; };
let seed = 7; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
const xs = poly.map(p => p[0]), ys = poly.map(p => p[1]);
const bx = [Math.min(...xs) - 40, Math.min(...ys) - 40, Math.max(...xs) + 40, Math.max(...ys) + 40];
const sites = []; const step = 20;
for (let y = bx[1]; y < bx[3]; y += step) for (let x = bx[0]; x < bx[2]; x += step) sites.push([x + (rnd() - 0.5) * step * 1.5, y + (rnd() - 0.5) * step * 1.5]);
const vor = Delaunay.from(sites).voronoi(bx);
const fringeY = proj([-45, -64.6])[1];
let floes = '', fringe = '';
sites.forEach((s, i) => {
  if (!inside(s[0], s[1])) return;
  const cell = vor.cellPolygon(i); if (!cell) return;
  const cx = cell.reduce((a, p) => a + p[0], 0) / cell.length, cy = cell.reduce((a, p) => a + p[1], 0) / cell.length;
  const k = 0.80 + rnd() * 0.12;
  const d = 'M' + cell.slice(0, -1).map(p => `${(cx + (p[0] - cx) * k).toFixed(2)},${(cy + (p[1] - cy) * k).toFixed(2)}`).join('L') + 'Z';
  // distance to launch point decides the "breaking up" fringe
  if (s[1] < fringeY) fringe += d; else floes += d;
});

fs.writeFileSync('data.js', 'window.MAP=' + JSON.stringify({ land: landD, detail, rects, grat, routes, places, floes, fringe }) + ';\n');
console.log('land', (landD.length / 1024 | 0) + 'KB', 'detail', detail.map(d => d.length / 1024 | 0), JSON.stringify(rects), 'floes', (floes.length / 1024 | 0) + 'KB', 'fringe', (fringe.length / 1024 | 0) + 'KB');
console.log(places);
