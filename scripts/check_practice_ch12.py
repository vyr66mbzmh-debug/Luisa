"""Exact checks of differentiation, stationary points and models; requires SymPy."""
import argparse,json
from pathlib import Path
import sympy as s
parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
x,h=s.symbols('x h',positive=True);p,q,a,b,c=s.symbols('p q a b c');R=s.Rational
checks=[]
def ck(label,actual,expected):
 ok=s.simplify(actual-expected)==0
 checks.append({'check':label,'passed':bool(ok)})
 if not ok:raise AssertionError((label,actual,expected))
def derivative(label,f,d):
 ck(label,s.limit((f.subs(x,x+h)-f)/h,h,0),d)
def value(label,f,v,result):ck(label,f.subs(x,v),result)
def stationary(label,f,v,y,kind=None):
 value(label+' derivative',s.diff(f,x),v,0);value(label+' ordinate',f,v,y)
 if kind: ck(label+' second derivative sign',s.sign(s.diff(f,x,2).subs(x,v)),kind)
for j,(f,d) in enumerate([(12*x,12),(2*x*x,4*x),(8*x,8),(3*x*x,6*x),(x**3,3*x*x),(6-3*x*x,-6*x),(x**5,5*x**4),(x**-6,-6*x**-7),(s.sqrt(x),x**-R(1,2)/2),(x**-R(1,4),-x**-R(5,4)/4),(5*x**4,20*x**3),(5*x**-2,-10*x**-3),(3*x*x/(12*x**5),-R(3,4)*x**-4),(9*x**-R(2,3),-6*x**-R(5,3)),(3*x*x-7*x+12,6*x-7),(R(3,4)*x*x+x/2-1,3*x/2+R(1,2)),(12-5*x*x,-10*x),(8*x**R(5,2)-4*x*x-6*x**R(1,3),20*x**R(3,2)-8*x-2*x**-R(2,3)),(1/(7*x*x)+x**R(1,4),-R(2,7)*x**-3+x**-R(3,4)/4),(x*(2*x*x-6*x+5),6*x*x-12*x+5),((x*x-2)*(x+2/x),3*x*x+4/x**2),((6*x**R(5,2)-8*x**R(3,2))/s.sqrt(x),12*x-8),(4*x**4-x**R(1,3)+(1-x**5)/x**3,16*x**3-x**-R(2,3)/3-3*x**-4-2*x),((x*x-3)*(5-x**3),-5*x**4+9*x*x+10*x)]):derivative('difference quotient '+str(j),f,d)
for label,f,v,ans in [('12.3.3a',2*x**3,3,54),('12.3.3b',2*x**3,-5,150),('12.3.3c',2*x**3,R(1,2),R(3,2)),('12.3.3d',2*x**3,R(3,4),R(27,8)),('12.3.4',5/x**3,2,-R(15,16)),('12.3.5',-8/s.sqrt(x),16,R(1,16)),('12.3.6',2*x**4,R(3,2),27),('12.3.7',4*x**R(2,3),27,R(8,9)),('12.4.2a',-4*x*x+11*x-1,2,-5),('12.4.2b',3*x*x-20,4,24),('12.4.2c',18+7*x/2-x*x/4,8,-R(1,2)),('12.4.3',2*x*x-3*x+4,3,9),('12.4.4',(2-x)*(2+x),5,-10),('12.4.5',6*x*x-5*x+3,-2,-29),('12.5.4a',x**4/2-8*x*x+2,-2,16),('12.5.4b',6/s.sqrt(x)-3*x-2*x*x,1,-10),('12.5.5',(4*x*x-8*x)/x**3,-2,-3),('12.5.6',R(5,2)*x*x-20*s.sqrt(x),4,15)]:value(label,s.diff(f,x),v,ans)
H=R(95,11)*x**3+4*R(95,11)*x-R(24,11)/x**3
value('12.5.7 function',H,-1,-41);value('12.5.7 derivative',s.diff(H,x),-1,67)
for label,f,v,m,c0,normal in [('12.6.1a',x**3-4*x*x,2,-4,0,False),('12.6.1b',4/x-3*x*x,-2,11,8,False),('12.6.1c',6*x**R(3,2)-4*s.sqrt(x),4,17,-28,False),('12.6.1d',(12-x*x)/(2*x),-3,-R(7,6),-4,False),('12.6.2a',x*x/2+6/x,3,-R(3,7),R(109,14),True),('12.6.2b',4/x-3*x*x,4,R(4,97),-R(4575,97),True),('12.6.3t',10-2*x-x*x,1,-4,11,False),('12.6.3n',10-2*x-x*x,1,R(1,4),R(27,4),True),('12.6.4t',x*x-5*x+4,5,5,-21,False),('12.6.4n',x*x-5*x+4,3,-1,1,True),('12.6.5',x**3-4*x,-1,-1,2,False),('12.6.6',x*x/2-8*x+6,6,R(1,2),-27,True),('12.6.7t',s.sqrt(x)+1/s.sqrt(x),4,R(3,16),R(7,4),False),('12.6.7n',s.sqrt(x)+1/s.sqrt(x),4,-R(16,3),R(143,6),True)]:
 value(label+' point',f,v,m*v+c0);t=s.diff(f,x).subs(x,v);ck(label+' slope',m*t if normal else t,-1 if normal else m)
