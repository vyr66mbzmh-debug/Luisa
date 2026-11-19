#!/usr/bin/env python3
"""Independent coordinate, direction and geometric checks for Pure 1 chapter 11."""
import argparse,json,math
from pathlib import Path
import sympy as s
checks=[]
def check(name,actual,expected):
 if isinstance(actual,s.MatrixBase):ok=actual==s.Matrix(expected)
 else:ok=s.simplify(actual-s.sympify(expected))==0
 checks.append({'case':name,'passed':bool(ok)});assert ok,(name,actual,expected)
def close(name,actual,expected,places=1):
 ok=round(float(actual),places)==expected;checks.append({'case':name,'passed':ok});assert ok,(name,actual,expected)
def V(x,y):return s.Matrix([x,y])
a=V(1,0);b=V(0,1);zero=V(0,0)
hexagon={'A':zero,'B':b-a,'C':2*b-a,'D':2*b,'E':a+b,'F':a,'O':b}
for pair,expected in [('AD',(0,2)),('EB',(-2,0)),('CB',(0,-1)),('AE',(1,1)),('OF',(1,-1)),('FC',(-2,2)),('CE',(2,-1)),('BF',(2,-1))]:check('11.1 hexagon '+pair,hexagon[pair[1]]-hexagon[pair[0]],expected)
check('11.1 midpoint PM',(a+b)/2,[s.Rational(1,2),s.Rational(1,2)])
check('11.1 midpoint SM',(a+b)/2-b,[s.Rational(1,2),-s.Rational(1,2)])
check('11.1 division YX',a/4-(a+s.Rational(2,5)*(b-a)),[-s.Rational(7,20),-s.Rational(2,5)])
k=s.symbols('k')
# Coordinate model: E=(0,0), H=a, F=b, G=b+k*a.
E=zero;H=a;F=b;G=b+k*a;M=(E+F)/2;N=(G+H)/2
check('11.1 trapezium midpoint',(N-M),(k+1)*a/2)
for name,actual,expected in [('11.2 1a',3*V(-7,3),(-21,9)),('11.2 1b',V(-7,3)-2*V(2,-5),(-11,13)),('11.2 1c',3*V(2,-5)-V(-7,3),(13,-18)),('11.2 2a',V(-2,4)/2,(-1,2)),('11.2 2b',V(-2,4)+V(6,-1)+V(-3,-5),(1,-2)),('11.2 2c',V(-3,-5)+2*V(6,-1)-s.Rational(3,2)*V(-2,4),(12,-13)),('11.2 3',V(-6,7)+V(3,-5),(-3,2)),('11.2 4',V(11,-1)-V(-8,7),(19,-8)),('11.2 5',2*V(-3,-4)-V(-8,11),(2,-19)),('11.2 6 first',2*V(-2,7)+5*V(3,-2),(11,4)),('11.2 6 second',2*V(2,-2)-V(-1,-6),(5,2)),('11.2 7',V(4,7)-V(14,-3),(-10,10))]:check(name,actual,expected)
check('11.2 nonparallel determinant',s.det(s.Matrix.hstack(V(11,4),V(5,2))),2)
for name,xy,v in [('11.3 1a',(6,-8),10),('11.3 1b',(5,4),s.sqrt(41)),('11.3 1c',(-3,6),3*s.sqrt(5)),('11.3 1d',(-8,-8),8*s.sqrt(2)),('11.3 3',(-5,12),13),('11.4 3a',(-6,8),10),('11.4 3b',(9,-3),3*s.sqrt(10)),('11.4 3c',(3,5),s.sqrt(34)),('11.4 4b',(-4,5),s.sqrt(41)),('11.6 1a',(5,-12),13),('11.6 1b',(-6,-8),10),('11.6 1c',(6,1),s.sqrt(37)),('11.6 1d',(0,14),14),('11.6 2a',(-4,3),5),('11.6 4b',(9,-16),s.sqrt(337)),('11.6 5b',(11,-4),s.sqrt(137)),('11.6 6c',(6,-9),3*s.sqrt(13)),('exam16 separation',(14,-10),2*s.sqrt(74))]:check(name,s.sqrt(V(*xy).dot(V(*xy))),v)
for name,xy,expected in [('11.3 2a',(2,4),63.4),('11.3 2b',(-7,-1),188.1),('11.3 2c',(0,6),90),('11.3 2d',(5,-5),315),('11.6 8a',(8,32),76),('exam5 direction',(6,-3),333.4)]:close(name,math.degrees(math.atan2(xy[1],xy[0]))%360,expected)
check('11.3 4 components',V(50*s.cos(s.pi/4),-50*s.sin(s.pi/4)),[25*s.sqrt(2),-25*s.sqrt(2)])
close('11.3 5 p',11*s.sin(s.pi/9),3.76,2);close('11.3 5 q',11*s.cos(s.pi/9),10.3)
for p in [-7,7]:check('11.3 6 p'+str(p),V(2*p,3*p).dot(V(2*p,3*p)),637)
check('11.3 7 OB',V(5,4)+V(7,-4),(12,0));check('11.3 7 OC',V(12,0)-V(10,7),(2,-7))
close('11.3 7 AOC',math.degrees(math.atan2(4,5)-math.atan2(-7,2)),112.7)
for p,q in [(6,s.Rational(-5,2)),(-6,s.Rational(5,2))]:check('11.3 8 length '+str(p),p*p+q*q,s.Rational(169,4));check('11.3 8 ratio '+str(p),q/p,-s.Rational(5,12))
for name,actual,expected in [('11.4 1c',V(7,0)-V(-2,3),(9,-3)),('11.4 2b',V(1,3)-V(-1,-1),(2,4)),('11.4 2c',V(6,-2)-V(1,3),(5,-5)),('11.4 3c position',V(-6,8)-V(-9,3),(3,5)),('11.4 4a',V(-7,-6)+V(3,11),(-4,5)),('11.5 1d',a+(b-a)/4,[s.Rational(3,4),s.Rational(1,4)]),('11.5 2',a+s.Rational(2,5)*(b-a),[s.Rational(3,5),s.Rational(2,5)]),('11.5 3',s.Rational(2,5)*(b-s.Rational(3,4)*a),[-s.Rational(3,10),s.Rational(2,5)]),('11.5 5',b/2-a/2,(b-a)/2),('11.6 3',(V(2,-51)-V(-7,-24))/6,[s.Rational(3,2),-s.Rational(9,2)]),('11.6 4',V(1,-4)+4*V(2,-3),(9,-16))]:check(name,actual,expected)
for x,y in [(s.Rational(22,5),s.Rational(29,5)),(-2,-7)]:check('11.4 5 line '+str(x),y,2*x-3);check('11.4 5 radius '+str(x),x*x+y*y,53)
W=a/3;Y=2*a/3+b;X=a+b/2;Z=b/2
check('11.5 6 WY',Y-W,a/3+b);check('11.5 6 XZ',Z-X,-a);check('11.5 6 midpoint coincidence',(W+Y)/2,(X+Z)/2)
check('11.5 7 parallel',(a+k*b)/(1+k)-a/(1+k),k*b/(1+k));check('11.5 7 ratio at k=1/2',s.Rational(1,2)/(1+s.Rational(1,2)),s.Rational(1,3))
# Independent dot product for angles; authoring uses the cosine rule.
for name,u,v,expected in [('11.5 4',(8,1),(2,-6),78.7),('problemA bronze',(5,12),(12,5),44.8),('problemA silver',(1,4),(8,5),44.0),('exam56',(-8,1),(-5,8),50.9)]:
 u=V(*u);v=V(*v);close(name,180*s.acos(u.dot(v)/(u.norm()*v.norm()))/s.pi,expected)
