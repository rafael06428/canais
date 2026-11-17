// YouTube Studio uploader, run inside studio.youtube.com (Claude's built-in browser).
// Paste this file, then start a job in the background and poll it (the JS tool times out at ~50 s):
//   window.__res = null; ytUpload(JOB).then(r => window.__res = r).catch(e => window.__res = 'ERR ' + e); 'started'
//   ... later: window.__state + ' | ' + window.__res
// JOB = {files: [raw urls, joined in order], name, title, description, tags: [..], thumb: url|null}
// Publishes as PUBLIC, not made for kids, altered/synthetic content = YES, no paid promotion.
window.ytUpload = async (job) => {
  const s = ms => new Promise(r => setTimeout(r, ms));
  const st = x => { window.__state = x; };
  st('fetching');
  const blobs = [];
  for (const u of job.files) { const r = await fetch(u); if (!r.ok) throw 'fetch ' + r.status + ' ' + u; blobs.push(await r.blob()); }
  const file = new File(blobs, job.name, { type: 'video/mp4' });
  st('opening dialog ' + Math.round(file.size / 1e6) + 'MB');
  if (!document.querySelector('ytcp-uploads-file-picker input[type=file]')) {
    document.querySelector('#upload-icon, ytcp-button#create-icon')?.click(); await s(800);
    [...document.querySelectorAll('tp-yt-paper-item, ytcp-text-menu tp-yt-paper-item')].find(e => /Enviar v|Upload v/.test(e.innerText))?.click();
  }
  let inp; for (let i = 0; i < 30 && !(inp = document.querySelector('ytcp-uploads-file-picker input[type=file]')); i++) await s(500);
  if (!inp) throw 'no file input';
  const dt = new DataTransfer(); dt.items.add(file); inp.files = dt.files; inp.dispatchEvent(new Event('change', { bubbles: true }));
  let d; for (let i = 0; i < 60; i++) { d = document.querySelector('ytcp-uploads-dialog'); if (d && d.querySelectorAll('#textbox[contenteditable=true]').length >= 2) break; await s(500); }
  await s(1500); st('details');
  const boxes = [...d.querySelectorAll('#textbox[contenteditable=true]')];
  const set = (el, t) => { el.focus(); document.execCommand('selectAll', false, null); document.execCommand('insertText', false, t); el.dispatchEvent(new Event('input', { bubbles: true })); };
  set(boxes[0], job.title.slice(0, 100)); set(boxes[1], job.description.slice(0, 4900)); await s(500);
  if (job.thumb) {
    try {
      const tb = await (await fetch(job.thumb)).blob();
      const ti = d.querySelector('ytcp-thumbnails-compact-editor-uploader input[type=file], #file-loader');
      if (ti && !ti.disabled) { const t2 = new DataTransfer(); t2.items.add(new File([tb], 'thumb.jpg', { type: 'image/jpeg' })); ti.files = t2.files; ti.dispatchEvent(new Event('change', { bubbles: true })); await s(2500); }
    } catch (e) { console.log('thumb skipped', e); }
  }
  d.querySelector('tp-yt-paper-radio-button[name=VIDEO_MADE_FOR_KIDS_NOT_MFK]')?.click();
  d.querySelector('#toggle-button')?.click(); await s(1200);
  for (const n of ['VIDEO_HAS_ALTERED_CONTENT_YES', 'VIDEO_PAID_PRODUCT_PLACEMENT_NO']) d.querySelector(`tp-yt-paper-radio-button[name=${n}]`)?.click();
  if (job.tags && job.tags.length) {
    const ti = d.querySelector('ytcp-form-input-container#tags-container input, #tags-container input#text-input, input[aria-label*="Tags"], input[aria-label*="tags"]');
    if (ti) { ti.focus(); document.execCommand('insertText', false, job.tags.join(',') + ','); ti.dispatchEvent(new Event('input', { bubbles: true })); await s(400); }
  }
  await s(500); st('steps');
  for (let i = 0; i < 3; i++) { d.querySelector('#next-button').click(); await s(1800); }
  d.querySelector('tp-yt-paper-radio-button[name=PUBLIC]').click(); await s(800);
  st('uploading');
  const done = d.querySelector('#done-button');
  for (let i = 0; i < 1800 && done.getAttribute('aria-disabled') === 'true'; i++) await s(1000);
  const link = [...d.querySelectorAll('a')].map(a => a.href).find(h => /shorts\/|youtu\.be\//.test(h)) || '';
  done.click(); await s(3000);
  document.querySelector('ytcp-uploads-still-processing-dialog #close-button, ytcp-video-share-dialog #close-button')?.click();
  st('done');
  return link;
};
'ytUpload ready';
