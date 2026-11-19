"""Independent exact checks of domains, compositions and transformed points."""
import argparse,json
from pathlib import Path
import sympy as s
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);args=p.parse_args()
x=s.symbols('x',real=True);R=s.Rational;checks=[]
def ck(label,a,b):
 a=R(str(a)) if isinstance(a,float) else a;b=R(str(b)) if isinstance(b,float) else b
 ok=s.simplify(a-b)==0;checks.append({'check':label,'passed':bool(ok)})
 if not ok:raise AssertionError((label,a,b))
def roots(label,formula,target,values):
 for v in values:ck(label+' '+str(v),formula.subs(x,v),s.sympify(target).subs(x,v))
roots('2.1.1',s.Abs(x*x+5*x),0,[])
for v,value in [(-3,6),(2,14),(-1,4)]:ck('2.1.1 '+str(v),abs(v*v+5*v),value)
for v,value in [(1,2),(10,29),(-1,6)]:ck('2.1.2 '+str(v),abs(2-3*v)+1,value)
for a,b,vertex,yi in [(1,1,-1,1),(2,1,-R(1,2),1),(3,-4,R(4,3),4),(-2,3,R(3,2),3),(R(1,2),3,-6,3)]:
 ck('modulus vertex '+str((a,b)),abs(a*vertex+b),0);ck('modulus intercept '+str((a,b)),abs(b),yi)
for label,f,g,vs in [('2.1.4a',s.Abs(2*x-3),7,[-2,5]),('2.1.4b',s.Abs(2-5*x),3*x+5,[-R(3,8),R(7,2)]),('2.1.4c',s.Abs(3*x+2),x/2+5,[-2,R(6,5)]),('2.1.7',s.Abs(5-3*x),x,[R(5,4),R(5,2)]),('2.1.9',-s.Abs(3-x),-(x+5)/3,[1,7]),('2.3.3',s.Abs(2*x-7),2*x,[R(7,4)]),('2.5.7',3/s.Abs(x-2),4,[R(5,4),R(11,4)]),('2.7.1',2*s.Abs(x+1)-3,x+4,[-3,5]),('2.7.4',3*s.Abs(2-x)+4,x+20,[11]),('setB bronze',6-3*s.Abs(x-4),x/2+1,[R(14,5),R(34,7)]),('exam55',2*s.Abs(x+4)-2,x+3,[-3,-R(13,3)])]:roots(label,f,g,vs)
# Exact sign samples include boundary values and every linear branch interval.
for label,f,relation,predicate in [('2.1.5',s.Abs(4*x-5)-2*x,'>',lambda v:v<R(5,6) or v>R(5,2)),('2.1.6',s.Abs(4*x+3)-7,'<=',lambda v:-R(5,2)<=v<=1),('2.1.8',s.Abs(2*x-6)-(5-x),'>',lambda v:v<1 or v>R(11,3)),('2.7.2',9-3*s.Abs(x-2)-3,'<=',lambda v:v<=0 or v>=4),('2.7.6b',s.Abs(5*x-4)-(3-2*x),'>',lambda v:v<R(1,3) or v>1),('2.7.6c',s.Abs(5*x-4)-(R(8,5)-2*x),'>',lambda v:v!=R(4,5)),('setB silver',2*s.Abs(x+3)-4-(4-x/2),'<=',lambda v:-R(28,3)<=v<=R(4,5)),('exam32',s.Abs(2*x-7)+3-(x+2),'>',lambda v:v<R(8,3) or v>6)]:
 for v in [-10,-R(28,3),-3,-R(5,2),0,R(1,3),R(4,5),R(5,6),1,2,R(5,2),R(8,3),3,R(11,3),4,6,7]:
  z=f.subs(x,v);actual=bool(z>0) if relation=='>' else bool(z<=0)
  ck(label+' sign '+str(v),int(actual),int(bool(predicate(v))))