value('12.6.6 second intersection',x*x/2-8*x+6,11,-R(43,2));ck('12.6.7 area',R(1,2)*(R(143,6)-R(7,4))*4,R(265,6))
for f,d in [(9*x*x-6*x+7,18),(-x**3+4/x,-6*x+8*x**-3),(4*x**-R(1,2)+8*x**R(3,2),3*x**-R(5,2)+6*x**-R(1,2)),(6/x**3-x**4/2-9*x,72*x**-5-6*x*x),(8*x**-R(1,4)-x**R(1,6)-7,R(5,2)*x**-R(9,4)+R(5,36)*x**-R(11,6))]:ck('second derivative '+str(f),s.diff(f,x,2),d)
value('12.8.4',s.diff(1/x-6*x-2*x**3,x,2),-2,R(95,4))
F=-3*x**3+5*x*x-8*x+6
value('12.8.6 first',s.diff(F,x),2,-24);value('12.8.6 second',s.diff(F,x,2),-5,100)
G=-R(2,5)*x**3+R(3,10)*x*x+6*x-1
for v in [-2,R(5,2)]:value('12.8.7 root '+str(v),s.diff(G,x),v,0)
for label,f,v,y,k in [('12.9.1',(x-4)*(x-8),6,-4,1),('12.9.2a',x*x-6*x+8,3,-1,1),('12.9.2b',x*x-3*x-11,R(3,2),-R(53,4),1),('12.9.2c',3*x*x+2*x+1,-R(1,3),R(2,3),1),('12.9.3a',8-16*x-x*x,-8,72,-1),('12.9.3b',12*x-4*x*x,R(3,2),9,-1),('12.9.3c',18-30*x-7*x*x,-R(15,7),R(351,7),-1),('12.9.4a',-4*x**3+6*x*x+24*x+3,-1,-11,1),('12.9.4b',-4*x**3+6*x*x+24*x+3,2,43,-1),('12.9.5',-x**3-6*x*x-12*x-6,-2,2,None),('12.9.6a',2*x**3-x*x/2-x+2,-R(1,3),R(119,54),None),('12.9.6b',2*x**3-x*x/2-x+2,R(1,2),R(13,8),None),('12.9.7',54/x+4*s.sqrt(x),9,18,1),('12.9.8',-2*x**3+4*x*x+8*x-10,2,6,-1),('12.9.9',x**3-3*x*x+3*x+4,1,5,None),('setA bronze',14+6*x-x*x,3,23,-1),('setA silver1',-x**3-3*x*x+4,-2,0,1),('setA silver2',-x**3-3*x*x+4,0,4,-1),('setA gold1',R(2,3)*x**R(3,2)-10*s.sqrt(x)-8/s.sqrt(x),1,-R(52,3),-1),('setA gold2',R(2,3)*x**R(3,2)-10*s.sqrt(x)-8/s.sqrt(x),4,-R(56,3),1),('exam15',s.sqrt(x)/3+3/s.sqrt(x),9,2,1),('exam50',4-2*s.sqrt(x)+x*x/2,1,R(5,2),1)]:stationary(label,f,v,y,k)
for label,f,v,result in [('fence',80*x-(1+2*s.sqrt(2))*x*x,40/(1+2*s.sqrt(2)),1600/(1+2*s.sqrt(2))),('cylinder',2048*s.pi/x+64*s.pi*s.sqrt(x),16,384*s.pi),('box',(608*x-2*x**3)/3,s.sqrt(R(304,3)),R(1216,9)*s.sqrt(R(304,3))),('bin',s.pi*x*(2400-5*x*x)/6,4*s.sqrt(10),3200*s.pi*s.sqrt(10)/3),('riding',150*x-s.pi*x*x/4,300/s.pi,22500/s.pi),('cardboard',x*(60-2*x)*(36-2*x),16-2*s.sqrt(19),1792+1216*s.sqrt(19))]:stationary(label,f,v,result,-1 if label!='cylinder' else 1)
for v in [R(1,16),R(81,16)]:value('exam11 gradient '+str(v),16*x-40*s.sqrt(x)+5,v,-4)
F=R(8,9)*x**3-R(5,3)*x*x+x
value('exam27 derivative1',s.diff(F,x),-1,7);value('exam27 derivative2',s.diff(F,x),2,5);value('exam27 second',s.diff(F,x,2),1,2)
ck('setB bronze intersection',-3*R(11,7)+3,-R(12,7));ck('setB bronze intersection2',4*R(11,7)-8,-R(12,7));ck('setB silver intersection',-R(1,3)*(-4)-R(1,3),1);ck('setB silver intersection2',-R(1,6)*(-4)+R(1,3),1)
value('setB gold derivativeA',x*x/2+2*x/3-R(4,3),-4,4);value('setB gold derivativeB',x*x/2+2*x/3-R(4,3),2,2);ck('setB gold normal intersectionA',-R(1,4)*(8+4),-3);ck('setB gold normal intersectionB',-R(1,2)*(8-2),-3)
args.output.write_text(json.dumps(checks,indent=2)+'\n');print(len(checks),'exact checks passed')
