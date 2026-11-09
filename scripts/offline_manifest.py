"""Build complete, hash-addressed offline chapter inventories from packaged files."""
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import urlsplit, unquote
import posixpath

BOOK_BASES = {'maths-applied-year-1':'applied-year-1','maths-applied-year-2':'applied-year-2','further-core-pure-1':'core-pure-1','further-core-pure-2':'core-pure-2','maths-pure-year-2':'pure-year-2'}
BOOK_ALIASES = {'maths-mechanics-year-1':'maths-applied-year-1','maths-mechanics-year-2':'maths-applied-year-2','maths-statistics-year-1':'maths-applied-year-1','maths-statistics-year-2':'maths-applied-year-2','pure-core-1':'further-core-pure-1','pure-core-2':'further-core-pure-2'}


def generate(root, entries, version):
    root = Path(root)
    teaching = json.loads((root/'teaching-catalogue.js').read_text().split('=',1)[1].strip().rstrip(';'))
    catalogue = json.loads((root/'textbook-catalogue.json').read_text())
    shared = {n for n in entries if (len(Path(n).parts)==1 and Path(n).suffix in {'.html','.js','.css','.webmanifest'}) or n in {'textbook-catalogue.json','release.json','version-history.json'} or n.startswith('vendor/') or n.startswith('assets/luisa/') or (n.startswith('resources/') and (Path(n).suffix in {'.js','.css'} or Path(n).name=='index.json'))}
    shared.discard('sw.js')
    def local(url, bases=('',)):
        p = urlsplit(url)
        if p.scheme or p.netloc or not p.path or p.path.startswith('#'): return None
        name = unquote(p.path)
        for base in bases:
            candidate = posixpath.normpath(posixpath.join(base,name))
            if candidate.startswith('./'): candidate=candidate[2:]
            if candidate in entries:return candidate
        return None
    def refs(obj, bases):
        found=set()
        if isinstance(obj,dict):
            for field,value in obj.items():
                if field in {'asset','solutionsResource'} and isinstance(value,str) and value and not value.startswith('data:'):
                    if not local(value,bases):raise ValueError('Unresolved offline dependency: '+value+' in '+str(bases))
                found.update(refs(value,bases))
        elif isinstance(obj,list):
            for value in obj:found.update(refs(value,bases))
        elif isinstance(obj,str):
            # JSON asset fields and embedded question HTML; do not follow unrelated navigation.
            candidates=[obj] if len(obj)<1000 else []
            candidates+=re.findall(r'(?:src|href)=[\"\']([^\"\']+)',obj)
            for image in re.findall(r'src=[\"\']([^\"\']+)',obj):
                if not image.startswith('data:') and not local(image,bases):raise ValueError('Unresolved offline image: '+image)
            for value in candidates:
                if '\n' in value or '<' in value:continue
                name=local(value,bases)
                if name:found.add(name)
        return found
    for name in list(shared):
        if name.endswith('.css'):
            for url in re.findall(r'url\([\"\']?([^\)\"\']+)',(root/name).read_text()):
                if url.startswith('data:'):continue
                path=local(url,(str(Path(name).parent),'',))
                if not path:raise ValueError('Unresolved offline stylesheet dependency: '+name+' -> '+url)
                shared.add(path)
    def close_assets(names):
        visited=set();pending=list(names)
        while pending:
            name=pending.pop()
            if name in visited:continue
            visited.add(name)
            suffix=Path(name).suffix
            if suffix not in {'.svg','.css'}:continue
            content=(root/name).read_text()
            urls=re.findall(r'(?:src|href)=["\']([^"\']+)',content) if suffix=='.svg' else re.findall(r'url\(["\']?([^\)"\']+)',content)
            for url in urls:
                if url.startswith(('data:','#')):continue
                dependency=local(url,(str(Path(name).parent),'',))
                if not dependency:raise ValueError('Unresolved nested offline dependency: '+name+' -> '+url)
                if dependency not in names:names.add(dependency);pending.append(dependency)
        return names
    shared=close_assets(shared)
    # Use the same print destinations as the skill library, including Edexcel-only topics.
    library_path=root/'data.js'
    library=json.loads(library_path.read_text().split('=',1)[1].strip().rstrip(';')) if library_path.exists() else {'courses':[]}
    print_by_skill={}
    for course in library['courses']:
        for book in course['books']:
            for topic in book['topics']:
                for skill in topic['skills']:
                    if course['id']=='maths-a-level':
                        urls=[topic.get('printoutPath'),skill.get('printoutPath')]
                    else:
                        urls=[topic.get('edexcelPrintoutPath'),f"printouts/{book['id']}/{topic['id']}/skills/{skill['id']}_{'v03' if skill['code']=='1.28' else 'v02'}.pdf"]
                    paths=set()
                    for url in filter(None,urls):
                        path=local(url)
                        if not path:raise ValueError('Offline print PDF missing: '+url)
                        paths.add(path)
                    print_by_skill[skill['id']]=paths
    packs=[];warnings=[]
    for book in catalogue['books']:
        tk=BOOK_ALIASES.get(book['id'],book['id'])
        for ch in book['chapters']:
            number=int(ch['id'])
            tc=next((c for c in teaching.get(tk,{}).get('chapters',[]) if c['number']==number),{})
            files=set(); unavailable=[]; links={}
            for kind in ['slides','booklet','solutions','pdf','practice']:
                url=tc.get(kind) or next((r.get('url') for r in ch['resources'] if r['type']==kind and r['access']=='available'),None)
                if url:
                    path=local(url)
                    if not path:raise ValueError('Offline resource missing: '+url)
                    files.add(path);links[kind]=url
                elif kind != 'practice':unavailable.append({'slides':'Teaching slides','booklet':'Student booklet','solutions':'Solutions','pdf':'Textbook chapter'}[kind])
            for resource in ch['resources']:
                if resource.get('access')=='available' and resource.get('url'):
                    path=local(resource['url'])
                    if path:files.add(path)
            if tc.get('slides'):
                viewer=urlsplit(tc['slides']).path
                if viewer=='lesson-viewer.html' or viewer=='pure1-native-viewer.html':
                    base='resources/pure-year-1/v11/';assetbase='resources/pure-year-1/native/'
                elif viewer=='pure2-lesson-viewer.html' or (viewer in {'v025-lesson-viewer.html','v026-lesson-viewer.html','v027-lesson-viewer.html'} and tk=='maths-pure-year-2'):
                    base=assetbase='resources/pure-year-2/v12/'
                else:
                    base=assetbase='resources/teaching/v003/'+BOOK_BASES[tk]+'/'
                chapter=base+f'chapter-{number:02}.json'
                if chapter not in entries:raise ValueError('Offline lesson missing: '+chapter)
                try:
                    assets=close_assets(refs(json.loads((root/chapter).read_text()),(assetbase,base,'')))
                except ValueError as error:
                    warnings.append({'pack':book['id']+':'+ch['id'],'reason':str(error)})
                    unavailable.append('Teaching slides offline (an existing dependency is unavailable)')
                    links.pop('slides',None)
                else:
                    files.add(chapter);files.update(assets)
                # Include the viewer's textbook even if an older library catalogue omitted it.
                extras = [base+f'textbook/chapter-{number:02}.pdf']
                if 'booklet' not in links:
                    extras.append(base+f'booklets/chapter-{number:02}.pdf')
                for extra in extras:
                    if extra in entries:files.add(extra)
            practice=[q for q in catalogue['questions'] if any(t['book']==book['id'] and t['chapter']==ch['id'] for t in q['targets'])]
            for skill in {q['skill'] for q in practice}:
                name='content/'+skill+'.json'
                if name not in entries:raise ValueError('Offline practice missing: '+name)
                files.add(name);files.update(refs(json.loads((root/name).read_text()),('',)));files.update(print_by_skill.get(skill,set()))
            if not practice:unavailable.append('Mapped practice questions (not yet available)')
            if not files:continue
            packs.append({'id':book['id']+':'+ch['id'],'book':book['title'],'chapter':ch['id'],'title':ch['title'],'course':book['course'],'bookId':book['id'],'links':links,'unavailable':unavailable,'practiceEntries':len(practice),'files':sorted(close_assets(files)-shared)})
    # Non-Edexcel/unmapped skill practice remains accessible from the skill library.
    mapped_skills={q['skill'] for q in catalogue['questions'] if q.get('targets')}
    for course in library['courses']:
        for book in course['books']:
            extra=[skill for topic in book['topics'] for skill in topic['skills'] if skill['id'] not in mapped_skills]
            files=set()
            for skill in extra:
                name='content/'+skill['id']+'.json'
                if name not in entries:raise ValueError('Offline skill missing: '+name)
                files.add(name);files.update(refs(json.loads((root/name).read_text()),('',)))
                files.update(print_by_skill.get(skill['id'],set()))
            if files:
                packs.append({'id':book['id']+':additional-skills','book':book['title'],'chapter':'Additional','title':'Skill practice','skill':extra[0]['id'],'topic':next(t['id'] for t in book['topics'] if extra[0] in t['skills']),'course':course['id'],'bookId':book['id'],'links':{},'unavailable':[],'practiceEntries':sum(len(s['questions']) for s in extra),'files':sorted(close_assets(files)-shared)})
    used=shared|set().union(*(set(p['files']) for p in packs))
    inventory={k:entries[k] for k in sorted(used)}
    revision=hashlib.sha256(json.dumps(inventory,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    result={'schemaVersion':1,'version':version,'revision':revision,'shared':sorted(shared),'files':inventory,'packs':packs,'warnings':warnings}
    content=(json.dumps(result,ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n').encode()
    (root/'offline-catalogue.json').write_bytes(content)
    entries['offline-catalogue.json']={'sha256':hashlib.sha256(content).hexdigest(),'bytes':len(content)}
    return result
