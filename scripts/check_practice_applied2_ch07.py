"""Independent static/dynamic force, reaction, friction and moment checks."""
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
def deg(x):return x*180/pi
# Static vector balances independently recomputed from source diagram angles.
P=40*(s.sqrt(3)-1);Q=P*s.sqrt(6)/2
ck('7.1.1 horizontal',P*cs(60)+Q*cs(45),40);ck('7.1.1 vertical',P*sn(60),Q*sn(45));near('7.1.1 P',P,29.3,.05);near('7.1.1 Q',Q,35.9,.05)
for label,forces in [('7.1.2',[(100,60),(50,180),(50*s.sqrt(3),270)]),('7.1.3',[(5,150),(5*s.sqrt(3),60),(10,270)]),('7.1.4',[(10,30),(10*s.sqrt(3),120),(20,270)])]:
 ck(label+' x',sum(f*cs(a) for f,a in forces),0);ck(label+' y',sum(f*sn(a) for f,a in forces),0)
P=30/(1+cs(45)/2);Q=60*cs(30)-P*sn(45)/2;ck('7.1.5 along',P+P/2*cs(45),30);ck('7.1.5 normal',Q+P/2*sn(45),60*cs(30));near('7.1.5 P',P,22.2,.05);near('7.1.5 Q',Q,44.1,.05)
a=s.asin(R(2,3));near('7.1.6 alpha',deg(a),41.8,.05);ck('7.1.6 normal',30*s.cos(a),10*s.sqrt(5));near('7.1.6 P',30*s.cos(a),22.4,.05)
ck('7.2.1 weight balance',2*(2*s.sqrt(3))*cs(30),6);ck('7.2.2 horizontal',15*s.sqrt(2)*cs(45),15);ck('7.2.2 weight',15*s.sqrt(2)*(1+sn(45)),15*(1+s.sqrt(2)))
TP=4*g/(s.sqrt(3)+1);TQ=TP/s.sqrt(2);ck('7.2.4 horizontal',TP*cs(60),TQ*cs(45));ck('7.2.4 vertical',TP*sn(60)+TQ*sn(45),2*g);near('7.2.4 TP',TP,14.3,.05);near('7.2.4 TQ',TQ,10.1,.05)
T=16/(sn(40)+sn(50));near('7.2.5 tension',T,11.4,.05);near('7.2.5 mass',T*(cs(40)-cs(50))/g,.143,.0005)
near('7.2.6 angle',deg(s.atan(2/(R(1,5)*g))),45.6,.05)
P=10/(4*cs(30)-cs(60));reaction=20*cs(30)-P*(4*sn(30)+sn(60));near('7.2.8 normal',reaction,7.65,.005)
# Static friction limits: signed friction at each endpoint has correct magnitude.
ck('7.3.1 maximum',R(1,5)*2*g,R(392,100));P=R(1,4)*R(15,100)*g/(cs(30)+R(1,4)*sn(30));near('7.3.2 maximum',P,.371,.0005);ck('7.3.2 balance',P*cs(30),R(1,4)*(R(15,100)*g-P*sn(30)))
near('7.3.3 normal',4*g*cs(15),37.9,.05);near('7.3.3 mu',s.tan(pi/12),.268,.0005);near('7.3.4 normal',R(5,2)*g*cs(18),23.3,.05);near('7.3.4 max force',R(5,2)*g*(sn(18)+R(3,10)*cs(18)),14.6,.05)
for sign,w in [(1,.603),(-1,3.32)]:
 mass=5/(g*(sn(30)+sign*R(2,5)*cs(30)));near('7.3.5 mass '+str(sign),mass,w,.0005 if sign>0 else .005);ck('7.3.5 equilibrium '+str(sign),5-mass*g*sn(30),sign*R(2,5)*mass*g*cs(30))
near('7.3.7 tension',250*g*(sn(25)-R(15,100)*cs(25)),702,.5)
for sign,w in [(-1,.116),(1,.549)]:
 f=R(1,10)*g*(sn(20)+sign*R(1,4)*cs(20))/(cs(15)+sign*R(1,4)*sn(15));normal=R(1,10)*g*cs(20)-f*sn(15)
 near('7.3.8 limit '+str(sign),f,w,.0005);near('7.3.8 equilibrium '+str(sign),f*cs(15)-R(1,10)*g*sn(20)-sign*normal/4,0,1e-10);ck('7.3.8 contact '+str(sign),int(bool(normal>0)),1)