for label,a,b in [('2.2.4 left',5-(-12)/2,11),('2.2.4 right',(7-4)**2+2,11),('2.2.4 min',(4-4)**2+2,2),('2.2.5 square',(x-R(3,2))**2+R(7,4),x*x-3*x+4),('2.2.6 square',(x-4)**2-10,x*x-8*x+6),('2.2.7 square',(x-R(5,2))**2+R(7,4),x*x-5*x+8),('2.2.8 square',8-(x-5)**2,10*x-x*x-17),('2.2.8 endpoint',2+4,6),('2.2.8 right root',8-(5+s.sqrt(3)-5)**2,5),('2.3.1a',(4-2)**3,8),('2.3.1b',2**3-2,6),('2.3.1c',-1-2-2,-5),('2.3.1d',6/2-2,1),('2.3.1e',(10/2-2)**3,27),('2.3.2a',3*(4-x*x)-1,11-3*x*x),('2.3.2b',4-(1/x)**2,4-1/x**2),('2.3.2c',3*(3*x-1)-1,9*x-4),('2.3.2e',3*(4-1/x**2)-1,11-3/x**2),('2.3.3a',abs(4*(-5-1)/2-5),17),('2.3.4',2*2,2**2),('2.3.5',4*(x-1)**2-4,4*x*x-8*x),('2.3.6',8-((8-(-2-2)**2)-2)**2,-92),('2.3.8',R(9,4)/9,R(9,4)-2)]:ck(label,a,b)
roots('2.3.7',2/(x-1)**2,18,[R(2,3),R(4,3)])
# Verify rational/linear inverses by composition, separately from their stated domains.
for label,f,inv in [('2.4.1a',2*x-5,(x+5)/2),('2.4.1b',(x-3)/2,2*x+3),('2.4.1d',1-3*x,(1-x)/3),('2.4.2a',2*x-3,(x+3)/2),('2.4.2c',4/(x-3),3+4/x),('2.4.3',2/x,2/x),('2.4.5',(3*x-5)/(x-3),(3*x-5)/(x-3)),('2.4.8',(2*x+1)/(x-3),(3*x+1)/(x-2)),('setA gold',(2*x-3)/(x-1),(x-3)/(x-2)),('exam79',(2-3*x)/(x-4),(4*x+2)/(x+3))]:
 ck(label+' left inverse',f.subs(x,inv),x);ck(label+' right inverse',inv.subs(x,f),x)
for label,f,root in [('2.4.2a',2*x-3,3),('2.4.2c',4/(x-3),4),('2.4.2d',(x-1)**2-5,4),('2.4.7',x*x-6*x+8,(7+s.sqrt(17))/2)]:ck(label+' fixed point',f.subs(x,root),root)
ck('2.4.2b no fixed roots discriminant',1-8,-7);ck('2.4.8 equation',((3*x+1)/(x-2)).subs(x,R(17,5)),8)
ck('2.4.6 exponential inverse',3*(s.exp(x)+1)/3-1,s.exp(x));ck('2.4.7 inverse',(3+s.sqrt(x+1)-3)**2-1,x)
for label,fun,inputs,outputs in [('2.5.1a',x*x-x-12,[-3,4,0,R(1,2)],[0,0,-12,-R(49,4)]),('2.5.2a',6+5*s.Abs(x)-x*x,[-6,6,0,-R(5,2),R(5,2)],[0,0,6,R(49,4),R(49,4)]),('2.6.7',2*s.Abs((x+1)**2-4)+2,[-3,-1,1],[2,10,2]),('2.7.3a',2*s.Abs(x)-1,[-R(1,2),0,R(1,2)],[0,-1,0]),('2.7.3b',2-3*s.Abs(x+1),[-R(5,3),-1,-R(1,3),0],[0,2,0,-1]),('2.7.3c',5+s.Abs(x-2)/2,[2,0],[5,6]),('setB silver',2*s.Abs(x+3)-4,[-5,-3,-1,0],[0,-4,0,2])]:
 for v,expected in zip(inputs,outputs):ck(label+' value '+str(v),fun.subs(x,v),expected)
