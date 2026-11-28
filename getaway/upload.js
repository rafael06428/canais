// The Getaway Case: YouTube Studio uploader (copy of agent/upload.js + scheduling), run inside studio.youtube.com.
// job.publish_at = 'YYYY-MM-DD HH:MM' (Brasília) schedules the video (Programar); null publishes now.
// Paste this file, then start a job in the background and poll it (the JS tool times out at ~50 s):
//   window.__res = null; ytUpload(JOB).then(r => window.__res = r).catch(e => window.__res = 'ERR ' + e); 'started'
//   ... later: window.__state + ' | ' + window.__res
// JOB = {files: [raw urls, joined in order], name, title, description, tags: [..], thumb: url|null}
// Publishes as PUBLIC, not made for kids, altered/synthetic content = YES, no paid promotion.
window.gcUpload = async (job) => {
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
  await s(4000); st('details');   // YouTube fills the title with the file name a moment later: wait, then overwrite and verify
  const boxes = [...d.querySelectorAll('#textbox[contenteditable=true]')];
  // select only this box's text (selectAll can grab the whole page when the browser pane is hidden)
  const set = (el, t) => { el.focus(); const r = document.createRange(); r.selectNodeContents(el); const sel = window.getSelection(); sel.removeAllRanges(); sel.addRange(r); document.execCommand('insertText', false, t); el.dispatchEvent(new Event('input', { bubbles: true })); sel.removeAllRanges(); };
  for (let k = 0; k < 3; k++) {
    set(boxes[0], job.title.slice(0, 100)); set(boxes[1], job.description.slice(0, 4900)); await s(1500);
    if (boxes[0].innerText.trim() === job.title.slice(0, 100).trim() && boxes[1].innerText.trim().length > 10) break;
  }
  if (job.thumb) {   // only works once the channel is phone-verified
    try {
      const tb = await (await fetch(job.thumb)).blob();
      const ti = d.querySelector('#file-loader');
      if (ti && !ti.disabled) { const t2 = new DataTransfer(); t2.items.add(new File([tb], 'thumb.jpg', { type: 'image/jpeg' })); ti.files = t2.files; ti.dispatchEvent(new Event('change', { bubbles: true })); await s(2500); }
    } catch (e) { console.log('thumb skipped', e); }
  }
  d.querySelector('tp-yt-paper-radio-button[name=VIDEO_MADE_FOR_KIDS_NOT_MFK]')?.click();
  d.querySelector('#toggle-button')?.click(); await s(1500);
  for (const n of ['VIDEO_HAS_ALTERED_CONTENT_YES', 'VIDEO_PAID_PRODUCT_PLACEMENT_NO']) d.querySelector(`tp-yt-paper-radio-button[name=${n}]`)?.click();
  if (job.tags && job.tags.length) {
    const ti = d.querySelector('input[aria-label="Tags"]');
    if (ti) { ti.focus(); document.execCommand('insertText', false, job.tags.join(',') + ','); await s(400); ti.dispatchEvent(new Event('change', { bubbles: true })); ti.blur(); await s(500); }
  }
  const pick = async (sel, label) => {   // dropdowns: video language, category (lists are long: search all items, scroll, click)
    const el = d.querySelector(sel); if (!el) return;
    (el.querySelector('ytcp-dropdown-trigger, #trigger, [role=button]') || el).click(); await s(1200);
    const it = [...document.querySelectorAll('tp-yt-paper-item, [role=option]')].find(e => e.innerText.trim() === label);
    if (it) { it.scrollIntoView({ block: 'center' }); await s(300); it.click(); }
    else (document.activeElement || document.body).dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', code: 'Escape', keyCode: 27, bubbles: true }));
    await s(700);
  };
  // idioma do vídeo já vem dos padrões de envio do canal (Inglês EUA); categoria fica no padrão
  for (let k = 0; k < 3 && boxes[0].innerText.trim() !== job.title.slice(0, 100).trim(); k++) {   // re-check after the dropdowns
    set(boxes[0], job.title.slice(0, 100)); set(boxes[1], job.description.slice(0, 4900)); await s(1500);
  }
  if (boxes[0].innerText.trim() !== job.title.slice(0, 100).trim()) throw 'title did not stick: ' + boxes[0].innerText;
  await s(500); st('steps');
  for (let i = 0; i < 3; i++) { d.querySelector('#next-button').click(); await s(1800); }
  if (job.publish_at) { st('schedule'); await window.gcSchedule(d, job.publish_at); }
  else { d.querySelector('tp-yt-paper-radio-button[name=PUBLIC]').click(); await s(800); }
  st('uploading');
  const done = d.querySelector('#done-button');
  for (let i = 0; i < 1800 && done.getAttribute('aria-disabled') === 'true'; i++) {
    if (/limite diário de envios|daily upload limit/i.test(d.innerText)) throw 'daily upload limit reached (kept as draft)';
    await s(1000);
  }
  const link = [...d.querySelectorAll('a')].map(a => a.href).find(h => /shorts\/|youtu\.be\//.test(h)) || '';
  // "done" turns clickable before the bytes finish: wait for "Envio em X%" to end, or leaving the page interrupts the upload
  for (let i = 0; i < 2400; i++) { const p = d.querySelector('ytcp-video-upload-progress, .progress-label')?.innerText || ''; if (!/Envio em|Enviando|Uploading/.test(p)) break; st('bytes ' + p.slice(0, 50)); await s(1000); }
  done.click(); await s(3000);
  document.querySelector('ytcp-uploads-still-processing-dialog #close-button, ytcp-video-share-dialog #close-button')?.click();
  st('done');
  return link;
};

// Programar (agendar) na etapa Visibilidade. when = 'YYYY-MM-DD HH:MM' no horário de Brasília (fuso "(GMT-0300) Horário local").
// O que funcionou em 28/11/2026: hora PRIMEIRO (digitar + Enter + blur: o modelo só atualiza no blur), depois o dia
// clicando no calendário (o campo de data não aceita digitação). Com o painel escondido, o calendário só desenha
// depois de um screenshot: o agente tira um screenshot logo antes. Nunca apertar Escape com o calendário fechado
// (fecha o diálogo de envio e o vídeo vira rascunho).
window.gcSchedule = async (d, when) => {
  const s = ms => new Promise(r => setTimeout(r, ms));
  const [ymd, hm] = when.split(' '); const [Y, M, D] = ymd.split('-').map(Number); const [hh, mm] = hm.split(':').map(Number);
  const MON = ['jan.', 'fev.', 'mar.', 'abr.', 'mai.', 'jun.', 'jul.', 'ago.', 'set.', 'out.', 'nov.', 'dez.'];
  if (!d.querySelector('ytcp-visibility-scheduler')?.offsetParent) { d.querySelector('#second-container-expand-button')?.click(); await s(1200); }
  const sch = d.querySelector('ytcp-visibility-scheduler'); if (!sch) throw 'no scheduler';
  // 1) hora
  const ti = sch.querySelector('tp-yt-paper-input input, input');
  const hmTxt = String(hh).padStart(2, '0') + ':' + String(mm).padStart(2, '0');
  ti.focus(); ti.select(); document.execCommand('insertText', false, hmTxt);
  ti.dispatchEvent(new Event('input', { bubbles: true })); ti.dispatchEvent(new Event('change', { bubbles: true }));
  for (const t of ['keydown', 'keypress', 'keyup']) ti.dispatchEvent(new KeyboardEvent(t, { key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true }));
  await s(700); ti.blur(); await s(900);
  // 2) dia (calendário)
  if (!document.querySelector('ytcp-date-picker')?.offsetParent) { sch.querySelector('#datepicker-trigger ytcp-dropdown-trigger').click(); await s(1200); }
  let months = [];
  for (let i = 0; i < 30 && !months.length; i++) { const dp = document.querySelector('ytcp-date-picker'); months = dp ? [...dp.querySelectorAll('.calendar-month')] : []; if (!months.length) await s(500); }
  const m = months.find(x => (x.getAttribute('aria-label') || '').trim() === `${MON[M - 1]} de ${Y}`);
  if (!m) throw 'month not found ' + MON[M - 1] + ' ' + Y + ' in [' + months.map(x => x.getAttribute('aria-label')).join(',') + '] (take a screenshot first if empty)';
  const day = [...m.querySelectorAll('.calendar-day')].find(x => x.innerText.trim() === String(D) && !/disabled/.test(x.className));
  if (!day) throw 'day not selectable ' + D;
  day.click(); await s(1200);   // clicar no dia fecha o calendário
  const mo = JSON.parse(sch.getAttribute('model') || '{}');
  const ok = mo.date && mo.date.year === Y && mo.date.month === M - 1 && mo.date.day === D && mo.selectedTimeOfDayValue === hh * 3600 + mm * 60 && (mo.selectedTimezoneIndex || 0) === 0;
  if (!ok) throw 'schedule did not stick: ' + sch.getAttribute('model');
  if (!/Programar|Schedule/.test(d.querySelector('#done-button').innerText)) throw 'done button is not Programar';
};
'gcUpload ready';
