// Validate every generated prompt and hint with the site's own KaTeX version.
const fs = require('fs'), path = require('path');
const root=path.resolve(__dirname,'../..');
const katex=require(path.join(root,'vendor/katex.min.js'));
const decode=s=>s.replace(/&(?:amp|quot|lt|gt|#x27|#39);/g,t=>({'&amp;':'&','&quot;':'"','&lt;':'<','&gt;':'>','&#x27;':"'",'&#39;':"'"}[t]));
let count=0,errors=[];
for (const family of fs.readdirSync(path.join(root,'content/practice'))) {
 if(family==='assets')continue;
 for(const file of fs.readdirSync(path.join(root,'content/practice',family)).filter(p=>p.endsWith('.json'))){
  const data=JSON.parse(fs.readFileSync(path.join(root,'content/practice',family,file)));
  for (const q of data.questions) for(const html of [q.question,...q.hints]) for(const match of html.matchAll(/data-math="([^"]*)"([^>]*)/g)) {
   const math=decode(match[1]);count++;
   try{katex.renderToString(math,{displayMode:match[2].includes('data-display="true"'),throwOnError:true,strict:'error'});}catch(e){errors.push({id:q.id,math,error:e.message})}
  }
 }
}
module.exports={expressions:count,errors};
if(require.main===module){console.log(JSON.stringify(module.exports,null,2));if(errors.length)process.exit(1);}
