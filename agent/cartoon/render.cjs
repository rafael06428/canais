// usage: node render.cjs <ep_dir> long <f0> <f1> <out.mp4>  |  node render.cjs <ep_dir> short <k> <f0> <f1> <out.mp4>
//        node render.cjs <ep_dir> shots <outdir> <t1> <t2> ...   |  node render.cjs <ep_dir> thumb <out.jpg>
//        node render.cjs <ep_dir> sshots <k> <outdir> <t1> ...
const { chromium } = require('playwright'); const { spawn } = require('child_process'); const path = require('path'); const fs = require('fs');
const [ED, MODE, ...A] = process.argv.slice(2); const FPS = 30;
(async () => {
  const b = await chromium.launch();
  const short = MODE === 'short' || MODE === 'sshots';
  const page = await b.newPage({ viewport: short ? { width: 1080, height: 1920 } : { width: MODE === 'thumb' ? 1280 : 1920, height: MODE === 'thumb' ? 720 : 1080 } });
  page.on('pageerror', e => console.log('PAGEERR', e.message));
  await page.goto('file://' + path.resolve(ED) + '/cartoon/page.html?mode=' + (short ? 'short' : 'long') + (MODE === 'thumb' ? '&w=1280' : ''));
  if (MODE === 'thumb') { await page.evaluate(() => thumb()); await page.screenshot({ path: A[0], type: 'jpeg', quality: 92 }); }
  else if (MODE === 'shots' || MODE === 'sshots') {
    const k = MODE === 'sshots' ? +A.shift() : null; const out = A.shift(); fs.mkdirSync(out, { recursive: true });
    for (const t of A.map(Number)) { await page.evaluate(([k, t]) => k == null ? seek(t) : seekShort(k, t), [k, t]); await page.screenshot({ path: `${out}/f_${String(t.toFixed(2)).padStart(8, '0')}.jpg`, type: 'jpeg', quality: 80 }); }
  } else {
    const k = MODE === 'short' ? +A.shift() : null; const f0 = +A[0], f1 = +A[1], out = A[2];
    const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-c:v', 'mjpeg', '-framerate', String(FPS), '-i', '-', '-vf', 'format=yuv420p', '-c:v', 'libx264', '-preset', 'fast', '-crf', '20', '-r', String(FPS), out], { stdio: ['pipe', 'inherit', 'inherit'] });
    const done = new Promise(r => ff.on('close', r));
    for (let f = f0; f < f1; f++) {
      await page.evaluate(([k, t]) => k == null ? seek(t) : seekShort(k, t), [k, f / FPS]);
      const buf = await page.screenshot({ type: 'jpeg', quality: 90 });
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
      if ((f - f0) % 900 === 0) console.log(out, f - f0, '/', f1 - f0);
    }
    ff.stdin.end(); console.log('done', out, await done);
  }
  await b.close();
})();
