#!/usr/bin/env python3
"""Build published Practice Booklet data from explicit private native inputs.

Run extract.py first, then supply its output, the native input inventory and a
verified PDF marker inventory. No private path is copied to generated content.
This does not author or approve worked solutions.
"""
import argparse
import hashlib
import json
from pathlib import Path
from render import Renderer

def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def build(native,questions,locations,root):
    inputs={x['publicPdf']:x for x in native if x.get('publicPdf')}
    locations={x['file']:x for x in locations}
    summary=[];assets={}
    for chapter in questions:
        pdf=chapter['sourcePdf'];src=inputs[pdf];source=Path(src['path']);markers=locations[pdf]
        if not markers['labelsEqual'] or markers['questions']!=len(chapter['questions']):raise ValueError('Unverified PDF boundaries: '+pdf)
        if digest(source)!=chapter['nativeSha256']:raise ValueError('Native input changed: '+pdf)
        if digest(source.with_suffix('.pdf'))!=digest(root/pdf):raise ValueError('Native PDF differs from published PDF: '+pdf)
        family=chapter['family'];n=chapter['chapter'];title=source.parent.name.split(' - ',1)[1]
        path=f'content/practice/{family}/chapter-{n:02d}.json'
        renderer=Renderer(source.parent,root/'content/practice/assets','content/practice/assets')
        rows=[]
        for q,marker in zip(chapter['questions'],markers['markers']):
            if marker['label']!=q['number']:raise ValueError('Marker changed')
            row={k:q[k] for k in ('id','courseId','bookId','chapterId','chapterNumber','questionLabel')}
            row.update(chapterTitle=title,subchapterId=q['sectionId'],subchapterTitle=q['sectionTitle'],number=q['number'],question=renderer.render(q['questionLatex']),hints=[renderer.render(h) for h in q['hintsLatex']],steps=[],solutionStatus='pending',skillIds=[],topicIds=[])
            row['source']={'kind':'practice-booklet','pdf':pdf,'pdfSha256':digest(root/pdf),'nativeSha256':chapter['nativeSha256'],'questionLatexSha256':hashlib.sha256(q['questionLatex'].encode()).hexdigest(),'printedBookPage':q['printedPage'],'marker':{'page':marker['page'],'bbox':[round(v,3) for v in marker['bbox']]},'coordinateSystem':'PDF points, top-left origin','extraction':'native-latex','boundaryCheck':'all printed question markers match native sequence'}
            rows.append(row)
        data={'schemaVersion':1,'sourceFamily':family,'chapterNumber':n,'chapterTitle':title,'sourcePdf':pdf,'questions':rows}
        target=root/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n')
        assets.update(renderer.assets)
        summary.append({'sourceFamily':family,'chapterNumber':n,'chapterTitle':title,'dataPath':path,'questionCount':len(rows),'subchapters':[{'id':s,'title':next(q['subchapterTitle'] for q in rows if q['subchapterId']==s),'count':sum(q['subchapterId']==s for q in rows)} for s in dict.fromkeys(q['subchapterId'] for q in rows)]})
    return {'chapters':summary,'questionCount':sum(c['questionCount'] for c in summary),'assets':assets}

def main():
    p=argparse.ArgumentParser();p.add_argument('--inventory',type=Path,required=True);p.add_argument('--questions',type=Path,required=True);p.add_argument('--locations',type=Path,required=True);p.add_argument('--root',type=Path,default=Path('.'));p.add_argument('--report',type=Path,required=True);a=p.parse_args()
    report=build(*[json.loads(p.read_text()) for p in (a.inventory,a.questions,a.locations)],a.root)
    a.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(f"{len(report['chapters'])} chapters, {report['questionCount']} questions, {len(report['assets'])} source assets")
if __name__=='__main__':main()
