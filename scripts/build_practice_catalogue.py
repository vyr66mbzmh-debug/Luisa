#!/usr/bin/env python3
"""Join exact practice questions with checked working and explicit skill mappings.

The default is fail-closed: every source row needs a matching authored solution.
This never edits the source booklet PDFs. Mixed chapter exercises get their own
review skill rather than being indiscriminately included in every narrow skill.
"""
import argparse
from collections import Counter
import json
from html.parser import HTMLParser
import re
from pathlib import Path

class _LetteredParts(HTMLParser):
    """Read explicit source list values without counting nested roman parts."""
    def __init__(self, markup):
        super().__init__(convert_charrefs=False)
        self.lists=[]
        self.parts=[]
        self.offsets=[0]
        for line in markup.splitlines(keepends=True):
            self.offsets.append(self.offsets[-1]+len(line))
        self.feed(markup)

    def handle_starttag(self, tag, attrs):
        attrs=dict(attrs)
        if tag in ('ol','ul'):
            self.lists.append({'lettered':tag=='ol' and attrs.get('type')=='a',
                               'next':int(attrs.get('start','1'))})
        elif tag=='li' and len(self.lists)==1 and self.lists[0]['lettered']:
            current=self.lists[0]
            value=int(attrs.get('value',current['next']))
            line,col=self.getpos()
            self.parts.append((value,self.offsets[line-1]+col,self.get_starttag_text()))
            current['next']=value+1

    def handle_endtag(self, tag):
        if tag in ('ol','ul') and self.lists:
            self.lists.pop()


def align_solution_parts(question, solution):
    """Match source subpart labels, including intentional gaps and continuations.

    Diagrams may contain their own labels; when no equivalent HTML list exists,
    retain the reviewed authored solution rather than guessing its numbering.
    """
    source=_LetteredParts(question).parts
    target=_LetteredParts(solution).parts
    if not source or len(source)!=len(target):
        return solution
    for (value,_,_),(_,offset,tag) in reversed(list(zip(source,target))):
        tag=re.sub(r'\svalue\s*=\s*(?:"[^"]*"|\'[^\']*\'|[^\s>]+)','',tag,flags=re.I)
        replacement=tag[:-1]+f' value="{value}">'
        # Work right-to-left so preceding source offsets remain unchanged.
        end=solution.index('>',offset)+1
        solution=solution[:offset]+replacement+solution[end:]
    return solution


ROOT=Path(__file__).resolve().parents[1]
# Entries correspond to the original numbered subsections, in order. Empty
# entries use the exact native subsection as a separately selectable skill.
SECTION_SKILLS={
 'pure-year-1':{
  1:['1.01','','','1.01','1.02','1.02'],
  2:['1.06','1.06','','1.08','1.10','1.11'],
  3:['1.07','1.07','1.07','1.20','1.20','1.21','1.21'],
  4:['1.15','1.16','1.18','','1.28','1.28','1.28'],
  5:['1.03','1.03','1.03','1.03','1.05'],
  6:['1.12','1.12','1.12','1.12','1.12'],
  7:['1.13','1.14','1.14','1.45','1.45'],
  8:['1.29','1.29','1.29','1.29','1.29'],
  9:['1.39','1.39','1.39','1.39','1.41','1.28,1.41'],
  10:['1.40','1.40','1.42','1.40','1.40,1.42','1.42'],
  11:['1.46']*6,
  12:['1.30','1.30','1.31','1.31','1.31','1.32','1.34','1.34','1.34','1.33','1.35'],
  13:['1.36','1.36','1.36','1.37','1.37','1.37','1.37'],
  14:['1.24','1.25','1.26','1.22','1.22','1.22','1.23','1.27']},
 'pure-year-2':{
  1:['2.44','','2.37','2.37',''],
  2:['2.13','2.10','2.10','2.12','2.13','2.11','2.13'],
  3:['2.07','2.07','2.08','2.08','2.08','2.06','2.06',''],
  4:['2.09','2.09','2.09,2.37'],
  5:['2.01','2.01','2.01','2.02','2.19'],
  6:['2.15','2.15','2.15','2.04,2.15','2.14'],
  7:['2.16','2.16','2.17','','2.18','','2.05'],
  8:['2.41']*5,
  9:['2.21','2.21','2.22','2.24','2.25','2.21','2.42','2.26','2.20','2.23'],
  10:['2.27','2.28','2.29',''],
  11:['2.32','2.33','2.39','2.33,2.34','2.35','2.36','2.38','2.31','2.30','2.40','2.40'],
  12:['2.45']*4},
 'applied-year-1':{
  1:['1.47','1.47','1.47','','1.58'],2:['1.48']*5,3:['1.49']*5,4:['1.50']*2,
  5:['1.52','1.53','1.54','1.52'],6:['1.55','1.56','1.56'],7:['1.57']*4,
  8:['','','','1.68'],9:['1.64','1.64','1.65','1.65','1.65'],
  10:['1.66','1.68','1.67','1.68','1.69','1.70'],11:['1.71']*5},
 'applied-year-2':{
  1:['','2.46','2.46'],2:['2.49']*5,3:['2.50']*6+['2.51'],4:['2.60']*5,
  5:['2.52','2.55','2.53'],6:['2.58']*4,
  7:['2.52','2.52','2.53','2.61','2.55','2.54,2.56'],
  8:['2.57','2.58','2.59','2.59','2.59']}}


