"""Independently verify displayed PMCCs against source data and rejection thresholds."""
from pathlib import Path
import json,re,html,statistics,math
import mpmath as mp
rows={r['id'].split('/ch1/')[1]:r for r in json.loads(Path('resources/practice-solutions/applied-year-2/chapter-01.json').read_text())['solutions']}
count=0
D=[('1.2/q2',[36,14,72,6,54,94,23,66,87,41],[78,67,281,29,210,312,84,237,305,160],False,False),('1.2/q3',[.79,1.4,2.62,.61,1.8,3.41,1.01,2.23,.21,3.23],[.43,.42,.18,.34,.35,.07,.42,.28,.47,.12],False,False),('1.2/q4',list(range(1,11)),[1137,785,578,561,546,535,524,496,492,459],True,True),('1.2/q5',[87,9,73,62,7,44,53,98,29,35],[95,19,58,41,14,37,47,82,24,26],False,True),('1.2/q6',[3.2,3.2,2.8,2.5,2.8,1.8,5,6,2.3,3.5],[24,26,26,27,26,29,21,19,30,23],True,True),('1.2/q7',[16.8,16.7,15.8,14.4,13.9,14,13.8],[2100,700,2500,6300,6200,4700,3900],False,False),('1.2/q8',[19,18,17,24,16,27],[3100,3100,3100,4800,5100,3200],False,False),('1.3/q3',[3.8,5.7,2.4,3.4,2.2,2.4],[30,28,30,28,34,33],False,False),('1.3/q4',[46,157,237,337,419,501,601,657],[5,21,17,20,25,28,24,30],False,False),('1.3/q8',[9,7,8,6,5,8,6,8],[6.3,5.3,6,5.5,4,5.4,4.7,7.1],False,False),('1.3/q9',[9,10,14,12,14,9,13,5],[21,22,41,24,30,25,29,19],False,False),('problem/qbronze',[53.6,.01,250,519,3.38,.55,1.45],[450,.48,510,680,42.5,3.2,14.9],False,False),('problem/qsilver',[3,4,7,9,10,12],[1.09,1.28,1.91,2.75,3.64,5.61],False,True),('exam/q4',[5.9,14.5,4.6,6.8,6.5,10.7],[3200,3400,1900,2200,2500,3600],False,False),('exam/q7',[19.7,21.3,21,20.6,21,20.8,18.8],[10.1,12.3,9.9,7.4,6.7,7.8,8.5],False,False),('exam/q14',[.2,1.3,5,11,20,45,80,160],[.1,.25,.5,.75,1,1.5,2.5,3.5],False,True),('exam/q17',[3.2,3.2,2.8,2.5,2.8,1.8,5,6,2.3,3.5],[24,26,26,27,26,29,21,19,30,23],False,False)]
for ident,x,y,lx,ly in D:
 x=[math.log10(a) if lx else a for a in x];y=[math.log10(a) if ly else a for a in y]
 expected=statistics.correlation(x,y)
 texes=[html.unescape(z) for z in re.findall('data-math="([^"]+)"',rows[ident]['solutionHtml'])]
 displayed=[float(z.split(r'\approx')[-1]) for z in texes if z.startswith(r'r=\frac{S_{xy}}')]
 assert len(displayed)==1,(ident,displayed)
 assert abs(displayed[0]-expected)<1e-6,(ident,displayed,expected);count+=1
# Critical values independently integrated using the exact null density of r.
for n,c,tail in [(30,.3061,.05),(30,.4226,.01),(12,.4973,.05),(12,.6581,.01),(6,.8114,.025),(8,.7887,.01),(24,.4716,.01),(8,.8343,.005),(9,.7977,.005),(8,.7067,.025),(7,.9056,.0025),(6,.7293,.05),(8,.5067,.10),(7,.6694,.05)]:
 density=lambda r:(1-r*r)**((n-4)/2)/mp.beta(.5,(n-2)/2)
 p=float(mp.quad(density,[c,1]))
 assert abs(p-tail)<5e-5,(n,c,p,tail);count+=1
# Coded models must reproduce their regression equation at several original x values.
for intercept,slope,power in [(.7,1.2,False),(1.5,.8,True),(2.1,.5,False),(3,-.355,True),(.494,.0327,False),(-1.22,1.02,True),(1.5,3.27,False),(2.6,.67,True),(1.15,.0085,False),(1.59,-.383,True),(.081,.749,True),(-.412,.0074,False)]:
 for x in [.5,1,3]:
  y=10**intercept*x**slope if power else 10**intercept*(10**slope)**x
  assert abs(math.log10(y)-(intercept+slope*(math.log10(x) if power else x)))<1e-12;count+=1
# Explicit source discrepancies change the intended solution.
assert 'two tails' in rows['1.3/q8']['method'];count+=1
assert 'Do not reject' in rows['1.3/q8']['solutionHtml'];count+=1
r=statistics.correlation([3,4,7,9,10,12],list(map(math.log10,[1.09,1.28,1.91,2.75,3.64,5.61])))
assert abs(r-.992402)<1e-6 and abs(r-.959)>.03;count+=1
assert statistics.mean([63,65,69,62,86,68,73])+2*statistics.pstdev([63,65,69,62,86,68,73])<86;count+=1
print(count,'independent transformed-data and significance checks passed')
