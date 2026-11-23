// builds <name>_map.js: window.MAP = { land, grat, routes, places }
import fs from 'fs';
import { geoMercator, geoPath, geoGraticule } from 'd3-geo';
import { feature } from 'topojson-client';
export function build(name, { center, scale, translate = [960, 540], res = '50m', routes = {}, places = {}, gratStep = [2, 2], pad = 700 }) {
  const proj = geoMercator().center(center).scale(scale).translate(translate).clipExtent([[-pad, -pad], [1920 + pad, 1080 + pad]]).precision(0.3);
  const path = geoPath(proj), r2 = s => (s || '').replace(/(\d+\.\d\d)\d+/g, '$1');
  const topo = JSON.parse(fs.readFileSync(`node_modules/world-atlas/land-${res}.json`));
  const land = r2(path(feature(topo, topo.objects.land)));
  const grat = r2(path(geoGraticule().step(gratStep)()));
  const spline = (pts, tension = 0.5) => { const p = pts.map(c => proj(c)); let d = `M${p[0][0].toFixed(2)},${p[0][1].toFixed(2)}`;
    for (let i = 0; i < p.length - 1; i++) { const p0 = p[i - 1] || p[i], p1 = p[i], p2 = p[i + 1], p3 = p[i + 2] || p2;
      d += `C${(p1[0] + (p2[0] - p0[0]) * tension / 3).toFixed(2)},${(p1[1] + (p2[1] - p0[1]) * tension / 3).toFixed(2)} ${(p2[0] - (p3[0] - p1[0]) * tension / 3).toFixed(2)},${(p2[1] - (p3[1] - p1[1]) * tension / 3).toFixed(2)} ${p2[0].toFixed(2)},${p2[1].toFixed(2)}`; } return d; };
  const R = {}, P = {}; for (const k in routes) R[k] = spline(routes[k]); for (const k in places) P[k] = proj(places[k]).map(v => +v.toFixed(1));
  fs.writeFileSync(`${name}_map.js`, 'window.MAP=' + JSON.stringify({ land, grat, routes: R, places: P }) + ';\n');
  console.log(name, 'land', (land.length / 1024 | 0) + 'KB', JSON.stringify(P));
}
