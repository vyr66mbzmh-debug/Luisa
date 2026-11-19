"""Independent exact coordinate-geometry checks for practice Pure Year 1 ch6."""
import argparse,json
from pathlib import Path
import sympy as s
p=argparse.ArgumentParser();p.add_argument('--output',required=True,type=Path);args=p.parse_args()
x,y,k=s.symbols('x y k');checks=[]
def ck(label,a,b=0):
    value=s.simplify(a-b);checks.append({'check':label,'passed':value==0})
    if value!=0:raise AssertionError((label,value))
def midpoint(A,B):return tuple((s.sympify(a)+b)/2 for a,b in zip(A,B))
def d2(A,B):return sum((s.sympify(a)-b)**2 for a,b in zip(A,B))
def at(label,eqs,P):
    for i,e in enumerate(eqs):ck(label+' '+str(i),s.sympify(e).subs({x:P[0],y:P[1]}))
def bisect(label,A,B,coeffs):
    a,b,c=coeffs;M=midpoint(A,B)
    ck(label+' midpoint',a*M[0]+b*M[1]+c)
    ck(label+' perpendicular',-b*(B[0]-A[0])+a*(B[1]-A[1]))
for label,A,B,line in [
('6.1 q2a',(-3,4),(1,-8),(1,-3,-5)),('6.1 q2b',(3,-5),(-7,15),(1,-2,12)),('6.1 q2c',(2,-3),(-6,-9),(4,3,26)),('6.1 q5a',(-1,-3),(5,7),(3,5,-16)),('6.1 q5b',(5,7),(7,-5),(1,-6,0)),('6.1 q6',(3,8),(-1,-4),(1,3,-7)),('6.1 q8',(7,-3),(3,19),(2,-11,78)),('6.3 q7',(-2,11),(9,10),(11,-1,-28)),('6.4 q3',(2,8),(-7,9),(9,-1,31)),('6.4 q4',(-2,7),(-8,5),(3,1,9)),('6.4 q7',(1,10),(7,8),(3,-1,-3)),('6.4 q8',(-2,3),(8,5),(5,1,-19)),('6.4 q9',(3,3),(7,-5),(1,-2,-7)),('6.5 q1ab',(-1,6),(3,4),(2,-1,3)),('6.5 q1bc',(3,4),(5,2),(1,-1,-1)),('6.5 q1ac',(-1,6),(5,2),(3,-2,2)),('exam87',(2,-3),(8,5),(3,4,-19))]:bisect(label,A,B,line)
at('6.1 q5 intersection',[3*x+5*y-16,x-6*y],(s.Rational(96,23),s.Rational(16,23)))
for label,original,centre,r2 in [
('6.2 q3',x*x+y*y+8*x-12*y-15,(-4,6),67),('6.2 q6',x*x+y*y-6*x+10*y-16,(3,-5),50),('6.2 q8',x*x+y*y+4*x-6*y-61,(-2,3),74),('6.3 q8',x*x+y*y-10*x+8*y+25,(5,-4),16),('6.4 q1',x*x+y*y-6*x+4*y-156,(3,-2),169),('6.4 q3',x*x+y*y+6*x-8*y-16,(-3,4),41),('6.4 q5',x*x+y*y-2*x+8*y+4,(1,-4),13),('6.4 q9',x*x+y*y-2*x+6*y-30,(1,-3),40),('6.5 q5',x*x+y*y-10*x+6*y-91,(5,-3),125),('6.5 q6',x*x+y*y-4*x+8*y-33,(2,-4),53),('6.5 q7',x*x+y*y+4*x-6*y-23,(-2,3),36),('exam58',x*x+y*y-8*x+12*y+16,(4,-6),36),('exam70',x*x+y*y-10*x+6*y-11,(5,-3),45)]:ck(label+' completing square',original, (x-centre[0])**2+(y-centre[1])**2-r2)
for label,circle,line,points in [
('6.3 q2',(x-1)**2+y*y-50,2*x+y-7,[(0,7),(6,-5)]),('6.3 q3',(x+2)**2+(y-4)**2-45,2*x+y-15,[(4,7)]),('6.3 q5',x*x+y*y-100,3*x+y-10,[(0,10),(6,-8)]),('6.3 q7',(x-3)**2+(y-5)**2-61,x+11*y-119,[(-2,11),(9,10)]),('6.4 q7',(x-3)**2+(y-6)**2-20,y-3*x+3,[(3+s.sqrt(2),6+3*s.sqrt(2)),(3-s.sqrt(2),6-3*s.sqrt(2))]),('setA bronze',x*x+(y-5)**2-100,2*x+y-1,[(-6,13),(s.Rational(14,5),-s.Rational(23,5))]),('setA silver',(x-5)**2+(y-1)**2-25,3*x+4*y-44,[(8,5)]),('exam28',x*x+(y+2)**2-16,x*x+(y+5)**2-16,[(s.sqrt(55)/2,-s.Rational(7,2)),(-s.sqrt(55)/2,-s.Rational(7,2))])]:
    for P in points:at(label,[circle,line],P)
