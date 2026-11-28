// Renderiza a página quadro a quadro (30 fps) em 2 workers, cada um gera um mp4; depois concat.
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const FPS = 30, WORKERS = 2;
(async () => {
  const b = await chromium.launch();
  const probe = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  await probe.goto('file://' + __dirname + '/index.html'); await probe.waitForTimeout(400);
  const DUR = await probe.evaluate(() => window.DUR); await probe.close();
  const total = Math.ceil(DUR * FPS);
  const per = Math.ceil(total / WORKERS);
  const jobs = [];
  for (let w = 0; w < WORKERS; w++) {
    jobs.push((async () => {
      const a = w * per, z = Math.min(total, a + per);
      const pg = await b.newPage({ viewport: { width: 1920, height: 1080 } });
      pg.on('pageerror', e => console.log('ERR', e.message));
      await pg.goto('file://' + __dirname + '/index.html'); await pg.waitForTimeout(400);
      const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', '-r', String(FPS), `part${w}.mp4`]);
      for (let f = a; f < z; f++) {
        await pg.evaluate(t => window.seek(t), f / FPS);
        const buf = await pg.screenshot({ type: 'jpeg', quality: 92 });
        if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
        if ((f - a) % 150 === 0) console.log(`w${w} ${f - a}/${z - a}`);
      }
      ff.stdin.end(); await new Promise(r => ff.on('close', r)); await pg.close();
    })());
  }
  await Promise.all(jobs); await b.close();
  require('fs').writeFileSync('list.txt', [...Array(WORKERS).keys()].map(w => `file 'part${w}.mp4'`).join('\n') + '\n');
  console.log('done', total, DUR);
})();
