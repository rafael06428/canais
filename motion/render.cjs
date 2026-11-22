// Renders each scene to its own mp4 (JPEG frames piped to ffmpeg), 2 workers.
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const fs = require('fs');
const FPS = 30, DUR = 114.9, TOTAL = Math.round(DUR * FPS);
const cuts = [0, 12.0, 24.5, 35.1, 42.0, 49.2, 57.0, 65.9, 73.0, 81.3, 89.5, 98.2, 106.0, DUR].map(t => Math.round(t * FPS)); cuts[cuts.length - 1] = TOTAL;
const only = process.argv.slice(2).map(Number);
const segs = []; for (let i = 0; i < cuts.length - 1; i++) if (!only.length || only.includes(i)) segs.push({ i, f0: cuts[i], f1: cuts[i + 1] });
fs.mkdirSync('scenes', { recursive: true });
(async () => {
  const browser = await chromium.launch();
  const queue = segs.slice(); const t00 = Date.now();
  async function worker(w) {
    const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
    page.on('pageerror', e => console.log('PAGEERR', e.message));
    await page.goto('file:///home/claude/test/index.html'); await page.evaluate(() => document.fonts.ready);
    while (queue.length) {
      const s = queue.shift(); const name = `scenes/s${String(s.i).padStart(2, '0')}`; const t0 = Date.now();
      const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-c:v', 'mjpeg', '-framerate', String(FPS), '-i', '-',
        '-vf', 'scale=in_range=pc:in_color_matrix=bt601:out_range=tv:out_color_matrix=bt709,format=yuv420p',
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '17', '-pix_fmt', 'yuv420p', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709', '-r', String(FPS), name + '.tmp.mp4'], { stdio: ['pipe', 'inherit', 'inherit'] });
      const done = new Promise(r => ff.on('close', r));
      for (let f = s.f0; f < s.f1; f++) {
        await page.evaluate(t => window.seek(t), f / FPS);
        const buf = await page.screenshot({ type: 'jpeg', quality: 92 });
        if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
      }
      ff.stdin.end(); const code = await done;
      if (code === 0) fs.renameSync(name + '.tmp.mp4', name + '.mp4');
      console.log(`w${w} seg ${s.i} frames ${s.f1 - s.f0} exit ${code} ${((Date.now() - t0) / 1000).toFixed(0)}s (total ${((Date.now() - t00) / 1000).toFixed(0)}s)`);
    }
    await page.close();
  }
  await Promise.all([worker(0), worker(1)]);
  await browser.close(); console.log('RENDER DONE');
})();