# Tangents must pass through a circle point and be perpendicular to its radius.
for label,C,P,r2,line in [('6.4 q1',(3,-2),(-2,10),169,(5,-12,130)),('6.4 q2',(8,2),(4,-6),80,(1,2,8)),('6.4 q9',(1,-3),(7,-5),40,(3,-1,-26)),('exam82',(5,3),(13,9),100,(4,3,-79))]:
    a,b,c=line;ck(label+' on circle',d2(C,P),r2);ck(label+' tangent point',a*P[0]+b*P[1]+c);ck(label+' perpendicular',-b*(P[0]-C[0])+a*(P[1]-C[1]))
ck('6.4 q5 invalid point squared distance',d2((1,-4),(3,-9)),29)
ck('6.4 q5 supplied line squared distance',s.Rational((2*1-5*(-4)-51)**2,2**2+(-5)**2),29)
at('6.4 q9 intersection',[3*x-y-26,x-2*y-7],(9,1))
for label,centre,points,r2 in [('6.5 q1',(-4,-5),[(-1,6),(3,4),(5,2)],130),('6.5 q2',(-2,5),[(-12,1),(8,9),(2,15)],116),('6.5 q3',(3,-2),[(6,3),(-2,1),(0,-7)],34),('6.5 q4',(6,4),[(6,14),(14,10),(-4,4)],100),('6.5 q9',(4,5),[(-4,4),(8,12),(12,6)],65),('exam87',(13,-5),[(2,-3),(8,5),(18,-15)],125),('exam92',(3,-2),[(8,10),(16,-2)],169)]:
    for P in points:ck(label+' radius to '+str(P),d2(centre,P),r2)
ck('6.5 q3 equal legs',d2((6,3),(-2,1)),d2((-2,1),(0,-7)))
ck('6.5 q3 right angle',d2((6,3),(-2,1))+d2((-2,1),(0,-7)),d2((6,3),(0,-7)))
ck('6.3 q4 discriminant',s.discriminant((x-5)**2+(2*x+4)**2-30,x),-184)
ck('6.3 q6 discriminant',s.discriminant(2*x*x+2*(k-3)*x+k*k-23,x),-4*(k+11)*(k-5))
ck('6.3 q8 discriminant',s.discriminant((1+k*k)*x*x+(8*k-10)*x+25,x),-4*k*(9*k+40))
ck('exam58 discriminant',s.discriminant((1+k*k)*x*x+(12*k-8)*x+16,x),16*k*(5*k-12))
for label,C,r,half,ycoord,tangent in [('bronze',(2,-3),5,4,-6,s.Rational(20,3)),('silver',(4,-5),s.Rational(25,2),12,-s.Rational(17,2),s.Rational(300,7)),('gold',(3,-2),s.Rational(17,2),s.Rational(15,2),-6,s.Rational(255,16))]:
    h=s.sqrt(r*r-half*half);ck(label+' chord height',C[1]-h,ycoord);ck(label+' tangent length',r*half/h,tangent)
ck('exam82 chord',2*s.sqrt(100-25),10*s.sqrt(3))
ck('exam87 area',s.sqrt(d2((2,-3),(8,5)))*s.sqrt(d2((2,-3),(18,-15)))/2,100)
args.output.write_text(json.dumps(checks,indent=2)+'\n');print(len(checks),'exact checks passed')
