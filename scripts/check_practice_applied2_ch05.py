"""Independent component, contact, friction and kinematics checks."""
import argparse,json,math
from pathlib import Path
import sympy as s
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);args=p.parse_args();checks=[];R=s.Rational;g=R(49,5);pi=s.pi

def ck(label,a,b):
 ok=s.simplify(a-b)==0;checks.append({'check':label,'passed':bool(ok)})
 if not ok:raise AssertionError((label,a,b))
def near(label,a,b,tol):
 ok=abs(float(a)-b)<tol;checks.append({'check':label,'passed':ok})
 if not ok:raise AssertionError((label,a,b))
def sin(d):return s.sin(d*pi/180)
def cos(d):return s.cos(d*pi/180)
def angle(y,x):return s.atan(y/x)*180/pi
# Resolve actual diagram forces in fixed Cartesian coordinates, independently of wording.
for label,m,F,ang,up,expectedA,expectedR in [('5.1.1a',10,40,60,-1,2,133),('5.1.1b',5,15,35,1,2.46,40.4),('5.1.1c',8,13,75,1,.421,65.8),('5.1.4',10,40,50,-1,2.57,129)]:
 acc=F*cos(ang)/m;normal=m*g-up*F*sin(ang)
 near(label+' acceleration',acc,expectedA,.0005 if expectedA<1 else .005);near(label+' reaction',normal,expectedR,.5 if expectedR>100 else .05);ck(label+' contact',int(bool(normal>0)),1)
for label,forces,w,theta,axis in [('5.1.2a',[(20,150),(15,45)],21.7,18.0,'y'),('5.1.2b',[(5,40),(6,-80)],5.57,28.9,'x'),('5.1.2c',[(15,120),(12,-70)],3.80,26.8,'x'),('5.1.3a',[(10,120),(40,30)],41.2,44.0,'x'),('5.1.3b',[(4,150),(6,65)],7.50,82.9,'x'),('5.1.3c',[(20,145),(15,250)],21.7,6.95,'x')]:
 X=sum(f*cos(a) for f,a in forces);Y=sum(f*sin(a) for f,a in forces)
 near(label+' magnitude',s.sqrt(X*X+Y*Y),w,.05 if w>10 else .005)
 near(label+' angle',angle(abs(X),abs(Y)) if axis=='y' else angle(abs(Y),abs(X)),theta,.005 if theta<10 else .05)
ck('5.1.5 mass',20*cos(30)/3,10*s.sqrt(3)/3);ck('5.1.6 kinematics',R(1,2)*R(16,5)*25,40);ck('5.1.6 force',8*R(4,5),2*R(16,5));ck('5.1.7 reaction reduction',6*sin(30),3);ck('5.1.7 double acceleration',6*s.sqrt(3)*cos(60)+6*cos(30),6*s.sqrt(3))
alpha=s.acos(R(3,4));ck('5.1.8 horizontal equilibrium',10*s.cos(alpha),60*s.cos(2*alpha));ck('5.1.8 upward total',10*s.sin(alpha)+60*s.sin(2*alpha),25*s.sqrt(7));near('5.1.8 alpha',alpha*180/pi,41.4,.05);near('5.1.8 min mass',25*s.sqrt(7)/g,6.75,.005)
ck('5.2.1 normal',5*g*cos(30),5*s.sqrt(3)*g/2);ck('5.2.1 acceleration',g*sin(30),g/2)
near('5.2.2 acceleration',(2-R(1,2)*g*sin(15))/R(1,2),1.46,.005)
near('5.2.3 force',g*sin(75)/(4*cos(45)),3.35,.005);near('5.2.3 speed',2*g*sin(75),18.9,.05)
a5=(100*R(119,169)-6*g*R(5,13))/6;v5=2*a5
near('5.2.5 acceleration',a5,7.97,.005);near('5.2.5 speed',v5,15.9,.05);near('5.2.5 stopping time',v5/(g*R(5,13)),4.23,.005)
ck('5.2.6 mass',6*g/2-g,6*g/3);ck('5.2.7 downforce',(5*g-2*g)*sin(30)/5,R(3,10)*g)
a8=g*(R(1,2)-sin(20));v8=3*a8;distance8=R(9,2)*a8;k8=g*sin(20);tau=(v8+s.sqrt(v8*v8+2*k8*distance8))/k8
near('5.2.8 return total',3+tau,6.85,.005);near('5.2.8 displacement balance',distance8+v8*tau-k8*tau*tau/2,0,1e-10)
for mu,f,a in [(R(1,5),3.92,2.04),(R(35,100),6.86,.57)]:near('5.3.1 friction '+str(mu),mu*2*g,f,1e-10);near('5.3.1 acceleration '+str(mu),(8-mu*2*g)/2,a,1e-10)
ck('5.3.1 static allowed',int(bool(8<2*g)),1)
for label,m,F,theta,sign,a,expected in [('5.3.2a',2,6,0,1,2,.102),('5.3.2b',2,15,30,1,4,.412),('5.3.2c',2,25,60,-1,1,.255)]:
 normal=m*g-sign*F*sin(theta);mu=(F*cos(theta)-m*a)/normal
 near(label,mu,expected,.0005);ck(label+' contact',int(bool(normal>0)),1)