# Coordinate maps independently apply each requested horizontal and vertical change.
for label,points,h,v,expected in [('2.6.1',[(0,0),(2,8),(8,-16)],lambda a:a-3,lambda b:b+4,[(-3,4),(-1,12),(5,-12)]),('2.6.2a',[(-2,-7),(0,-2),(2,4)],lambda a:a+1,lambda b:3*b,[(-1,-21),(1,-6),(3,12)]),('2.6.2b',[(-2,-7),(0,-2),(2,4)],lambda a:2*a,lambda b:b-2,[(-4,-9),(0,-4),(4,2)]),('2.6.4a',[(1,5),(0,3)],lambda a:-a,lambda b:b+1,[(-1,6),(0,4)]),('2.6.4b',[(1,5),(0,3)],lambda a:a-2,lambda b:b+3,[(-1,8),(-2,6)]),('2.6.5a',[(3,5),(5,1)],lambda a:a,lambda b:1-3*b,[(3,-14),(5,-2)]),('2.6.6a',[(9,10),(-9,-70),(0,0)],lambda a:a-2,lambda b:R(b,2),[(7,5),(-11,-35),(-2,0)]),('2.6.6b',[(9,10),(-9,-70),(0,0)],lambda a:R(a,2),lambda b:b-3,[(R(9,2),7),(-R(9,2),-73),(0,-3)]),('2.6.8a',[(5,-2)],lambda a:a-5,lambda b:2*b,[(0,-4)]),('2.6.8b',[(5,-2)],lambda a:-a,abs,[(-5,2)]),('exam63a',[(3,-5)],lambda a:2*a,lambda b:2*b,[(6,-10)])]:
 for i,((a,b),(c,d)) in enumerate(zip(points,expected)):
  ck(label+' horizontal '+str(i),h(a),c);ck(label+' vertical '+str(i),v(b),d)
pv,q=s.symbols('p q');ck('2.7.7 other root',3*(2*pv)-pv+(8-pv),2*(2*pv)+8)
ck('setA bronze composition',2/(3-2*x**3)-5,(10*x**3-13)/(3-2*x**3));ck('setA bronze root',(10*R(4,3)-13)/(3-2*R(4,3)),1)
ck('setA silver allowed root',(5+3)**2+2,66);ck('setA silver rejected root',int(-11>-3),0)
ck('setA gold identity',(x-5)/(x*x+2*x-3)-2/(x+3)+2,(2*x-3)/(x-1));ck('setA gold composition root',2-1/(3*R(50,27)-5),R(1,5))
ck('setB bronze height',6-3*abs(0-4),-6)
# Count intersections of the two straight branches, merging a repeated vertex.
for pv in [-2,-1,-R(3,4),-R(1,2),0,1,2]:
 roots_found=set()
 if pv!=1:
  t=3/(pv-1)
  if t<=-2:roots_found.add(s.sympify(t))
 if pv!=-1:
  t=-1/(pv+1)
  if t>=-2:roots_found.add(s.sympify(t))
 expected=0 if -1<=pv<-R(1,2) else (2 if -R(1,2)<pv<1 else 1)
 ck('setB gold intersection count '+str(pv),len(roots_found),expected)
ck('exam26 factorisation',(x-2)*(3*x-2)*(2*x+1),6*x**3-13*x*x+4)
ck('exam66 identity',(2*x-7)/(x-3)+1/((x-3)*(x-2)),2-1/(x-2))
ck('exam79 g(0)',R(5,2)*0-5,-5);ck('exam79 f(g9)',(2-3*5)/(5-4),-13)
ck('exam82 derivative',s.diff(3*s.exp(3*x),x),9*s.exp(3*x));ck('exam82 root',9*s.exp(3*(s.log(R(4,9))/3)),4)
ck('exam85 inverse exponential',s.exp(-(-s.log(x-5)))+5,x)
args.output.write_text(json.dumps(checks,indent=2)+'\n');print(len(checks),'exact checks passed')
