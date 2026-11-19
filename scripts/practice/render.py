"""Small strict renderer for the native published booklet dialect.

Unknown commands are errors: no silent stripping of mathematical content.
"""
import hashlib
import html
import re
import shutil
from pathlib import Path
from extract import environment, group, split_items

class Renderer:
    def __init__(self, source_dir, output_dir, asset_url):
        self.source_dir=Path(source_dir);self.output_dir=Path(output_dir);self.asset_url=asset_url;self.assets={}

    def image(self,name,options=""):
        path=self.source_dir/name
        if not path.suffix:path=path.with_suffix('.png')
        if not path.is_file():raise ValueError(f'Missing asset {name}')
        digest=hashlib.sha256(path.read_bytes()).hexdigest();filename=digest[:20]+path.suffix.lower()
        self.output_dir.mkdir(parents=True,exist_ok=True);target=self.output_dir/filename
        if not target.exists():shutil.copyfile(path,target)
        self.assets[filename]={'sha256':digest}
        style=[]
        for key,value in re.findall(r'(width|height)=([^,]+)',options):
            if re.fullmatch(r'[\d.]+(?:mm|cm|pt)',value):style.append(('max-width' if key=='width' else 'max-height')+':'+value)
            elif re.fullmatch(r'[\d.]*\\(?:line|text)width',value):
                ratio=re.match(r'[\d.]*',value)[0];style.append('max-width:'+str(float(ratio or 1)*100)+'%')
            else:raise ValueError('Unsupported image dimension '+value)
        return '<img style="'+html.escape(';'.join(style),quote=True)+'" class="practice-figure"  src="'+self.asset_url+'/'+filename+'" alt="Original question diagram">'

    def math(self,s,display=False):
        for macro,value in {'vi':r'\mathbf i','vj':r'\mathbf j','vk':r'\mathbf k','va':r'\mathbf a','vb':r'\mathbf b','vv':r'\overrightarrow','vc':r'\mathbf c','vd':r'\mathbf d','dy':r'\frac{dy}{dx}'}.items():s=re.sub(r'\\'+macro+r'\b',lambda m:value,s)
        s=re.sub(r'\\begin\{array\}\{\*\{(\d+)\}\{([clr])\}\}', lambda m:r'\begin{array}{'+m[2]*int(m[1])+'}',s)
        s=s.replace(r'{r@{\;}l}',r'{rl}')
        s=s.replace(r'\cline{2-2}x-1\big)&2x^3-5x^2+8x-5',r'x-1\big)&\overline{2x^3-5x^2+8x-5}')
        while (m:=re.search(r'\\cv(?![A-Za-z])',s)):
            p=m.end();args=[]
            for _ in range(2):
                while p<len(s) and s[p].isspace():p+=1
                if s[p]=='{':a,p=group(s,p)
                else:a=s[p];p+=1
                args.append(a)
            s=s[:m.start()]+r'\begin{pmatrix}'+args[0]+r'\\'+args[1]+r'\end{pmatrix}'+s[p:]
        return '<span data-math="'+html.escape(s,quote=True)+'"'+(' data-display="true"' if display else '')+'></span>'

    def render(self,s):
        out=[];i=0
        while i<len(s):
            if s[i]=='$':
                j=i+1
                while j<len(s) and (s[j]!='$' or s[j-1]=='\\'):j+=1
                if j==len(s):raise ValueError('Unclosed inline math')
                out.append(self.math(s[i+1:j]));i=j+1;continue
            if s.startswith(r'\[',i) or s.startswith(r'\(',i):
                end=r'\]' if s[i+1]=='[' else r'\)';j=s.index(end,i+2);out.append(self.math(s[i+2:j],end==r'\]'));i=j+2;continue
            if s[i] in '{}':i+=1;continue
            if s[i]!='\\':
                j=i+1
                while j<len(s) and s[j] not in '$\\{}':j+=1
                out.append(html.escape(s[i:j]).replace('~','&nbsp;').replace('---','—').replace('--','–'));i=j;continue
            m=re.match(r'\\([A-Za-z]+|.)',s[i:]);cmd=m[1];i+=len(m[0])
            def arg():
                nonlocal i
                a,i=group(s,i);return a
            def optional():
                nonlocal i
                while i<len(s) and s[i].isspace():i+=1
                if i<len(s) and s[i]=='[':a,i=group(s,i,'[',']');return a
                return ''
            if cmd=='begin':
                name=arg();start=i-len(r'\begin{'+name+'}');inner,i=environment(s,start,name)
                if name in ('parts','romanparts','enumerate','itemize'):
                    opt=''
                    if inner.lstrip().startswith('['):opt,p=group(inner,0,'[',']');inner=inner[p:]
                    typ='i' if name=='romanparts' or r'\roman' in opt else ('a' if name=='parts' or r'\alph' in opt else '1')
                    items=split_items(inner);lis=[]
                    for label,content in items:
                        attrs=' value="'+label+'"' if label.isdigit() else ''
                        lis.append('<li'+attrs+'>'+self.render(content)+'</li>')
                    out.append(('<ul>'+''.join(lis)+'</ul>') if name=='itemize' else '<ol type="'+typ+'">'+''.join(lis)+'</ol>')
                elif name=='tabular':
                    p=0
                    if inner.lstrip().startswith('['):_,p=group(inner,p,'[',']')
                    columns,p=group(inner,p);table=inner[p:];tableclass='practice-table' if '|' in columns or r'\hline' in table or r'\cline' in table else 'practice-layout-table';table=re.sub(r'\\(?:hline|cline\{[^}]*\})','',table)
                    # Protect inline mathematical arrays and escaped ampersands.
                    cells=[];rows=[];start=0;math=False;braces=0;k=0
                    while k<len(table):
                        if table[k]=='$' and (not k or table[k-1]!='\\'):math=not math
                        if not math:
                            if table[k]=='{':braces+=1
                            if table[k]=='}':braces-=1
                            if braces==0 and table[k]=='&' and (not k or table[k-1]!='\\'):
                                cells.append(table[start:k]);start=k+1
                            elif braces==0 and table.startswith('\\\\',k):
                                cells.append(table[start:k]);rows.append(cells);cells=[];k+=1;start=k+1
                        k+=1
                    if table[start:].strip():cells.append(table[start:])
                    if cells:rows.append(cells)
                    out.append('<table class="'+tableclass+'"><tbody>'+''.join('<tr>'+''.join('<td>'+self.render(c.strip())+'</td>' for c in row)+'</tr>' for row in rows)+'</tbody></table>')
                else:
                    if name=='minipage':
                        p=0
                        if inner.lstrip().startswith('['):_,p=group(inner,p,'[',']')
                        _,p=group(inner,p);inner=inner[p:]
                    elif name=='tcolorbox' and inner.lstrip().startswith('['):_,p=group(inner,0,'[',']');inner=inner[p:]
                    elif name not in ('center','quote','flushleft','tcolorbox'):raise ValueError('Unknown environment '+name)
                    out.append('<div>'+self.render(inner)+'</div>')
            elif cmd in ('textbf','textit','textsf','textrm','emph','fbox','shortstack'):
                if cmd=='shortstack':optional()
                val=self.render(arg());tag='strong' if cmd=='textbf' else ('em' if cmd in ('textit','emph') else 'span');out.append('<'+tag+'>'+val+'</'+tag+'>')
            elif cmd=='qmarks':
                n=arg();out.append('<span class="marks">('+html.escape(n)+' '+('mark' if n=='1' else 'marks')+')</span>')
            elif cmd in ('qtag','ep'):out.append('<span class="practice-tag">'+(html.escape(arg()) if cmd=='qtag' else 'E/P')+'</span> ')
            elif cmd=='includegraphics':
                opts=optional();out.append(self.image(arg(),opts))
            elif cmd=='ansgraph':
                width=optional() or '45mm';out.append(self.image('assets/'+arg()+'.png','width='+width))
            elif cmd=='datatable':
                columns=arg();body=arg();out.append(self.render(r'\begin{tabular}{'+columns+'}'+body+r'\end{tabular}'))
            elif cmd in ('Needspace','vspace','hspace'):
                if s[i:i+1]=='*':i+=1
                arg()
            elif cmd in ('setlength','renewcommand'):arg();arg()
            elif cmd=='raisebox':arg();out.append(self.render(arg()))
            elif cmd=='parbox':optional();arg();out.append(self.render(arg()))
            elif cmd=='multicolumn':arg();arg();out.append(self.render(arg()))
            elif cmd in ('par','\\'):out.append('<br>');optional() if cmd=='\\' else None
            elif cmd in ('enspace','quad','qquad','hfill',',',';',' '):out.append(' ')
            elif cmd in ('leavevmode','noindent','centering','small','medskip','smallskip'):pass
            elif cmd=='pounds':out.append('£')
            elif cmd=='copyright':out.append('©')
            elif cmd in ('%','&','_','#','{','}','$'):out.append(html.escape(cmd))
            else:raise ValueError('Unknown command \\'+cmd+' near '+s[max(0,i-30):i+70])
        return ''.join(out).strip()
