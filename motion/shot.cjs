const { chromium } = require('playwright');
(async () => {
const times = process.argv.slice(2).map(Number);
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
p.on('console', m => console.log('console:', m.text())); p.on('pageerror', e => console.log('ERR', e.message));
await p.goto('file:///home/claude/test/index.html'); await p.evaluate(() => document.fonts.ready);
for (const t of times) { const t0 = Date.now(); await p.evaluate(t => window.seek(t), t); await p.screenshot({ path: `${process.env.OUT||"shots"}/f_${String(t).padStart(6, '0')}.jpg`, type: 'jpeg', quality: 80 }); console.log(t, Date.now() - t0, 'ms'); }
await b.close();
})();
