"""Independent geometry, radian-root and small-angle-limit checks."""
import argparse,json,math
from pathlib import Path
import sympy as s
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);args=p.parse_args();checks=[];R=s.Rational;x=s.symbols('x',real=True);pi=s.pi

def ck(label,a,b):
 ok=s.simplify(a-b)==0;checks.append({'check':label,'passed':bool(ok)})
 if not ok:raise AssertionError((label,a,b))
def near(label,a,b,tol):
 ok=abs(float(a)-b)<tol;checks.append({'check':label,'passed':ok})
 if not ok:raise AssertionError((label,a,b))
for label,value,expected in [('5.1.1a',5*pi/6*180/pi,150),('5.1.1b',pi/8*180/pi,R(45,2)),('5.1.1c',4*pi*180/pi,720),('5.1.2ai',18*pi/180,pi/10),('5.1.2aii',R(65,2)*pi/180,13*pi/72),('5.1.2aiii',320*pi/180,16*pi/9),('5.1.4a',s.cos(9*pi/3),-1),('5.1.4b',s.tan(-3*pi/4),1),('5.1.4c',s.sin(-11*pi/6),R(1,2))]:ck(label,value,expected)
for label,v,w,tol in [('5.1.1d',R(34,100)*180/pi,19.5,.05),('5.1.1e',s.sqrt(2)*180/pi,81,.05),('5.1.1f',R(19,10)*180/pi,108.9,.05),('5.1.2bi',16*pi/180,.279,.0005),('5.1.2bii',124*pi/180,2.16,.005),('5.1.2biii',260*pi/180,4.54,.005)]:near(label,v,w,tol)
for label,func,inputs,outputs in [('5.1.3a',s.tan(2*x),[0,pi/2,pi],[0,0,0]),('5.1.3b',s.cos(x+pi),[0,pi/2,3*pi/2,pi,2*pi],[-1,0,0,1,-1]),('5.1.3c',s.sin(x/2)+1,[-pi,0,pi],[0,1,2]),('5.1.5a',2*s.cos(2*x),[-7*pi/4,-5*pi/4,-3*pi/4,-pi/4,0],[0,0,0,0,2]),('5.1.5b',s.sin(x-pi/4),[-3*pi/4,pi/4,0],[0,0,-s.sqrt(2)/2]),('5.1.7',s.sin(x+5*pi/6),[pi/6,7*pi/6,13*pi/6,19*pi/6,0],[0,0,0,0,R(1,2)]),('exam46 zeros',4*s.sin(x+pi/3),[0,2*pi/3,5*pi/3],[2*s.sqrt(3),0,0])]:
 for z,w in zip(inputs,outputs):ck(label+' '+str(z),func.subs(x,z),w)
