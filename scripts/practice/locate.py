#!/usr/bin/env python3
"""Independently verify every native question label against printed PDF markers.

Output coordinates describe the original question's label, not a crop rectangle.
Do not use these anchors to crop questions or omit the rest of a question.
"""
import argparse
import json
import re
from pathlib import Path
import pymupdf

def locate(chapters,root):
    report=[]
    for c in chapters:
        with pymupdf.open(root/c['sourcePdf']) as d:
            stop=next(x[2]-1 for x in d.get_toc() if x[1]=='Answers');candidates=[]
            for n in range(1,stop):
                for block in d[n].get_text('dict',flags=pymupdf.TEXTFLAGS_DICT & ~pymupdf.TEXT_PRESERVE_IMAGES)['blocks']:
                    for line in block.get('lines',[]):
                        title=''.join(s['text'] for s in line['spans']).strip()
                        if re.fullmatch(r'Question \d+',title):candidates.append({'label':title[9:],'page':n+1,'bbox':line['bbox']})
                        for s in line['spans']:
                            text=s['text'].strip();box=s['bbox']
                            if (re.fullmatch(r'\d+\.',text) and box[0]<75 and 'bold' in s['font'].lower()) or text in ('Bronze','Silver','Gold'):
                                candidates.append({'label':text.rstrip('.'),'page':n+1,'bbox':box})
            candidates.sort(key=lambda x:(x['page'],x['bbox'][1]))
            exact=[q['number'] for q in c['questions']]==[x['label'] for x in candidates]
            report.append({'file':c['sourcePdf'],'questions':len(c['questions']),'candidates':len(candidates),'labelsEqual':exact,'markers':candidates})
    return report

def main():
    p=argparse.ArgumentParser();p.add_argument('--questions',type=Path,required=True);p.add_argument('--repo',type=Path,default=Path('.'));p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    report=locate(json.loads(a.questions.read_text()),a.repo);a.output.write_text(json.dumps(report,indent=2)+'\n')
    count=sum(r['labelsEqual'] for r in report);print(f'{count}/{len(report)} exact chapter marker sequences')
    if count!=len(report):raise SystemExit(1)
if __name__=='__main__':main()
