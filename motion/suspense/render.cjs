// usage: node render.cjs v4   -> scenes_v4/sNN.mp4 (2 workers, 300-frame chunks)
const { chromium } = require('playwright'); const { spawn } = require('child_process'); const fs = require('fs');
const name = process.argv[2], FPS = 30, CH = 300;
const DUR = JSON.parse(fs.readFileSync(`${name}_voice.json`)).dur, TOTAL = Math.round(DUR * FPS);
const dir = `scenes_${name}`; fs.mkdirSync(dir, { recursive: true });
const segs = []; for (let f = 0, i = 0; f < TOTAL; f += CH, i++) segs.push({ i, f0: f, f1: Math.min(TOTAL, f + CH) });
(async () => {
  const browser = await chromium.launch(); const queue = segs.slice(); const t00 = Date.now();
  async function worker(w) {
    const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
    page.on('pageerror', e => console.log('PAGEERR', e.message));
    await page.goto(`file:///home/claude/sus/${name}.html`); await page.evaluate(() => document.fonts.ready);
    while (queue.length) {
      const s = queue.shift(); const out = `${dir}/s${String(s.i).padStart(2, '0')}`;
      const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-c:v', 'mjpeg', '-framerate', String(FPS), '-i', '-',
        '-vf', 'scale=in_range=pc:in_color_matrix=bt601:out_range=tv:out_color_matrix=bt709,format=yuv420p',
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '18', '-pix_fmt', 'yuv420p', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709', '-r', String(FPS), out + '.tmp.mp4'], { stdio: ['pipe', 'inherit', 'inherit'] });
      const done = new Promise(r => ff.on('close', r));
      for (let f = s.f0; f < s.f1; f++) { await page.evaluate(t => window.seek(t), f / FPS); const buf = await page.screenshot({ type: 'jpeg', quality: 92 }); if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r)); }
      ff.stdin.end(); const code = await done; if (code === 0) fs.renameSync(out + '.tmp.mp4', out + '.mp4');
      console.log(`w${w} seg ${s.i} exit ${code} total ${((Date.now() - t00) / 1000).toFixed(0)}s`);
    }
    await page.close();
  }
  await Promise.all([worker(0), worker(1)]); await browser.close(); console.log('RENDER DONE', name, TOTAL, 'frames');
})();
