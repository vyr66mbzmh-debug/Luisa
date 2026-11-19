"""Independent projectile trajectory, energy, root and domain checks."""
import argparse,json
from pathlib import Path
import sympy as s
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);args=p.parse_args();checks=[];R=s.Rational;g=R(49,5);pi=s.pi

def ck(label,a,b):
 ok=s.simplify(s.trigsimp(a-b))==0;checks.append({'check':label,'passed':bool(ok)})
 if not ok:raise AssertionError((label,a,b))
def near(label,a,b,tol):
 ok=abs(float(a)-b)<tol;checks.append({'check':label,'passed':ok})
 if not ok:raise AssertionError((label,a,b))
def sn(d):return s.sin(d*pi/180)
def cs(d):return s.cos(d*pi/180)
def deg(v):return v*180/pi
def Y(t,b,h=0):return h+b*t-g*t*t/2
# Horizontal launch and component values.
ck('6.1.1 time',g/2*(10*s.sqrt(5)/7)**2,50);ck('6.1.1 range',15*10*s.sqrt(5)/7,150*s.sqrt(5)/7)
ck('6.1.3 time',40*R(5,2),100);ck('6.1.3 height',g/2*R(5,2)**2,R(245,8));near('6.1.4 speed',R(49,2)/s.sqrt(30/g),14,.05)
ck('6.1.5 range',20*2,40);ck('6.1.5 height',Y(2,0,20),R(2,5));ck('6.1.6 flight',g/2*(s.sqrt(10)/7)**2,1);ck('6.1.6 distance',R(7,10)*(2-s.sqrt(10)/7),(14-s.sqrt(10))/10)
ck('6.1.7 speed',6-R(1,5)*g*2,R(52,25));ck('6.1.7 flight time',R(78,100)/R(52,25),R(3,8));ck('6.1.7 height',g/2*R(3,8)**2,R(441,640));ck('6.1.7 smooth height',g/2*R(13,100)**2,R(8281,100000))
for label,a,b in [('6.2.1 horizontal',10*cs(30),5*s.sqrt(3)),('6.2.1 vertical',10*sn(30),5),('6.2.2 horizontal',20*cs(45),10*s.sqrt(2)),('6.2.2 vertical',20*sn(45),10*s.sqrt(2)),('6.2.3 speed',s.sqrt(12**2+5**2),13),('6.2.6 horizontal',156*R(5,13),60),('6.2.6 vertical',156*R(12,13),144),('6.2.7 speed',s.sqrt(4**2+3**2),5)]:ck(label,a,b)
for label,a,b,tol in [('6.2.3 angle',deg(s.atan(R(5,12))),22.6,.05),('6.2.4 horizontal',15*cs(25),13.6,.05),('6.2.4 vertical',15*sn(25),6.34,.005),('6.2.5 horizontal',8*cs(10),7.88,.005),('6.2.5 vertical',-8*sn(10),-1.39,.005),('6.2.7 angle',deg(s.atan(R(3,4))),36.9,.05)]:near(label,a,b,tol)
# Direct substitutions into y=h+bt-gt²/2 verify landing and crossing roots.
ck('6.3.1 flight',Y(10,49),0);ck('6.3.2 flight',Y(R(120,49),12),0);near('6.3.2 time',R(120,49),2.45,.005);near('6.3.2 range',R(600,49),12.2,.05)
near('6.3.3 maximum',(34*sn(50))**2/(2*g),34.6,.05);near('6.3.4 height',-Y(5,12*sn(35)),88.1,.05)
b=50*sn(20);T=(b+s.sqrt(b*b+196))/g;near('6.3.5 landing height',Y(T,b,10),0,1e-10);near('6.3.5 range',50*cs(20)*T,188,.5)
times=[(15-s.sqrt(29))/g,(15+s.sqrt(29))/g]
for t in times:ck('6.3.6 height crossing '+str(t),Y(t,15),10)
near('6.3.6 duration',times[1]-times[0],1.10,.005)
a=77*s.sqrt(5)/5;b=14*s.sqrt(5);ck('6.3.7 height',b*b/(2*g),50);ck('6.3.7 range',a*2*b/g,220);ck('6.3.7 speed exact',s.sqrt(a*a+b*b),7*s.sqrt(1105)/5);near('6.3.7 angle',deg(s.atan(b/a)),42.3,.05);near('6.3.7 initial speed',s.sqrt(a*a+b*b),46.5,.05);near('6.3.7 speed5',s.sqrt(a*a+(b-5*g)**2),38.7,.05)
tedge=R(50,9);T=(48+s.sqrt(344))/g;near('6.3.8 cliff clearance',Y(tedge,48),115.4,.05);ck('6.3.8 landing',Y(T,48),100);near('6.3.8 distance',36*T-200,44.5,.05)
b=25*sn(40);T=(b+s.sqrt(b*b- R(392,5)))/g;near('6.3.9 crossbar',Y(T,b),4,1e-10);near('6.3.9 limiting range',25*cs(40)*T,57.6,.05)
# Symbolically derive the range/apex equations and discriminate the source typo.
U,G,alpha=s.symbols('U G alpha',positive=True);t,x,H=s.symbols('t x H',real=True)
flight=2*U*s.sin(alpha)/G;rang=U*s.cos(alpha)*flight;apex=U*s.sin(alpha)/G
ck('range identity',rang,U*U*s.sin(2*alpha)/G);ck('apex time velocity',U*s.sin(alpha)-G*apex,0);height=U*s.sin(alpha)*apex-G*apex**2/2
ck('6.4.1 maximum',height.subs(U,20),200*s.sin(alpha)**2/G)
ck('6.4.2 maximum at45',s.sin(2*pi/4),1)
correct= rang/2*s.tan(alpha)-G*rang**2/(8*U*U*s.cos(alpha)**2);printed=rang*s.tan(alpha)-G*rang**2/(8*U*U*s.cos(alpha)**2)
ck('6.4.3 correct formula',correct,height);ck('6.4.3 wrong formula excess',printed-height,rang*s.tan(alpha)/2)
ck('6.4.3 sec identity',1/s.cos(alpha)**2,1+s.tan(alpha)**2)
ck('6.4.5 shared flight',G/2*s.sqrt(2*H/G)**2,H)
a,b=s.symbols('a b',positive=True);ck('6.4.6 landing',b*(2*b/G)-G/2*(2*b/G)**2,0);ck('6.4.6 components product',(12*7/s.sqrt(3))*(5*7/s.sqrt(3))*2/g,200);near('6.4.6 speed',91/s.sqrt(3),52.5,.05)
for z,w in [((400-s.sqrt(130796))/98,21.4),((400+s.sqrt(130796))/98,82.7)]:
 ck('6.4.8 wall quadratic '+str(w),R(49,10)*(1+z*z)-40*z+10,0);near('6.4.8 angle '+str(w),deg(s.atan(z)),w,.05)