# Independent coordinate determinants for all three triangle-area problems.
for name,u,v,expected in [('11.6 7',(-3,5),(6,1),s.Rational(33,2)),('problemA silver',(1,4),(8,5),s.Rational(27,2)),('problemA gold',(8,-2),(2,-7),26)]:check(name,abs(s.det(s.Matrix.hstack(V(*u),V(*v))))/2,expected)
close('11.6 5 bearing',90+math.degrees(math.atan2(4,11)),110.0)
check('11.6 6 elimination',3*(2*k-3)+2*(-3*k+7),5)
check('11.6 8 force balance',V(11,25)+V(-3,7),(8,32));check('11.6 8 third force',V(8,32)+V(-8,10),(0,42))
check('problemB bronze OP',5*(a+s.Rational(3,5)*(b-a)),2*a+3*b);check('problemB bronze collinear',(2*a+3*b)-b,2*(b+a))
check('problemB silver B two routes',a+(3*b-a)/5,2*a+s.Rational(3,5)*(b-2*a))
P=4*a/5;Q=2*a/5+b;M=b/2;C=a+b
check('problemB gold midpoint intersection',P+s.Rational(3,4)*(Q-P),(M+C)/2)
check('exam14 zero vertical',3*s.Rational(5,3)-5,0);check('exam14 force',6+4*s.Rational(5,3),s.Rational(38,3))
check('exam19 line',3*8+2*(-6),12);check('exam19 radius',8**2+(-6)**2,100)
P=a+3*b/5;Q=3*b/5;Z=3*(a+b)/5
check('exam80 CZ',Z-b,3*a/5-2*b/5);check('exam80 AP ratio',s.Rational(3,5)/s.Rational(2,5),s.Rational(3,2));check('exam80 PZ division',P+s.Rational(2,5)*(Q-P),Z)
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args();args.output.write_text(json.dumps(checks,indent=2));print(len(checks),'independent checks passed')