def build(root=ROOT):
    textbook=json.loads((root/'textbook-catalogue.json').read_text())
    books={b['id']:b for b in textbook['books']}
    existing=textbook['skills']
    descriptors=[];extra={};seen=set();chapters=[]
    for path in sorted((root/'content/practice').glob('*/chapter-*.json')):
        doc=json.loads(path.read_text());family=doc['sourceFamily'];number=doc['chapterNumber']
        authored=root/'resources/practice-solutions'/family/path.name
        if not authored.exists():raise ValueError(f'Missing worked solutions: {family}/{path.name}')
        solutions=json.loads(authored.read_text())['solutions']
        by_id={r['id']:r for r in solutions}
        if len(by_id)!=len(solutions):raise ValueError(f'Duplicate worked solutions: {authored}')
        if set(by_id)!={q['id'] for q in doc['questions']}:raise ValueError(f'Source/solution mismatch: {authored}')
        changed=[]
        for question in doc['questions']:
            ident=question['id'];book=question['bookId'];course=question['courseId'];section=question['subchapterId']
            if ident in seen:raise ValueError(f'Duplicate source question: {ident}')
            seen.add(ident)
            mapped=[]
            if section[0].isdigit():
                raw=SECTION_SKILLS[family][number][int(section.split('.')[1])-1]
                mapped=['smq-'+x for x in raw.split(',') if x]
            for skill in mapped:
                if skill not in existing or existing[skill]['book']!=book:raise ValueError(f'Invalid skill mapping {ident}: {skill}')
            if not mapped:
                sid=f'practice-{family}-ch{number}-{section}'
                # Prefer the chapter's established library topic. This is broad
                # grouping only; mixed exercises keep a distinct review skill.
                candidates=Counter(existing[q['skill']]['topic'] for q in textbook['questions'] for t in q['targets'] if t['book']==book and str(t['chapter'])==str(number))
                topic=candidates.most_common(1)[0][0] if candidates else f'practice-topic-ch{number}'
                extra[sid]=dict(id=sid,courseId=course,bookId=book,topicId=topic,topicTitle=question['chapterTitle'],code=f'Practice {section}' if section[0].isdigit() else f'Chapter {number} review',title=question['subchapterTitle'],bookTitle=books[book]['title'])
                mapped=[sid]
            solution=by_id[ident]
            if solution.get('status')!='worked' or not solution.get('method') or not solution.get('solutionHtml') or not solution.get('steps'):raise ValueError(f'Incomplete solution: {ident}')
            if solution.get('answerCheck') not in {'matches','domain-qualified','source-discrepancy'}:raise ValueError(f'Unchecked answer: {ident}')
            question.update(steps=[align_solution_parts(question['question'],solution['solutionHtml'])],solutionStatus='worked',skillIds=mapped)
            fields=('id','courseId','bookId','chapterId','chapterNumber','chapterTitle','subchapterId','subchapterTitle','questionLabel')
            descriptors.append(dict(**{k:question[k] for k in fields},board='Edexcel',skillIds=mapped,dataPath=path.relative_to(root).as_posix()))
            changed.append(question)
        doc['questions']=changed;chapters.append((path,doc))
    if len(chapters)!=45:raise ValueError(f'Expected45 practice booklets, found{len(chapters)}')
    # Write only after every source and solution passes the complete join.
    for path,doc in chapters:path.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n')
    index=dict(version=1,questions=descriptors,skills=list(extra.values()))
    (root/'practice-catalogue.json').write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n')
    return len(descriptors)

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--root',type=Path,default=ROOT);args=parser.parse_args()
    print(f'{build(args.root)} practice questions joined with worked solutions.')