# Construct triangle measurements independently from the cosine law and coordinates.
angle=s.acos(R(1,144));near('5.1.6 angle',angle,1.56,.005);near('5.1.6 area',s.sqrt(29*5*13*11)/4,36,.05)
east=800*s.sin(pi/9);north=800*s.cos(pi/9)-600
near('5.1.8 distance',s.sqrt(east**2+north**2),313,.5);near('5.1.8 bearing',s.atan(east/north)*180/pi,61,.05)
for label,a,b in [('5.2.1a',18*R(5,2),45),('5.2.1b',R(13,2)*2*pi/3,13*pi/3),('5.2.1c',R(23,10)*R(35,100),R(805,1000)),('5.2.4 radius',R(608,100)/R(152,100),4),('5.2.4 perimeter',R(86,10)+R(73,10)+R(608,100)+4,R(2598,100)),('5.2.5 arc',8*7*pi/9,56*pi/9),('5.2.6 reflex',40*pi/9/4,10*pi/9),('5.2.7 diameter',12*5*pi/3/pi,20),('5.2.7 angle',2*pi/12,pi/6),('5.3.1a',R(1,2)*25*R(45,100),R(5625,1000)),('5.3.1b',R(1,2)*R(73,10)**2*R(12,10),R(31974,1000)),('5.3.1c',s.sqrt(2*9*pi/8/(pi/4)),3),('5.3.1d',2*R(33696,1000)/R(72,10)**2,R(13,10)),('5.3.4 angle',s.acos(R(-1,2)),2*pi/3),('5.3.4 area',R(25,2)*2*pi/3,25*pi/3),('5.3.6 radius2',2*R(378,10)/R(12,10),63),('5.3.7 theta',R(2,5),R(2,5)),('5.3.7 radius2',24/R(2,5),60)]:ck(label,a,b)
for label,val,w,tol in [('5.2.2a',30*s.sqrt(3)/pi,16.5,.05),('5.2.2b',R(20,1)/R(18,10),11.1,.05),('5.2.2c',R(925,100)/R(45,100),20.6,.05),('5.2.3a',R(121,10)/R(34,10),3.56,.005),('5.2.3b',R(7235,1000)/R(92,100),7.86,.005),('5.2.3c',s.sqrt(R(5,2)),1.58,.005),('5.2.5 perimeter',8+8*s.cos(2*pi/9)+8*s.sin(2*pi/9)+56*pi/9,38.8,.05),('5.2.6 triangle',12*s.sin(8*pi/9),4.1,.05),('5.3.2a',R(9,2)*(R(7,10)-s.sin(R(7,10))),.251,.0005),('5.3.2b',18*(2*pi/3-s.sin(2*pi/3)),22.1,.05),('5.3.2c',R(25,2)*(s.acos(R(1,50))-s.sqrt(1-R(1,50)**2)),6.89,.005),('5.3.3a',R(9,8)*(2*pi-R(3,10)),6.73,.005),('5.3.3b',R(121,2)*(5*pi/4+s.sin(3*pi/4)),280,.5),('5.3.3c',32*(pi-R(6,10)),81.3,.05),('5.3.4 segment',25*pi/3-25*s.sqrt(3)/4,15.4,.05),('5.3.5 area',76*s.sin(R(73,100))+32*(pi-R(73,100)),128,.5),('5.3.5 perimeter',27+s.sqrt(19**2+8**2-2*19*8*s.cos(R(73,100)))+8*(pi-R(73,100)),60.4,.05),('5.3.6 segment',R(378,10)-R(63,2)*s.sin(R(12,10)),8.4,.05),('5.3.7 segment',30*(R(2,5)-s.sin(R(2,5))),.317,.0005)]:near(label,val,w,tol)
# Check every listed trigonometric root against the original equation and interval.
rootsets=[
('5.4.1a',s.sin(x)-R(1,2),[pi/6,5*pi/6],0,2*pi),('5.4.1b',s.tan(x)+2,[pi-s.atan(2),2*pi-s.atan(2)],0,2*pi),('5.4.1c',5*s.cos(x)-3,[s.acos(R(3,5)),2*pi-s.acos(R(3,5))],0,2*pi),('5.4.1d',s.sqrt(2)*s.sin(x)-1,[pi/4,3*pi/4],0,2*pi),
('5.4.2a',3*s.sin(x)-2,[s.asin(R(2,3)),pi-s.asin(R(2,3))],0,pi),('5.4.2b',6*s.cos(x)+3,[-2*pi/3,2*pi/3,4*pi/3],-pi,2*pi),('5.4.2c',s.sqrt(2)*s.tan(x)-2,[s.atan(s.sqrt(2))+j*pi for j in [-2,-1,0]],-2*pi,pi),('5.4.2d',s.sqrt(2)*s.cos(2*x)-1,[9*pi/8,15*pi/8,17*pi/8,23*pi/8],pi,3*pi),
('5.4.3a',s.tan(x)**2+3*s.tan(x)+2,[pi-s.atan(2),3*pi/4,2*pi-s.atan(2),7*pi/4],0,2*pi),('5.4.3b',3*s.sin(x)**2-2*s.cos(x)+1,[s.acos((-1+s.sqrt(13))/3),2*pi-s.acos((-1+s.sqrt(13))/3)],0,2*pi),('5.4.3c',s.cos(x+pi/4)-R(1,2),[pi/12,17*pi/12],0,2*pi),('5.4.3d',s.sin(2*x+R(3,5))-1,[pi/4-R(3,10),5*pi/4-R(3,10)],0,2*pi),
('5.4.4a',s.cos(x-pi/18)-s.cos(pi/12),[5*pi/36,71*pi/36],0,2*pi),('5.4.4b',s.tan(2*x)-R(3,5),[s.atan(R(3,5))/2+j*pi/2 for j in range(4)],0,2*pi),('5.4.5',4*s.sin(2*x)-3*s.cos(2*x),[s.atan(R(3,4))/2+j*pi/2 for j in [-2,-1,0,1]],-pi,pi),('5.4.6',2*s.cos(x)**2+3*s.sin(x)-3,[pi/6,pi/2,5*pi/6],0,pi),('5.4.7a',s.sin(3*x+pi/4)+R(1,5),[(j*pi+(-1)**(j+1)*s.asin(R(1,5))-pi/4)/3 for j in [1,2,3,4]],0,3*pi/2),('5.4.7b',4*s.cos(x)-6*s.tan(x),[pi/6,5*pi/6],0,pi),
('setB bronze',3*s.tan(x)**2+8*s.tan(x)-3,[s.atan(R(1,3)),pi-s.atan(3),pi+s.atan(R(1,3)),2*pi-s.atan(3)],0,2*pi),('setB silver',3*s.cos(x)**2-5*(1-s.sin(x)),[s.asin(R(2,3)),pi/2,pi-s.asin(R(2,3))],-pi,pi),('setB gold',s.cos(x)-3*s.tan(x),[s.asin((-3+s.sqrt(13))/2),pi-s.asin((-3+s.sqrt(13))/2),2*pi+s.asin((-3+s.sqrt(13))/2),3*pi-s.asin((-3+s.sqrt(13))/2)],0,3*pi),('exam46',4*s.sin(x+pi/3)+R(6,5),[2*pi/3+s.asin(R(3,10)),5*pi/3-s.asin(R(3,10))],0,2*pi)]
for label,f,values,lo,hi in rootsets:
 for i,v in enumerate(values):
  near(label+' root '+str(i),f.subs(x,v).evalf(30),0,1e-25);ck(label+' interval '+str(i),int(float(lo)<=float(v)<=float(hi)),1)