ck('setA bronze time',(2*U*s.sin(alpha))*(4*U*s.sin(alpha)/G)-G/2*(4*U*s.sin(alpha)/G)**2,0)
ck('setA bronze range',2*U*s.cos(alpha)*(4*U*s.sin(alpha)/G),4*U*U*s.sin(2*alpha)/G)
traj=R(3,5)*U*(5*x/(4*U))-G/2*(5*x/(4*U))**2;ck('setA silver trajectory',traj,R(3,4)*x-R(25,32)*G*x*x/U**2)
t=R(10,7);ck('setA silver crossing',Y(t,21),28*t/2);ck('setA silver speed',s.sqrt(28**2+(21-g*t)**2),7*s.sqrt(17))
ck('setA gold trajectory equality',x-x*x/80+x*x/160,x-x*x/160);ck('setA gold max square',x-x*x/160,40-(x-80)**2/160)
h=s.symbols('h',positive=True);xsol=80-4*s.sqrt(400-10*h);ck('setA gold intersection',xsol-xsol*xsol/160,h);ck('setA gold ground limiting',80-80**2/R(80),0)
# The specified g=10 applies only to Set B.
near('setB bronze impact speed',s.sqrt(10**2+15**2+2*10*6),21.1,.05);near('setB bronze duration',s.sqrt(5),2.24,.005)
for t in [(15-5*s.sqrt(5))/10,(15+5*s.sqrt(5))/10]:ck('setB bronze speed boundary '+str(t),100+(15-10*t)**2,225)
ck('setB silver height',120+(18**2-(55**2-33**2))/R(20),R(394,10));near('setB silver landing angle',deg(s.atan(s.sqrt(18**2+20*120)/33)),57.7,.05)
T=(16*s.sqrt(6)-6)/10;ck('setB gold impact speed',s.sqrt(40**2+36+20*75),56);ck('setB gold landing height',75-6*T-5*T*T,0);near('setB gold straight distance',s.sqrt((40*T)**2+75**2),152,.5);ck('setB gold parallel time',-6-10*R(26,10),-32);ck('setB gold parallel height',75-6*R(26,10)-5*R(26,10)**2,R(256,10));ck('setB gold impossible required drop',(40**2-6**2)/R(20),R(782,10))
near('exam35 drop metres',g/2*(R(9,4)/R(56,5))**2,.198,.0005)
near('exam38 apex',R(11,10)+18**2/(2*g),17.6,.05);near('exam38 catch',Y(R(43,12),18,R(11,10)),2.68,.005)
ck('exam42 vertical initial',14**2/(2*g),10);near('exam42 angle',deg(s.asin(R(14,50))),16.3,.05);near('exam42 return speed time',28/g,2.86,.005);near('exam42 landing angle',deg(s.atan(s.sqrt(14**2+2*g*36)/48)),32.0,.05)
z=(80+s.sqrt(80**2-4*R(256,10)*R(306,10)))/R(512,10);ck('exam45 trajectory',80*z-R(256,10)*(1+z*z),5);near('exam45 angle',deg(s.atan(z)),69.5,.05)
for sign,w in [(-1,6.33),(1,29.0)]:
 t=(10+sign*s.sqrt(R(412,10)))/g;ck('exam48 wall crossing '+str(sign),Y(t,10,2),5);near('exam48 horizontal '+str(sign),10*s.sqrt(3)*t,w,.005 if sign<0 else .05)
near('exam48 impact speed',s.sqrt(400+4*g),21.0,.05);ck('exam51 height',(256-144)/(2*g),R(40,7));ck('exam51 landing height',Y(R(100,49),R(128,10)),R(40,7));ck('exam51 impact speed',R(96,10)**2+(R(128,10)-g*R(100,49))**2,144);near('exam51 distance',R(960,49),19.6,.05)
args.output.write_text(json.dumps(checks,indent=2)+'\n');print(len(checks),'independent checks passed')
