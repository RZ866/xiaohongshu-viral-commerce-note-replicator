// Developer-only test of locally generated project HTML; never controls user sessions.
const fs=require('fs'),path=require('path'),{pathToFileURL}=require('url'),{chromium}=require('playwright');
const args=process.argv.slice(2),get=k=>args[args.indexOf(k)+1],root=path.resolve(__dirname,'..'),out=path.join(root,'.qa/browser');
fs.mkdirSync(out,{recursive:true});
(async()=>{
 const browser=await chromium.launch({headless:true,...(args.includes('--browser')?{executablePath:get('--browser')}:{})});
 const context=await browser.newContext({offline:true,viewport:{width:1440,height:1000}}),page=await context.newPage(),requests=[],errors=[];
 page.on('request',r=>{if(/^https?:/.test(r.url()))requests.push(r.url())});page.on('pageerror',e=>errors.push(e.message));
 await page.goto(pathToFileURL(path.join(root,'examples/screenshot/xiaohongshu-replication-report.html')).href);
 await page.evaluate(async()=>{await document.fonts.ready;await Promise.all([...document.images].map(i=>i.decode()))});
 const result={browser:browser.version()};
 const layout=()=>page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1);
 result.desktop=await layout();result.chinese=(await page.locator('h1').innerText()).includes('原创复刻');
 result.images=await page.evaluate(()=>[...document.images].every(i=>i.naturalWidth>0));
 await page.screenshot({path:path.join(out,'desktop.png'),fullPage:true});await page.screenshot({path:path.join(out,'preview.png')});
 await page.locator('#plan-A').screenshot({path:path.join(out,'plan-a.png')});await page.locator('.migration').screenshot({path:path.join(out,'migration.png')});
 await page.setViewportSize({width:390,height:844});await page.evaluate(()=>scrollTo(0,0));result.mobile=await layout();await page.screenshot({path:path.join(out,'mobile.png')});
 await page.setViewportSize({width:1440,height:1000});await page.emulateMedia({media:'print'});await page.pdf({path:path.join(out,'print.pdf'),format:'A4',printBackground:true});result.print=fs.statSync(path.join(out,'print.pdf')).size>10000;
 await page.emulateMedia({media:'screen'});await page.goto(pathToFileURL(path.join(root,'.qa/hostile.html')).href);result.security=await page.evaluate(()=>!globalThis.pwned&&document.querySelectorAll('script').length===0);
 result.offline=requests.length===0&&errors.length===0;
 fs.writeFileSync(path.join(out,'results.json'),JSON.stringify(result,null,2));if(Object.values(result).some(x=>x===false))throw Error(JSON.stringify(result));console.log(JSON.stringify(result));await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
