#!/usr/bin/env python3
"""Independent exact algebra checks for the authored Pure Year 1 chapter 1.

Requires SymPy and its optional LaTeX parser in a private authoring environment.
No dependency is added to the Luisa runtime. These checks supplement the source,
subpart, graph and contextual-solution review; they do not replace that review.
"""
import json,re
import sympy as s
from sympy.parsing.latex import parse_latex
def norm(t):
 t=t.replace(r'\left','').replace(r'\right','')
 t=re.sub(r'\\sqrt\s*([A-Za-z0-9])',r'\\sqrt{\1}',t)
 t=re.sub(r'([A-Za-z])\(',r'\1\\cdot(',t)
 # TeX permits single-token fraction arguments; SymPy requires braces.
 def arg(i):
  while i<len(t) and t[i].isspace():i+=1
  if t[i]=='{':
   start=i;depth=1;i+=1
   while depth:
    if t[i]=='{':depth+=1
    if t[i]=='}':depth-=1
    i+=1
   return t[start:i],i
  return '{'+t[i]+'}',i+1
 pos=0
 while True:
  pos=t.find(r'\frac',pos)
  if pos<0:break
  a,end=arg(pos+5);b,end=arg(end)
  t=t[:pos]+r'\frac'+a+b+t[end:];pos+=5
 return t.rstrip(',')
from pathlib import Path
import argparse
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output',required=True,type=Path)
args=parser.parse_args()
p=Path(__file__).resolve().parents[1]/'resources/practice-solutions/pure-year-1/chapter-01.json'
rows=json.load(open(p))['solutions'];results=[]
for r in rows:
 for i,st in enumerate(r['steps']):
  text=st.get('latex','')
  text=text.split(';')[0].split(r'\Rightarrow')[0].split(r'\quad')[0]
  text=re.sub(r'\\ \\mathrm.*','',text)
  if text.startswith(('A=','V=','y=','x=')): text=text.split('=',1)[1]
  if any(w in text for w in ('<',r'\text',r'\ne',r'\mathrm')) or '=' not in text:continue
  terms=text.split('=')
  try:
   vals=[parse_latex(norm(t),strict=True) for t in terms]
   context={}
   if '/1.4/q9' in r['id']:context[s.Symbol('y')]=s.Symbol('x')**2/9
   roots={'/1.2/q8':3,'/1.5/q6':s.sqrt(15)+s.sqrt(3),'/1.6/q9':(2+s.sqrt(14))/2,'/problem-b/qbronze':s.Rational(1,2),'/exam/q46':20}
   if r['id'].endswith('/problem-b/qsilver'):context[s.Symbol('y')]=2
   if r['id'].endswith('/problem-b/qgold'):context[s.Symbol('u')]=3
   if r['id'].endswith('/exam/q36'):context[s.Symbol('u')]=2
   for suffix,value in roots.items():
    if r['id'].endswith(suffix) and (len(terms)==2 or terms[-1]=='0'):context[s.Symbol('x')]=value
   if terms[-1]=='0' and '/problem-b/qsilver' in r['id']:context[s.Symbol('y')]=2
   vals=[v.subs(context) for v in vals]
   diffs=[]
   for a,b in zip(vals,vals[1:]):
    dif=s.simplify(s.nsimplify(a)-s.nsimplify(b))
    if dif!=0:
     syms=dif.free_symbols
     dif=s.simplify(dif.subs({v:s.Symbol(str(v),positive=True) for v in syms}))
    diffs.append(str(dif))
   results.append({'id':r['id'],'part':i+1,'terms':terms,'differences':diffs,'passed':all(x=='0' for x in diffs)})
  except Exception as e:results.append({'id':r['id'],'part':i+1,'error':str(e)})
json.dump(results,args.output.open('w'),indent=2)
print('checks',len(results),'passed',sum(r.get('passed',False) for r in results))
for r in results:
 if not r.get('passed'):print(r)

if not all(r.get('passed',False) for r in results):
 raise SystemExit('An algebra check failed; inspect the report.')
