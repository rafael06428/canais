// usage: OUT=dir node shot.cjs v4 t1 t2 ...
const { chromium } = require('playwright'); const fs = require('fs');
(async () => { const name = process.argv[2], times = process.argv.slice(3).map(Number), out = process.env.OUT || 'shots'; fs.mkdirSync(out, { recursive: true });
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  p.on('console', m => console.log('console:', m.text())); p.on('pageerror', e => console.log('ERR', e.message));
  await p.goto(`file:///home/claude/sus/${name}.html`); await p.evaluate(() => document.fonts.ready); let tot = 0;
  for (const t of times) { const t0 = Date.now(); await p.evaluate(t => window.seek(t), t); await p.screenshot({ path: `${out}/f_${t}.jpg`, type: 'jpeg', quality: 80 }); tot += Date.now() - t0; }
  console.log('avg ms/frame', Math.round(tot / times.length)); await b.close(); })();
