/* Export selected teaching panels as vector PDF, keeping the website's own
   mathematical typesetting, source drawings, figure crops and answer ownership. */
const fs = require('node:fs');
const path = require('node:path');
const {chromium} = require('playwright');

const [base, planFile, destination] = process.argv.slice(2);
if (!base || !planFile || !destination) throw Error('Usage: node export-panels.cjs SITE_URL PLAN.json OUTPUT');
const plan = JSON.parse(fs.readFileSync(planFile));
const here = __dirname;
const styles = fs.readFileSync(path.join(here, 'panel.css'), 'utf8');
const maths = fs.readFileSync(path.join(here, 'print-maths.js'), 'utf8');
const exporter = fs.readFileSync(path.join(here, 'panel-state.js'), 'utf8');

(async function main() {
  const browser = await chromium.launch({channel: 'chrome'});
  try {
    const context = await browser.newContext({viewport:{width:1440,height:900},reducedMotion:'reduce',serviceWorkers:'block'});
    const page = await context.newPage();
    const paper = await context.newPage();
    for (const item of plan) {
      const out = path.join(destination, item.chapterKey);
      fs.mkdirSync(out, {recursive:true});
      const names = ['student','solution'].map(edition => path.join(out, edition+'-'+item.slide+'.pdf'));
      if (names.every(file=>fs.existsSync(file)) && !process.env.LUISA_REPRINT) continue;
      const url = new URL(item.viewer, base);
      url.searchParams.set('slide', item.slide);
      await page.goto(url.href, {waitUntil:'domcontentloaded'});
      await page.waitForFunction(()=>window.FMQ_TEST?.getState().slide);
      const source = page.locator('#slide-content .luisa-overview,#slide-content .ch14,#slide-content .source-slide,#slide-content .lesson-flow').first();
      await source.waitFor({state:'attached'});
      await page.evaluate(exporter);
      for (const [index, edition] of ['student','solution'].entries()) {
        const data = await page.evaluate(async opts=>window.luisaPrintPanel(opts), {item,edition});
        const links = data.css.map(href=>'<link rel="stylesheet" href="'+href+'">').join('');
        await paper.setContent('<!doctype html><base href="'+base+'">'+links+'<style>'+styles+'</style><body class="paper '+edition+'"><main id="print-body">'+data.html+'</main></body>',{waitUntil:'load'});
        await paper.evaluate(maths);
        await paper.evaluate(()=>prepareBookletMath(document));
        const result = await paper.evaluate(async({width,height})=>{
          await Promise.all([...document.images].map(el=>el.decode()));
          await document.fonts.ready;
          const el=document.querySelector('#print-body').firstElementChild;
          const scale=Math.min(1200/width,805/height);
          el.style.transform='scale('+scale+')';
          el.style.transformOrigin='0 0';
          el.style.left=(1200-width*scale)/2+'px';
          el.style.top=(805-height*scale)/2+'px';
          const rect=el.getBoundingClientRect();
          return [rect.left,rect.top,rect.right,rect.bottom];
        },data);
        if(result[0]<-1||result[1]<-1||result[2]>1201||result[3]>806) throw Error('Overflow '+JSON.stringify([item,edition,result]));
        const output=names[index]+'.part';
        await paper.pdf({path:output,printBackground:true,preferCSSPageSize:true,tagged:false});
        fs.renameSync(output,names[index]);
      }
      console.log(item.chapterKey,item.slide);
    }
  } finally { await browser.close(); }
})().catch(e=>{console.error(e);process.exitCode=1;});
