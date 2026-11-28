const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();const pg=await b.newPage({viewport:{width:1920,height:1080}});
pg.on('pageerror',e=>console.log('ERR',e.message));pg.on('console',m=>{if(m.type()==='error')console.log('CERR',m.text())});
await pg.goto('file://'+__dirname+'/index.html');await pg.waitForTimeout(500);
const ts=process.argv.slice(2).map(Number);
for(const t of ts){await pg.evaluate(t=>window.seek(t),t);await pg.screenshot({path:`f_${String(t).padStart(6,'0')}.jpg`,type:'jpeg',quality:80});}
console.log('DUR',await pg.evaluate(()=>window.DUR));await b.close();})();