# Rigid bodies: independently verify force balance and signed moment about the hinge/base.
N=25*g/(2*s.sqrt(3));ck('7.4.1 moments',N*6*sn(60),25*g*3*cs(60));near('7.4.1 wall reaction',N,70.7,.05)
N=20*g*R(5,2)*cs(20)/R(7,2);normal=20*g-N*cs(20);fr=N*sn(20);near('7.4.2 peg',N,132,.5);near('7.4.2 friction coefficient',fr/normal,.622,.0005);ck('7.4.2 moment',N*R(7,2),20*g*R(5,2)*cs(20))
N=5*s.sqrt(3)*g/3;ck('7.4.3 moment',N*3*sn(60),10*g*R(3,2)*cs(60));ck('7.4.3 mu',N/(10*g),s.sqrt(3)/6)
a=s.atan(2);ck('7.4.4 moment',4*g*4*s.sin(a),4*g*s.sin(a)+12*g*2*s.cos(a));near('7.4.4 angle',deg(a),63.4,.05)
a=s.atan(R(25,12));F=R(3,10)*96*g;near('7.4.5 friction',F,282,.5);ck('7.4.5 moment',F*6*s.sin(a),(24*g*3+72*g*4)*s.cos(a));near('7.4.5 angle',deg(a),64.4,.05)
N=R(320,3);W=R(496,3);ck('7.4.6 horizontal',N*R(3,5),R(4,5)*80);ck('7.4.6 vertical',80+N*R(4,5),W);near('7.4.6 peg',N,107,.5);near('7.4.6 weight',W,165,.5)
T=55*g;Hx=-T*cs(30);Hy=40*g-T*sn(30);ck('7.4.7 moment',T*sn(30)*4,25*g*2+15*g*4);ck('7.4.7 Hx',Hx+T*cs(30),0);ck('7.4.7 Hy',Hy+T*sn(30)-40*g,0);ck('7.4.7 upward sign',int(bool(Hy>0)),1);near('7.4.7 magnitude',s.sqrt(Hx*Hx+Hy*Hy),483,.5);near('7.4.7 angle above left',deg(s.atan(Hy/abs(Hx))),14.7,.05)
M,G,a,alpha=s.symbols('M G a alpha',positive=True);T=2*M*G/(3*s.sin(alpha));Rx=2*M*G/(3*s.tan(alpha));Ry=M*G/3
ck('7.4.8 moment',T*s.sin(alpha)*3*a/2,M*G*a);ck('7.4.8 horizontal',T*s.cos(alpha),Rx);ck('7.4.8 vertical',T*s.sin(alpha)+Ry,M*G);ck('7.4.8 limiting',Ry,R(2,5)*Rx.subs(alpha,s.atan(R(4,5))));near('7.4.8 angle',deg(s.atan(R(4,5))),38.7,.05)
# Dynamics use original forces and independently recomputed normal reactions.
near('7.5.1 normal',5*g*cs(30),42.4,.05);near('7.5.1 acceleration',(120-5*g*sn(30)-R(1,4)*5*g*cs(30))/5,17.0,.05)
ck('7.5.2 friction',R(2,5)*g*cs(60),R(196,100));near('7.5.2 acceleration',g*(sn(60)-R(2,5)*cs(60)),6.53,.005)
near('7.5.3 mass',20/(2+g*(sn(45)+R(1,5)*cs(45))),1.94,.005);near('7.5.4 time',s.sqrt(10/(g*(sn(30)-R(15,100)*cs(30)))),1.66,.005)
normal=4*g*cs(25)-50*sn(30);acc=(50*cs(30)-4*g*sn(25)-normal/10)/4;d=g*(sn(25)+cs(25)/10);v=3*acc
near('7.5.5 initial acceleration',acc,6.42,.005);near('7.5.5 after removal time',v/d,3.83,.005);near('7.5.5 total time',3+v/d,6.83,.005);near('7.5.5 downhill surplus',4*g*(sn(25)-cs(25)/10),13.0,.05);ck('7.5.5 contact',int(bool(normal>0)),1)
mu=(g*sn(35)-R(8,9))/(g*cs(35));near('7.5.6 mu',mu,.589,.0005);ck('7.5.6 displacement',g*(sn(35)-mu*cs(35))*9/2,4)
near('7.5.7 mu',(1-g*sn(5))/(g*cs(5)),.0149,.00005)
normal=g/2*cs(10)-5*sn(60);acc=(5*cs(60)+g/2*sn(10)-R(3,4)*normal)/R(1,2);near('7.5.8 acceleration',acc,5.96,.005);near('7.5.8 time',30/acc,5.03,.005);ck('7.5.8 contact',int(bool(normal>0)),1)
normal=20*g*cs(30)-200*sn(10);acc=(200*cs(10)-20*g*sn(30)-R(3,10)*normal)/20;v=10*acc;d=g*(sn(30)+R(3,10)*cs(30));near('7.5.9 snap speed',v,29.2,.05);near('7.5.9 stop distance',v*v/(2*d),57.4,.05);ck('7.5.9 short of B',int(bool(v*v/(2*d)<60)),1)
acc=(10000-350-1200*g*sn(10))/1200;T=200*acc+150+200*g*sn(10);near('7.6.1 acceleration',acc,6.34,.005);near('7.6.1 tow tension',T,1760,5);ck('7.6.1 car balance',10000-200-1000*g*sn(10)-T,1000*acc)
acc=g/25;T=12*g/25;ck('7.6.2 table',T-R(2,5)*g,2*acc);ck('7.6.2 hanging',g/2-T,acc/2)
acc=g/10;T=R(9,5)*g;ck('7.6.3 slope',T-3*g*sn(30),3*acc);ck('7.6.3 hanging',2*g-T,2*acc);near('7.6.3 time',s.sqrt(6/acc),2.47,.005)
res=12000-1450*5-1450*g*sn(12);T=250*5+res/4+250*g*sn(12);near('7.6.4 resistance',res,1800,5);near('7.6.4 tow tension',T,2210,5);near('7.6.4 stop time',8/((res/4+250*g*sn(12))/250),2.09,.005)
ck('7.6.5 limiting mu',6*g*R(3,5)-R(1,3)*6*g*R(4,5)-2*g,0);acc=(6*g*R(3,5)-R(1,5)*6*g*R(4,5)-2*g)/8;near('7.6.5 time',5/acc,6.38,.005)
d=s.symbols('d',positive=True);acc=(2-s.sqrt(2))*g/6;ck('7.6.6 net acceleration',3*acc,g-g/s.sqrt(2));ck('7.6.6 time',acc/2*(12*d/((2-s.sqrt(2))*g)),d)
# Mixed problems and exam cases.
near('setA bronze friction',R(35,100)*6*g*cs(15),19.9,.05);near('setA bronze time',10/(g*(sn(15)+R(35,100)*cs(15))),1.71,.005)
a=s.atan(R(1,5));near('setA silver angle',deg(a),11.3,.05);near('setA silver time',20/(g*(s.sin(a)+s.cos(a)/5)),5.20,.005)
near('setA gold threshold',deg(s.atan(R(15,100))),8.53,.005);du=g*(sn(20)+R(15,100)*cs(20));ad=g*(sn(20)-R(15,100)*cs(20));distance=225/(2*du);near('setA gold time',15/du+s.sqrt(2*distance/ad),8.08,.005)
T=R(195,10);ck('setB bronze table',T-R(375,1000)*4*g,4*R(12,10));near('setB bronze mass',T/(g-R(12,10)),2.27,.005)
for sign,w in [(1,8.51),(-1,20.6)]:
 sinalpha=(g/2-sign*R(5,2)*R(4,5))/(2*g);near('setB silver angle '+str(sign),deg(s.asin(sinalpha)),w,.005 if sign>0 else .05)
