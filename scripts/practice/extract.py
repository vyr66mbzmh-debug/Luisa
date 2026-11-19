#!/usr/bin/env python3
"""Extract native Practice Booklet question boundaries without changing originals.

Inputs are explicitly supplied private authoring paths. Only published question
content and hashes may be exported; source paths remain in private inventories.
"""
import argparse
import collections
import hashlib
import json
import re
from pathlib import Path


def group(text, pos, opener='{', closer='}'):
    while pos < len(text) and text[pos].isspace(): pos += 1
    if pos >= len(text) or text[pos] != opener:
        raise ValueError(f'Expected {opener} at {pos}: {text[pos:pos+80]}')
    depth, start = 1, pos + 1
    pos += 1
    while pos < len(text):
        if text[pos] == '\\': pos += 2; continue
        if text[pos] == opener: depth += 1
        if text[pos] == closer: depth -= 1
        if not depth: return text[start:pos], pos + 1
        pos += 1
    raise ValueError('Unclosed group')


def clean_comments(text):
    return re.sub(r'(?<!\\)%[^\n]*', '', text)


def environment(text, start, name):
    pat = re.compile(r'\\(begin|end)\{' + re.escape(name) + r'\}')
    depth = 0
    for m in pat.finditer(text, start):
        depth += 1 if m[1] == 'begin' else -1
        if depth == 0: return text[start+len('\\begin{'+name+'}'):m.start()], m.end()
    raise ValueError(f'Unclosed {name}')


def split_items(text):
    """Return only list-level items; nested subparts never become questions."""
    stack=[]; items=[]; start=None; number=0
    token=re.compile(r'\\(?:begin\{([^}]+)\}|end\{([^}]+)\}|item\b|setcounter\{enum(?:i|ii|iii|iv)\}\{(\d+)\})')
    for m in token.finditer(text):
        if m[1]:stack.append(m[1])
        elif m[2]:
            if not stack or stack[-1]!=m[2]:raise ValueError(f'Environment mismatch {m[0]}')
            stack.pop()
        elif not stack and m[3]: number=int(m[3])
        elif not stack and m[0]==r'\item':
            if start is not None:items.append((label,text[start:m.start()].strip()))
            number+=1;label=str(number);start=m.end()
            if text[start:start+1]=='[': label,start=group(text,start,'[',']')
    if start is not None:items.append((label,text[start:].strip()))
    return items


def extract_native(text):
    body=clean_comments(text.split(r'\begin{document}',1)[1].split(r'\hypertarget{answers}',1)[0])
    event=re.compile(r'\\chaptersection\b|\\(?:section|subsection)\*\{|\\hypertarget\{|\\begin\{(?:questions|tierbox)\}')
    rows=[]; section=None;title=None;printed=None;pos=0
    while (m:=event.search(body,pos)):
        pos=m.end(); token=m[0]
        if token==r'\chaptersection':
            anchor,pos=group(body,pos);title,pos=group(body,pos);printed,pos=group(body,pos)
            section=title.split()[0] if re.match(r'\d+\.\d+',title) else None
            if 'set a' in title.lower():section='problem-a'
            if 'set b' in title.lower():section='problem-b'
        elif token==r'\hypertarget{':
            anchor,pos=group(body,m.end()-1)
            if anchor.lower() in ('seta','setb'):section='problem-'+anchor[-1].lower();title='Problem set '+anchor[-1].upper()
            if anchor=='set':section='problem';title='Problem solving'
            if anchor=='examquestions':section='exam';title='Selected exam question bank questions';printed=None
        elif token in (r'\section*{',r'\subsection*{'):
            heading,pos=group(body,m.end()-1)
            if re.match(r'\d+\.\d+\s',heading):section=heading.split()[0];title=heading
            if re.search(r'Problem (?:solving: )?[sS]et ([AB])',heading):
                section='problem-'+heading[-1].lower();title=heading
            if heading.startswith('Question ') and section=='exam':
                nxt=event.search(body,pos);end=nxt.start() if nxt else len(body)
                tex=body[pos:end].strip();tex=re.sub(r'\\(?:Needspace|vspace)\*?\{[^}]*\}\s*$','',tex)
                tex=re.sub(r'\\clearpage\s*$','',tex)
                rows.append(dict(sectionId=section,sectionTitle=title,number=heading[9:],questionLatex=tex,printedPage=printed))
                pos=end
        elif token==r'\begin{questions}':
            inner,pos=environment(body,m.start(),'questions')
            if not section:raise ValueError('Question list without section')
            rows.extend(dict(sectionId=section,sectionTitle=title,number=n,questionLatex=q,printedPage=printed) for n,q in split_items(inner))
        else:
            inner,pos=environment(body,m.start(),'tierbox')
            colour,p=group(inner,0);label,p=group(inner,p)
            if not section or not section.startswith('problem'):raise ValueError('Tier without problem set')
            rows.append(dict(sectionId=section,sectionTitle=title,number=label,questionLatex=inner[p:].strip(),printedPage=printed))
    for row in rows:
        hints=[]
        def hint(m):hints.append(m[1]);return ''
        row['questionLatex']=re.sub(r'\\begin\{hintbox\}(.*?)\\end\{hintbox\}',hint,row['questionLatex'],flags=re.S).strip()
        row['hintsLatex']=hints
    return rows


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--inventory',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    chapters=[]
    for source in json.loads(args.inventory.read_text()):
        if not source.get('publicPdf'):continue
        path=Path(source['path']);pdf=Path(source['publicPdf']);family=pdf.parent.name;chapter=int(pdf.stem.split('-')[1])
        rows=extract_native(path.read_text())
        for row in rows:
            book=('maths-'+family if family.startswith('pure') else 'maths-'+('statistics' if chapter<=(7 if family.endswith('1') else 3) else 'mechanics')+'-year-'+family[-1])
            row.update(id=f'practice/maths-a-level/{book}/ch{chapter}/{row["sectionId"]}/q{row["number"].lower()}',courseId='maths-a-level',bookId=book,chapterId=f'ch{chapter}',chapterNumber=chapter,questionLabel=row['number'])
        if len({r['id'] for r in rows})!=len(rows):raise ValueError(f'Duplicate IDs in {pdf}')
        chapters.append(dict(family=family,chapter=chapter,sourcePdf=str(pdf),nativeSha256=source['sha256'],questions=rows))
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(chapters,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'chapters':len(chapters),'questions':sum(len(c['questions']) for c in chapters),'byFamily':{f:sum(len(c['questions']) for c in chapters if c['family']==f) for f in sorted({c['family'] for c in chapters})}}))

if __name__=='__main__':main()