# Independent small-angle limits distinguish constants from reciprocal or linear behaviour.
for label,f,target in [('5.5.1a',s.sin(3*x)/x,3),('5.5.1b',s.tan(4*x)/s.sin(2*x),2),('5.5.1c',(5*s.tan(x)-x)/s.sin(4*x),1),('5.5.2a',(1-s.cos(2*x))/(x*s.sin(x)),2),('5.5.2b',(s.cos(6*x)-1)/(s.sin(3*x)*s.tan(x)),-6),('5.5.2c',x*s.tan(x)/(1-s.cos(x)),2),('5.5.3a scaled',x*(2*x-s.sin(3*x))/(x*s.tan(4*x)),-R(1,4)),('5.5.3b scaled',(s.cos(x)-1)/(x*s.sin(x)),-R(1,2)),('5.5.3c scaled',x*(s.sin(x)+s.tan(x))/(1-s.cos(2*x)),1),('5.5.4',(1-s.cos(2*x))/(3*x*s.sin(2*x)),R(1,3))]:ck(label,s.limit(f,x,0),target)
ck('5.5.5 expansion',s.series((3*s.tan(x)-4*s.cos(x)+5)/(s.sin(x)+1),x,0,2).removeO(),1+2*x)
ck('5.5.6 expansion',s.series(5*s.cos(x)**2+6*s.cos(x)+1,x,0,3).removeO(),12-8*x*x);near('5.5.6 radians',12-8*(pi/18)**2,11.76,.005)
ck('setA bronze triangle',18*s.sin(pi/3),9*s.sqrt(3));ck('setA bronze shaded',2*(6*pi-9*s.sqrt(3)),12*pi-18*s.sqrt(3));ck('setA silver rhombus',8*s.sqrt(8**2-4**2),32*s.sqrt(3));ck('setA silver full lens',2*R(1,2)*64*2*pi/3-32*s.sqrt(3),(128*pi-96*s.sqrt(3))/3);ck('setA gold lens',2*R(1,2)*x*x*s.Symbol('theta')-s.sqrt(3)*x*x/2,(s.Symbol('theta')-s.sqrt(3)/2)*x*x)
exact25=(1+s.sin(2*x)+s.tan(2*x))/(2*s.cos(4*x)-1)
ck('exam25 actual denominator',s.series(2*s.cos(4*x)-1,x,0,3).removeO(),1-16*x*x)
v=R(3,100);actual=exact25.subs(x,v);printed=(1+4*v)/(1-4*v*v);correct=(1+4*v)/(1-16*v*v)
near('exam25 actual',actual,1.136380360,5e-10);near('exam25 supplied percent',abs((printed-actual)/actual)*100,1.09,.005);near('exam25 corrected percent',abs((correct-actual)/actual)*100,.00147,.000005)
ck('exam30 radius2',2*R(88725,1000)/R(42,10),R(169,4));ck('exam30 arc',R(13,2)*(2*pi-R(42,10)),13*pi-R(273,10));near('exam30 segment',R(169,8)*(2*pi-R(42,10)-s.sin(2*pi-R(42,10))),25.6,.05)
ck('exam35 true root',s.sqrt(3)*s.sin(pi/6),s.cos(pi/6));ck('exam35 false root residual',s.sqrt(3)*s.sin(-pi/6)-s.cos(-pi/6),-s.sqrt(3))
theta=2*s.asin(R(4,11));phi=(pi-theta)/2;near('exam41 angle',theta,.744,.0005);near('exam41 shaded',R(121,8)*(s.sin(theta)+phi),28.4,.05);near('exam41 perimeter',11+R(11,2)*phi,17.6,.05)
ck('exam44 factorisation',(x-3)*(-2*x*x+2*x-1),-2*x**3+8*x*x-7*x+3);ck('exam44 quartic square',-2*(x*x-R(1,2))**2-R(1,2),-2*x**4+2*x*x-1)
args.output.write_text(json.dumps(checks,indent=2)+'\n');print(len(checks),'independent checks passed')