near('setB silver pulley',R(9,2)*s.sqrt(2+2*R(29,196)),6.82,.005)
ck('setB gold limiting mu',4*R(5,13)-4*R(7,48)*R(12,13)-1,0);ck('setB gold acceleration',(4*g*R(5,13)-R(1,10)*4*g*R(12,13)-g)/5,11*g/325)
near('exam26 angle',deg(s.atan(R(2,5))),21.8,.05);near('exam26 force',3*s.sqrt(29),16.2,.05);near('exam26 time',s.sqrt(20/s.sqrt(29)),1.93,.005)
T=25/(sn(35)+sn(55));near('exam34 tension',T,18,.05);near('exam34 mass',T*(cs(35)-cs(55))/g,.450,.0005)
mu=5/(16*s.sqrt(3));near('exam40 mu',mu,.180,.0005);ck('exam40 moment',mu*4*2*sn(60),(1+3*R(1,2))*cs(60))
acc=R(10,9);mu=(45*cs(40)-7*acc)/(3*g+2*(4*g-45*sn(40)));T=3*acc+mu*3*g;near('exam43 mu',mu,.534,.0005);near('exam43 tension',T,19,.05);ck('exam43 Q balance',45*cs(40)-2*mu*(4*g-45*sn(40))-T,4*acc)
acc=(2*g-3*g*sn(30)-R(1,10)*3*g*cs(30))/5;near('exam46 acceleration',acc,.4708,.00005);near('exam46 time',10/acc,21.2,.05);near('exam46 stop distance',100/(2*g*(sn(30)+cs(30)/10)),8.70,.005);ck('exam46 downhill motion',int(bool(sn(30)>cs(30)/10)),1)
# Unit weight/length for exam49: forces, moments and impending-slip directions.
RA=R(100,121);NB=R(30,121);FB=R(21,121);AM=(30*s.sqrt(3)+21)/121
ck('exam49 vertical',RA+FB,1);ck('exam49 floor friction',R(3,10)*RA,NB);ck('exam49 wall friction',R(7,10)*NB,FB);ck('exam49 moment',NB*sn(60)+FB*cs(60),AM*cs(60));near('exam49 AM/l',AM,.603,.0005)
ck('exam52 moment15',80*cs(15)*sn(15),20);ck('exam52 moment75',80*cs(75)*sn(75),20)
Hx=80*sn(15);Hy=20-80*cs(15);near('exam52 hinge magnitude',s.sqrt(Hx*Hx+Hy*Hy),60.9,.05);near('exam52 hinge direction',deg(s.atan(-Hy/Hx)),70.1,.05);ck('exam52 greater-angle downward',int(bool(20-80*cs(75)<0)),1)
args.output.write_text(json.dumps(checks,indent=2)+'\n');print(len(checks),'independent checks passed')
