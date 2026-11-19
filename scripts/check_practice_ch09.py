#!/usr/bin/env python3
"""Independent triangle, bearing, symbolic and graph checks for Pure 1 chapter 9.

Triangle side checks use Cartesian endpoints; areas additionally use determinants
or Heron's formula. Reference rounded answers are fixed from source comparison.
"""
import argparse,json,math
from pathlib import Path
import sympy as s
checks=[]
def trig(d):return math.cos(math.radians(d)),math.sin(math.radians(d))
def sn(d):return trig(d)[1]
def cs(d):return trig(d)[0]
def asi(v):return math.degrees(math.asin(v))
def aco(v):return math.degrees(math.acos(v))
def check(name,ok):checks.append({'case':name,'passed':bool(ok)});assert ok,name
def close(name,v,expected,sf=3,dp=None):
 got=round(v,dp) if dp is not None else float(format(v,f'.{sf}g'));check(name,abs(got-expected)<1e-8)
def side(a,b,C):return math.hypot(a-b*cs(C),b*sn(C))
def heron(a,b,c):p=(a+b+c)/2;return math.sqrt(p*(p-a)*(p-b)*(p-c))
def bearing(E,N):return math.degrees(math.atan2(E,N))%360
def pos(dist,brg):return dist*sn(brg),dist*cs(brg)
for name,a,b,C,out in [('9.1 1',7.2,9.3,110,13.6),('9.1 3a',3.6,5.2,30,2.75),('9.1 3b',1.8,3.1,110,4.08),('9.1 3c',5.8,6.2,50,5.08),('9.1 4',40,48,30,24.1),('9.1 6',600,800,20,313),('9.4 7a',10,6.5,120,14.4)]:close(name,side(a,b,C),out)
for name,a,b,c,out in [('9.1 2',5,6.5,10,120),('9.1 3d',5,9,12,115),('9.1 3e',4.9,7.1,7.1,69.8),('9.1 3f',9.3,10.4,18.2,135)]:close(name,aco((a*a+b*b-c*c)/(2*a*b)),out)
check('9.1 5 exact cosine',s.Rational(25+36-64,60)==-s.Rational(1,20));check('9.1 7 acute',12**2<7**2+10**2)
AC=side(8,10,80);close('9.1 8 perimeter',27+math.sqrt(AC*AC-81),34.4)
x=s.symbols('x');check('9.1 9 polynomial',s.expand(4*((x+2)**2+(x+1)**2-x*x)-6*(x+2)*(x+1))==-2*(x*x-3*x-4));check('9.1 9 root',s.Rational(6**2+5**2-4**2,2*6*5)==s.Rational(3,4))
for name,a,A,B,out in [('9.2 1a',10,80,45,7.18),('9.2 1b',25,100,12,5.28),('9.2 1c',14,70,85,14.8)]:close(name,a*sn(B)/sn(A),out)
close('9.2 2a',asi(7*sn(95)/10),44.2);close('9.2 2b',asi(9*sn(65)/12),42.8);close('9.2 2c',80-asi(6.8*sn(100)/12.5),47.6)
D=asi(AC*sn(35)/7);close('9.2 3 acute',D,73);close('9.2 3 CD',7*sn(145-D)/sn(35),11.6);close('9.2 3 second CD',7*sn(D-35)/sn(35),7.51)
for d in [D,180-D]:check('9.2 3 alternative residual '+str(round(d)),abs(side(AC,7*sn(145-d)/sn(35),35)-7)<1e-10)
C=asi(6*sn(40)/4);close('9.2 4 acute',C,74.6,dp=1);close('9.2 4 obtuse',180-C,105.4,dp=1)
close('9.2 5',130-asi(18*sn(50)/20),86.4,dp=1);close('9.2 6 sine',9*sn(25)/8,.475,dp=3);close('9.2 6 acute',asi(9*sn(25)/8),28.39,dp=2);close('9.2 6 obtuse',180-asi(9*sn(25)/8),151.61,dp=2)
# Solve the ray-circle intersection independently in Cartesian coordinates.
# C lies on bearing45: C=t*(sin45,cos45), and |C-B|=14.
BE,BN=pos(6,15);dot=BE*sn(45)+BN*cs(45);t=dot+math.sqrt(dot*dot+14**2-6**2)
close('9.2 7a Cartesian',t,18.9);close('9.2 7b Cartesian',bearing(t*sn(45)-BE,t*cs(45)-BN),57,dp=0)
th=asi(4*sn(115)/7);close('9.2 8a',th,31.2);close('9.2 8b',7*sn(115+th)/sn(50-th),12.1);close('9.2 8c',7*sn(15)/sn(50-th),5.62)
r=(11+5*s.sqrt(3))/8;check('9.2 9 exact',s.simplify((4*r-3)/(s.sqrt(3)/2)-(2*r+1)/s.Rational(3,4))==0)
for name,a,b,C,out in [('9.3 1a',4.6,6.5,50,11.5),('9.3 1b',5.8,7.2,110,19.6),('9.3 1c',8.4,10.3,75,41.8)]:close(name,heron(a,b,side(a,b,C)),out)
for name,ar,a,b,out1,out2 in [('9.3 2a',8.2,4.5,6.8,32.4,148),('9.3 2b',300,25,30,53.1,127),('9.3 2c',8.2,10.4,10.3,8.81,171)]:v=asi(2*ar/(a*b));close(name+' acute',v,out1);close(name+' obtuse',180-v,out2)
close('9.3 3 obtuse perimeter',155+side(75,80,150),305);close('9.3 3 acute perimeter',155+side(75,80,30),195)
BC=16.4*sn(75)/sn(52);AB=16.4*sn(53)/sn(52);close('9.3 4a',BC,20.1,dp=1);close('9.3 4b Heron',heron(16.4,BC,AB),132,dp=0)
check('9.3 5 complete square',s.expand((18+3*x-x*x)/5-(s.Rational(81,20)-(x-s.Rational(3,2))**2/5))==0)
root=(-9+math.sqrt(49617))/36;close('9.3 6 positive x',root,5.94);check('9.3 6 residual',abs(.5*3*root*(2*root+1)*3/8-43)<1e-10)
AC=20*sn(70)/sn(30);BC=20*sn(80)/sn(30);close('9.3 7 Heron',heron(20,AC,BC),370)
X=asi(5.4*sn(65)/6.7);Y=115-X
for name,val,out in [('9.4 1a x',X,46.9),('9.4 1a y',Y,68.1),('9.4 1a z',6.7*sn(Y)/sn(65),6.86),('9.4 1b x',180-75-52,53),('9.4 1b y',15.2*sn(52)/sn(75),12.4),('9.4 1b z',15.2*sn(53)/sn(75),12.6),('9.4 1c x',180-25-110,45),('9.4 1c y',24*sn(25)/sn(110),10.8),('9.4 1c z',24*sn(45)/sn(110),18.1)]:close(name,val,out)
D=aco(-23/110);close('9.4 2a',11*sn(D-50)/sn(50),11.3)
C=180-asi(15*sn(25)/9);D=155-C;close('9.4 2b',15*sn(D)/sn(145-D),6.21)
AD=10*sn(60)/sn(40);close('9.4 2c',side(4,AD,100),14.7)
# Independent convex field coordinates: B=(0,0), C=(65,0).
A=(50*cs(130),-50*sn(130));C=(65,0);D=(65-80*cs(52),-80*sn(52));poly=[A,(0,0),C,D];area=abs(sum(poly[i][0]*poly[(i+1)%4][1]-poly[(i+1)%4][0]*poly[i][1] for i in range(4)))/2
close('9.4 3 coordinate polygon',area,3360)
AC=side(8,10,80);DC=math.sqrt(AC*AC-49);close('9.4 4 Heron plus right triangle',heron(8,10,AC)+7*DC/2,72.1)
check('9.4 5 exact side',225+64-240*(-s.Rational(3,5))==433)
# D=(0,0), E=(5,0), A has |AD|9 and angle DAE30. Use sine to locate A,
# then B is on horizontal through A and on ray40 from E.
E=asi(.9);D=150-E;Ax=9*cs(D);Ay=9*sn(D);Bx=5+Ay/math.tan(math.radians(40));close('9.4 6 coordinate area',abs(Bx-Ax)*Ay/2,67.5)
AE,AN=pos(10,80);BE,BN=pos(6.5,200);close('9.4 7b coordinate bearing',bearing(AE-BE,AN-BN),57,dp=0)
BC=20.3*sn(82)/sn(40);AB=20.3*sn(58)/sn(40);close('problemA bronze BC',BC,31.3,dp=1);close('problemA bronze area',heron(20.3,BC,AB),269,dp=0);close('problemA bronze perimeter',20.3+BC+AB,78.4,dp=1)
BW=500*sn(40)/sn(35);close('problemA silver distance',BW,560);close('problemA silver perpendicular',BW*sn(75),541)
CE,CN=pos(750,42);dot=CE*sn(162)+CN*cs(162);disc=dot*dot-(750**2-680**2);t1=-dot-math.sqrt(disc);t2=-dot+math.sqrt(disc);close('problemA gold XB',t2-t1,403);close('problemA gold bearing',bearing(-(CE+t2*sn(162)),-(CN+t2*cs(162))),269,dp=0)
check('exam31 tan exact',s.simplify((s.Rational(8,9))/(-s.sqrt(17)/9)+8/s.sqrt(17))==0)
ang=asi(4/7);close('exam37 acute',ang,34.8,dp=1);close('exam37 obtuse',180-ang,145.2,dp=1);close('exam37 side',math.sqrt(232+24*math.sqrt(33)),19.2)
height=4.6*sn(35);AD=4.6*cs(35)+math.sqrt(3.8**2-height**2);close('exam45 perpendicular area',.5*(AD+5.2)*height,15.4)
check('exam63 polynomial',s.expand((x+2)**2-36-(2*x-5)**2+9*(2*x-5))==-3*(x*x-14*x+34))
for v in [7-s.sqrt(15),7+s.sqrt(15)]:check('exam63 root '+str(v),s.simplify(v*v-14*v+34)==0)
RE,RN=pos(200,68);qe,qn=pos(95,130);QE,QN=RE+qe,RN+qn;close('exam73 distance',math.hypot(QE,QN),258.6,dp=1);close('exam73 bearing',bearing(QE,QN),87,dp=0)
# Graph points, all stated equation solution sets and periodic transformations.
for name,fn,target,roots in [('9.5 4a',sn,1,[-270,90]),('9.5 4b',cs,-1,[-180,180]),('9.5 4c',lambda x:math.tan(math.radians(x)),0,[-360,-180,0,180,360]),('9.5 5',sn,.5,[-330,-210,30,150]),('9.5 6',lambda x:math.tan(math.radians(x)),-1,[-225,-45,135,315]),('9.5 7i',cs,1/math.sqrt(2),[-315,-45,45,315]),('9.5 7ii',cs,-1/math.sqrt(2),[-225,-135,135,225]),('9.6 5',lambda x:cs(2*x),0,[45,135,225,315]),('9.6 6i',lambda x:sn(x-20),1,[110]),('9.6 6ii',lambda x:sn(x-20),-1,[290]),('9.6 8',lambda x:sn(x)-cs(x),0,[45,225]),('problemB silver',lambda x:cs(x+40),0,[-130,50,230]),('exam39',lambda x:cs(3*x),.5,[20,100,140,220,260,340]),('exam78 axes',lambda x:cs(x-60),0,[-30,150,330]),('exam78 crossings',lambda x:cs(x-60)+cs(x),0,[-60,120,300])]:check(name+' graph values',all(abs(fn(v)-target)<1e-12 for v in roots))
for k,want in [(1,2),(1.5,3),(7/6,3),(11/6-1e-7,3),(11/6,4),(2,4)]:
 # Count by monotone half-cycle segments of cosine, independently of crossing formula.
 limit=360*k;count=0
 for n in range(math.ceil(limit/180)):
  lo=180*n;hi=min(180*(n+1),limit)
  if (cs(lo)-.5)*(cs(hi)-.5)<-1e-12 or abs(cs(hi)-.5)<1e-10:count+=1
 check('problemB Gold root count '+str(k),count==want)
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args();args.output.write_text(json.dumps(checks,indent=2));print(len(checks),'independent checks passed')