for label,F,theta,sign,mu,a,expected in [('5.3.3a',6,0,1,R(2,5),5,.673),('5.3.3b',5,45,1,R(15,100),R(1,2),2.06),('5.3.3c',15,50,-1,R(1,5),R(3,2),2.12)]:
 mass=F*(cos(theta)+sign*mu*sin(theta))/(a+mu*g);normal=mass*g-sign*F*sin(theta)
 near(label+' mass',mass,expected,.0005 if expected<1 else .005);ck(label+' balance',F*cos(theta)-mu*normal,mass*a);ck(label+' contact',int(bool(normal>0)),1)
near('5.3.4 acceleration',(15-2*g*sin(30)-R(1,10)*2*g*cos(30))/2,1.75,.005)
v=(4-R(2,5)*R(1,5)*g)/R(1,5)*5;ck('5.3.5 speed',v,R(804,10));near('5.3.5 stopping',v/(R(2,5)*g),20.5,.05)
loadfactor=g*(sin(10)+R(3,10)*cos(10));near('5.3.7 limiting tension',500*loadfactor,2300,5);near('5.3.7 load',5000/(R(1,32)+loadfactor)-500,580,.5);ck('5.3.7 displacement',R(1,2)*R(1,32)*80**2,100)
ck('setA bronze distance',R(1,2)*(6-R(15,100)*3*g)/3*36,R(954,100));near('setA silver speed',(10*cos(60)-R(1,4)*(2*g-10*sin(60)))/2*10,11.3,.05)
M,mu,theta,t=s.symbols('M mu theta t',positive=True)
normal=M*g-2*g*s.sin(theta);acc=(2*g*s.cos(theta)-mu*normal)/M
ck('setA gold formula',acc*t,((2*s.cos(theta)+2*mu*s.sin(theta))/M-mu)*g*t)
f=R(1,5)*R(1,5)*g*cos(30);ck('setB bronze friction',f,49*s.sqrt(3)/250);near('setB bronze applied',R(1,5)*R(1,5)+R(1,5)*g*sin(30)+f,1.36,.005)
ck('setB silver threshold',R(3,5)+R(1,10)*R(4,5),R(17,25));near('setB silver mass',50/(R(11,10)+R(17,25)*g),6.44,.005)
for label,v,expected,sign in [('setB gold uphill',s.atan(R(6325,1000)/26),13.7,1),('setB gold downhill',s.atan(R(13675,1000)/23),30.7,-1)]:
 normal=R(49,2)*s.cos(v)+10*s.sin(v);driving=10*s.cos(v)-R(49,2)*s.sin(v)
 ck(label+' equilibrium',driving,sign*R(15,100)*normal);near(label+' angle',v*180/pi,expected,.05)
near('exam22 mass',(80*R(12,13)/R(3,4)-80*R(5,13))/g,6.91,.005)
P=15*g/(cos(60)+R(1,4)*sin(60));ck('exam25 balance',P*cos(60),R(1,4)*(60*g-P*sin(60)));near('exam25 force',P,205,.5);near('exam25 unrounded',P,205.16,.005)
P29=2*(32-20*cos(30));mu29=(P29*cos(30)-20*sin(30))/32;near('exam29 force',P29,29.4,.05);near('exam29 friction coefficient',mu29,.482,.0005)
near('exam32 magnitude',s.sqrt((6+5*cos(50))**2+(5*sin(50))**2),9.98,.005);near('exam32 angle',angle(5*sin(50),6+5*cos(50)),22.6,.05)
near('exam36 tension',30*R(5,4)+30*g*(R(3,5)+R(1,5)*R(4,5)),261,.5)
normal47=2*g*cos(25)-20*sin(15);mu47=(20*cos(15)-2*g*sin(25))/normal47;near('exam47 coefficient',mu47,.877,.0005);near('exam47 stop distance',64/(2*g*(sin(25)+mu47*cos(25))),2.68,.005);ck('exam47 initial contact',int(bool(normal47>0)),1)
args.output.write_text(json.dumps(checks,indent=2)+'\n');print(len(checks),'independent checks passed')
