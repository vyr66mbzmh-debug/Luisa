"""Independent kinematic identities, derivative, direction and feasibility checks."""
import argparse,json
from pathlib import Path
import sympy as s
import mpmath as mp
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);args=p.parse_args();checks=[];R=s.Rational;g=R(49,5);t=s.symbols('t',real=True);pi=s.pi

def ck(label,a,b):
 ok=s.simplify(s.trigsimp((s.Rational(str(a)) if isinstance(a,float) else s.sympify(a))-(s.Rational(str(b)) if isinstance(b,float) else s.sympify(b))))==0;checks.append({'check':label,'passed':bool(ok)})
 if not ok:raise AssertionError((label,a,b))
def near(label,a,b,tol):
 ok=abs(float(a)-b)<tol;checks.append({'check':label,'passed':ok})
 if not ok:raise AssertionError((label,a,b))
def vec(label,a,b):
 for k,(x,y) in enumerate(zip(a,b)):ck(label+f' component{k+1}',x,y)
def norm(v):return s.sqrt(sum(x*x for x in v))
def deg(x):return x*180/pi
vec('8.1.1 position',[4+5,2-15],[9,-13]);vec('8.1.2 position',[-6+4,1+2],[-2,3]);ck('8.1.2 north x',-6+2*3,0)
vec('8.1.3 displacement',[30*2+10*4/2,20*2+20*4/2],[80,80]);near('8.1.3 distance',norm([80,80]),113,.5)
vec('8.1.4 velocity',[3+3*3,-2+3],[12,1]);ck('8.1.4 speed squared',12**2+1,145);near('8.1.4 bearing',deg(s.atan(12)),85.2,.05)
vec('8.1.5 acceleration',[(4+8)/8,(-5-3)/8],[R(3,2),-1]);vec('8.1.6 final velocity',[-11+3*5,-18+5],[4,-13]);vec('8.1.6 displacement',[s.integrate(3*t-11,(t,0,5)),s.integrate(t-18,(t,0,5))],[-R(35,2),-R(155,2)])
# Quadrature independently compared to a closed antiderivative of the speed.
Q=10*t*t-102*t+445
A=(20*t-102)*s.sqrt(Q)/40+R(1849,20)/s.sqrt(10)*s.asinh((10*t-51)/43)
ck('8.1.6 arc derivative',s.diff(A,t),s.sqrt(Q));distance=A.subs(t,5)-A.subs(t,0);near('8.1.6 arc quadrature',distance,mp.quad(lambda z:mp.sqrt((3*z-11)**2+(z-18)**2),[0,5]),1e-10);near('8.1.6 distance',distance,81.9,.05);near('8.1.6 displacement magnitude',norm([R(-35,2),R(-155,2)]),79.5,.05)
vec('8.1.7 position',[1540-220*2,2500-400*2],[1100,1700]);near('8.1.7 distance',norm([1100,1700]),2020,5);vec('8.1.7 south',[1540-220*7,2500-400*7],[0,-300])
ck('8.1.8 initial speed squared',2**2+(-5)**2,29);vec('8.1.8 final velocity',[2+R(12,5)*5,-5+2*5],[14,5]);vec('8.1.8 position',[-1+2*6+18*R(12,5),8-5*6+18*2],[R(271,5),14])
vec('8.1.9 meeting A',[4+R(3,2)*4,-6+2*4],[10,2]);vec('8.1.9 meeting B',[18-2*4,12-R(5,2)*4],[10,2]);vec('8.1.10 acceleration',[(14-5)/3,(-2-10)/3],[3,-4]);vec('8.1.10 force',[2*3,-8],[6,-8]);ck('8.1.10 due east',10*3-4*9/2-2*6,0)
vec('8.2.1 velocity',[15,25-2*g],[15,R(27,5)]);near('8.2.1 speed',norm([15,R(27,5)]),15.9,.05)
r=[6+12*t,6+19*t-g*t*t/2];vec('8.2.2 initial',[v.subs(t,0) for v in r],[6,6]);vec('8.2.2 velocity',[s.diff(v,t).subs(t,0) for v in r],[12,19])
T=(13+s.sqrt(463))/g;ck('8.2.3 landing',15+13*T-g*T*T/2,0);near('8.2.3 time',T,3.52,.005);near('8.2.3 distance',23*T,81,.05);ck('8.2.4 max height',49/(2*g),R(5,2))
ck('8.2.5 vertical return',R(49,2)*5-g*25/2,0);ck('8.2.5 range',24*5,120);near('8.2.5 height',R(49,2)**2/(2*g),30.6,.05)
T=(54+s.sqrt(6836))/g;ck('8.2.6 landing',200+54*T-g*T*T/2,0);near('8.2.6 time',T,13.9,.05);near('8.2.6 AB',norm([30*T,200]),464,.5)
T=(20+s.sqrt(8))/g;ck('8.2.7 platform',20*T-g*T*T/2,20);ck('8.2.7 descending velocity',20-g*T,-s.sqrt(8));near('8.2.7 range',13*T,30.3,.05);near('8.2.7 speed',s.sqrt(177),13.3,.05)
ck('8.2.8 same level q',g*6/2,R(147,5));ck('8.2.8 key altitude',R(234,5)*6-g*36/2,R(522,5));ck('8.2.8 impossible speed',int(bool(g*3>13)),1)
position=2*s.sin(pi*t)+t*t;ck('8.3.1 velocity',s.diff(position,t).subs(t,2),2*pi+4);ck('8.3.1 acceleration',s.diff(position,t,2).subs(t,5),2)
position=s.exp(t)+t**4/12-t-1;ck('8.3.2 acceleration',s.diff(position,t,2),s.exp(t)+t*t);ck('8.3.2 initial position',position.subs(t,0),0);ck('8.3.2 initial velocity',s.diff(position,t).subs(t,0),0);ck('8.3.2 displacement',position.subs(t,3),s.exp(3)+R(11,4))
ck('8.3.3 first velocity',s.diff(2*t+4**t-4,t).subs(t,R(3,2)),2+8*s.log(4));ck('8.3.3 later acceleration',s.diff(t*(t+6),t,2),2)
position=-2*s.log(t)+s.cos(2*pi*t)/(4*pi*pi)+2*t-1/(4*pi*pi)-2;ck('8.3.4 acceleration',s.diff(position,t,2),2/t**2-s.cos(2*pi*t));ck('8.3.4 position condition',position.subs(t,1),0);ck('8.3.4 velocity condition',s.diff(position,t).subs(t,1),0)
position=-t*s.sin(t)/2-s.cos(t)/2+R(1,2);ck('8.3.5 velocity',s.diff(position,t),-t*s.cos(t)/2);ck('8.3.5 acceleration condition',s.diff(position,t,2).subs(t,pi),R(1,2));ck('8.3.5 initial position',position.subs(t,0),0);ck('8.3.5 displacement',position.subs(t,pi),1)
position=1-s.exp(-2*t);ck('8.3.6 initial speed',s.diff(position,t).subs(t,0),2);ck('8.3.6 force magnitude',-2*s.diff(position,t,2).subs(t,R(1,2)),8/s.E)
position=s.sqrt(t*t+15);ck('8.3.7 velocity',s.diff(position,t),t/s.sqrt(t*t+15));ck('8.3.7 acceleration',s.diff(position,t,2),15/(t*t+15)**R(3,2));ck('8.3.7 max speed',s.diff(position,t).subs(t,7),R(7,8))
r=[3*t*t,-5*s.sqrt(t)];vec('8.4.1 velocity',[s.diff(x,t).subs(t,9) for x in r],[54,-R(5,6)]);ck('8.4.1 speed',norm([s.diff(x,t).subs(t,1) for x in r]),R(13,2));near('8.4.1 direction',deg(s.atan(R(5,12))),22.6,.05)
vec('8.4.2 acceleration',[s.diff(s.cos(t),t).subs(t,pi),-5],[0,-5]);near('8.4.2 direction',90+deg(s.atan(R(1,5))),101,.5)
r=[t*(t+1),t**3-1];ck('8.4.3 distance',norm([x.subs(t,2) for x in r]),s.sqrt(85));vec('8.4.3 acceleration',[s.diff(x,t,2).subs(t,4) for x in r],[2,24]);vec('8.4.4 acceleration',[s.diff(s.exp(3*t),t,2).subs(t,2),s.diff(s.sin(2*pi*t),t,2).subs(t,2)],[9*s.exp(6),0])
r=[4*t,-3/(t+1)];ck('8.4.5 southeast',(r[0]+r[1]).subs(t,R(1,2)),0);near('8.4.5 speed',norm([s.diff(x,t).subs(t,R(1,2)) for x in r]),4.22,.005)
r=[2-3*t*t,-t*(t**3-4)];vec('8.4.6 actual initial',[x.subs(t,0) for x in r],[2,0]);ck('8.4.6 initial speed',norm([s.diff(x,t).subs(t,0) for x in r]),4);vec('8.4.6 parallel velocity',[s.diff(x,t).subs(t,1) for x in r],[-6,0]);vec('8.4.6 position',[x.subs(t,1) for x in r],[-1,3]);vec('8.4.6 displacement',[x.subs(t,1)-x.subs(t,0) for x in r],[-3,3])
r=[3*s.exp(2*t*(t+1)),-s.exp(t)];near('8.4.7 speed',norm([s.diff(x,t).subs(t,R(1,5)) for x in r]),13.6,.05);vec('8.4.7 acceleration',[s.diff(x,t,2) for x in r],[(48*t*t+48*t+24)*s.exp(2*t*(t+1)),-s.exp(t)])
r=[5*t*(t+1),3-t*t];vec('8.4.8 acceleration',[s.diff(x,t,2) for x in r],[10,-2]);ck('8.4.8 force',5*norm([10,-2]),10*s.sqrt(26))
v=[R(5,2)*t*t-2,2*t-2];vec('8.5.1 initial condition',[x.subs(t,2) for x in v],[8,2]);vec('8.5.1 acceleration',[s.diff(x,t) for x in v],[5*t,2]);near('8.5.1 speed',norm([x.subs(t,3) for x in v]),20.9,.05)
r=[3*t-1,3-R(2,3)*t**3];vec('8.5.2 velocity',[s.diff(x,t) for x in r],[3,-2*t*t]);vec('8.5.2 initial',[x.subs(t,0) for x in r],[-1,3])
r=[t*t/2-t**3+t+4,R(3,2)*t*t+2*t+1];vec('8.5.3 acceleration',[s.diff(x,t,2) for x in r],[1-6*t,3]);vec('8.5.3 initial velocity',[s.diff(x,t).subs(t,0) for x in r],[1,2]);vec('8.5.3 initial position',[x.subs(t,0) for x in r],[4,1]);near('8.5.3 distance',norm([x.subs(t,3) for x in r]),25.7,.05)
r=[(1-s.cos(pi*t))/pi**2,2*t/pi-2*s.sin(pi*t)/pi**2];vec('8.5.4 acceleration',[s.diff(x,t,2) for x in r],[s.cos(pi*t),2*s.sin(pi*t)]);vec('8.5.4 initial velocity',[s.diff(x,t).subs(t,0) for x in r],[0,0]);vec('8.5.4 initial position',[x.subs(t,0) for x in r],[0,0]);vec('8.5.4 velocity3',[s.diff(x,t).subs(t,3) for x in r],[0,4/pi]);vec('8.5.4 position4',[x.subs(t,4) for x in r],[0,8/pi])
v=[R(3,2)*t*t+2,-2*t];vec('8.5.5 acceleration',[s.diff(x,t) for x in v],[3*t,-2]);vec('8.5.5 initial',[x.subs(t,0) for x in v],[2,0]);near('8.5.5 speed',norm([x.subs(t,R(12,5)) for x in v]),11.7,.05);near('8.5.5 direction',deg(s.atan(R(960,3656))),14.7,.05)
vec('8.5.6 collision P',[2*2**2+2,1-2*R(5,4)*2],[10,-4]);vec('8.5.6 collision Q',[5*2,2-R(3,2)*2**2],[10,-4]);ck('8.5.7 horizontal positivity',R(3,2)*(t-R(1,3))**2+R(41,6),R(3,2)*t*t-t+7)
ck('setA bronze horizontal',15*3,45);ck('setA bronze vertical velocity',17-10*3,-13);ck('setA bronze height',17*3-5*9,6)
ck('setA silver parallel',35-10*R(5,2),10);ck('setA silver higher landing',(20**2+35**2-30**2)/20,R(145,4));T=R(7,2)+s.sqrt(5);ck('setA silver conditional impact speed',20**2+(35-10*T)**2,900);near('setA silver conditional range',20*T,115,.5)
ck('setA gold parallel',30*(20-10*4)-20*(10-10*4),0);ck('setA gold separation',norm([40,-40]),40*s.sqrt(2))
r=[4*t*t,3*t*(t*t-1)];vec('setB bronze derivative',[s.diff(x,t) for x in r],[8*t,9*t*t-3]);near('setB bronze speed',norm([s.diff(x,t).subs(t,6) for x in r]),325,.5);T=(4+s.sqrt(43))/9;ck('setB bronze northeast',9*T*T-3,8*T)
ck('setB silver vertical displacement',s.integrate(t**(-R(1,2))+1,(t,0,9)),15);near('setB silver distance',norm([27,15]),30.9,.05);T=4-2*s.sqrt(3);ck('setB silver due east',-2+2*(s.sqrt(3)-1)+T,0)
r=[s.cos(pi*t),3*s.sin(pi*t)**2];vec('setB gold velocity',[s.diff(x,t) for x in r],[-pi*s.sin(pi*t),6*pi*s.sin(pi*t)*s.cos(pi*t)]);near('setB gold first time',s.acos(R(1,6))/pi,.447,.0005)
ck('exam23 incompatible meeting times',int(R(10,3)!=R(11,3)),1)
for k in [2,-R(13,6)]:ck('exam27 speed for k '+str(k),(36*k+3)**2+20**2,25*241)
v=(8-5*s.exp(-2*t/5))/3;ck('exam30 acceleration',s.diff(v,t),R(2,3)*s.exp(-2*t/5));ck('exam30 initial',v.subs(t,0),1);near('exam30 velocity',v.subs(t,3),2.16,.005)
vec('exam33 final position',[4+6*(-R(17,3))+18*R(3,2),-2+6*R(1,6)+18*R(1,2)],[-3,8])
ck('exam39 height',18**2/(2*g),R(810,49));ck('exam39 range',23*36/g,R(4140,49));ck('exam39 parallel',18-g*R(295,98),-R(23,2));near('exam39 time',R(295,98),3.01,.005)
v=[R(3,2)*t*t+6*t-2,t*t-2*t+3];vec('exam44 acceleration',[s.diff(x,t) for x in v],[3*(t+2),2*(t-1)]);vec('exam44 initial',[x.subs(t,0) for x in v],[-2,3]);near('exam44 speed',norm([x.subs(t,R(6,5)) for x in v]),7.64,.005);T=-8+s.sqrt(74);ck('exam44 parallel',(v[0]-v[1]).subs(t,T),0);near('exam44 time',T,.602,.0005)
args.output.write_text(json.dumps(checks,indent=2)+'\n');print(len(checks),'independent checks passed')
