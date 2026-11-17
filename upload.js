(async()=>{const s=ms=>new Promise(r=>setTimeout(r,ms));
const [file,title,desc]=window.__job;
for(let i=0;i<20&&!document.querySelector('input[name=Filedata]');i++)await s(500);
const b=await (await fetch('https://raw.githubusercontent.com/rafael06428/canais/main/'+file)).blob();
const inp=document.querySelector('ytcp-uploads-file-picker input[type=file]')||document.querySelector('input[name=Filedata]');
const dt=new DataTransfer();dt.items.add(new File([b],file.split('/').pop(),{type:'video/mp4'}));inp.files=dt.files;inp.dispatchEvent(new Event('change',{bubbles:true}));
let d;for(let i=0;i<40;i++){d=document.querySelector('ytcp-uploads-dialog');if(d&&d.querySelectorAll('#textbox[contenteditable=true]').length>=2)break;await s(500)}
await s(1500);
const boxes=[...d.querySelectorAll('#textbox[contenteditable=true]')];
const set=(el,t)=>{el.focus();document.execCommand('selectAll',false,null);document.execCommand('insertText',false,t);el.dispatchEvent(new Event('input',{bubbles:true}))};
set(boxes[0],title);set(boxes[1],desc);await s(500);
d.querySelector('tp-yt-paper-radio-button[name=VIDEO_MADE_FOR_KIDS_NOT_MFK]').click();
d.querySelector('#toggle-button')?.click();await s(1000);
for(const n of ['VIDEO_HAS_ALTERED_CONTENT_YES','VIDEO_PAID_PRODUCT_PLACEMENT_NO'])d.querySelector(`tp-yt-paper-radio-button[name=${n}]`)?.click();
await s(500);for(let i=0;i<3;i++){d.querySelector('#next-button').click();await s(1500)}
d.querySelector('tp-yt-paper-radio-button[name=PUBLIC]').click();await s(800);
for(let i=0;i<120;i++){const st=d.querySelector('#done-button');if(st&&!st.hasAttribute('disabled')&&st.getAttribute('aria-disabled')!=='true')break;await s(1000)}
const link=[...d.querySelectorAll('a')].map(a=>a.href).find(h=>/shorts|youtu\.be/.test(h));
d.querySelector('#done-button').click();await s(3000);
window.__res=(link||'nolink')+' '+boxes[0].innerText;})();
