"""Independent symbolic checks of variable-acceleration solutions."""
import sympy as s
T=s.symbols('t',real=True)
R=s.Rational
n=0
def eq(a,b):
 global n
 assert s.simplify(a-b)==0,(a,b)
 n+=1
def at(expr,t):return expr.subs(T,t)
def derivative(expr,v,a=None):
 eq(s.diff(expr,T),v)
 if a is not None:eq(s.diff(expr,T,2),a)
x=3*T**3-2*T**2;eq(at(x,2),16);eq(at(x,R(2,3)),0)
v=3*T**2-14*T+8
for t in [R(2,3),4]:eq(at(v,t),0)
eq(at(v,5),13);eq(at(v,R(7,3)),-R(25,3));eq(at(v,3),-7)
x=6*T**2-T**3;eq(at(x,5)-at(x,3),-2);eq(at(x,4)-at(x,3),5)
x=(5*T-T**2)/4;eq(at(x,R(5,2)),R(25,16));eq(at(x,5),0)
v=2*T**2-13*T+15
for t in [R(3,2),5]:eq(at(v,t),0)
for t in [R(1,2),6]:eq(at(v,t),9)
eq(at(v,R(13,4)),-R(49,8));eq(at(5*T**2-T**3,3)-at(5*T**2-T**3,2),6)
eq(at(10*T-T**2,5),25)
for expr,expected in [(4*T**3-T,47),(2*T+T**2-1,6),(T+1/T,R(3,4))]:eq(at(s.diff(expr,T),2),expected)
for expr,v,a in [(R(3,4)*T**4-T**-2,3*T**3+2*T**-3,9*T**2-6*T**-4),((3*T-5)*(2*T**2+1),18*T**2-20*T+3,36*T-20),((2*T**4-3*T**2+8)/(4*T),R(3,2)*T**2-R(3,4)-2*T**-2,3*T+4*T**-3)]:derivative(expr,v,a)
x=2*T**3-5*T**2+8;eq(at(s.diff(x,T),4),56);eq(at(s.diff(x,T),R(5,3)),0);eq(at(s.diff(x,T,2),2),14)
eq(at(20+T-T**2,5),0);eq(at(s.diff(20+T-T**2,T),5),-9)
x=(2*T**3-21*T**2+60*T+90)/3
for t in [2,5]:eq(at(s.diff(x,T),t),0);eq(abs(at(s.diff(x,T,2),t)),6)
eq(at(x,2)-at(x,5),9)
v=2*T**2-17*T+21
for t in [R(3,2),7]:eq(at(v,t),0)
eq(at(v,R(17,4)),-R(121,8));eq(at(v,6),-9)
x=6*T**3-5*T**2+12;eq(at(s.diff(x,T),1),8)
for t in [0,R(5,9)]:eq(at(s.diff(x,T),t),0);eq(abs(at(s.diff(x,T,2),t)),10)
v=T*(8-T)**2/10
for t,val in [(R(8,3),R(1024,135)),(8,0)]:eq(at(s.diff(v,T),t),0);eq(at(v,t),val)
eq(at(v,10),4)
x=3*T+T**2/4-T**3/4;root=(1+s.sqrt(37))/3;eq(at(s.diff(x,T),root),0)
assert 5.185<float(at(x,root))<5.195;n+=1
v=T**2*(T-5)**2;eq(s.diff(v,T),2*T*(T-5)*(2*T-5));eq(at(v,R(5,2)),R(625,16));eq(at(v,6),36)
x=T**3/2-R(45,100)*T**2-R(21,10)*T+6
for expr,result in [(s.diff(x,T,2),0),(x,R(5343,1000)),(s.diff(x,T),-R(2235,1000))]:eq(at(expr,R(3,10)),result)
x=5*T**3-T**4;eq(at(s.diff(x,T),R(15,4)),0);eq(at(x,R(15,4)),R(16875,256))
x=T**3/2-R(3,10)*T**2-R(4,5)*T+6;eq(at(s.diff(x,T,2),R(1,5)),0);eq(at(x,R(1,5)),R(5832,1000))
eq(3*T**2-6*T+8,3*(T-1)**2+5)
x=R(24,5)*T+R(6,5)*T**2-T**3/100;root=40+4*s.sqrt(110);eq(at(s.diff(x,T),root),0)
assert 2948.7<float(at(x,root))<2948.8;n+=1
print('car maximum',float(at(x,root)))
eq(at(x,100),2480)
v=3*T**2-18*T+28;eq(at(v,0),28);eq(at(v,3),1);eq(at(s.diff(v,T),4),6)
for a,v in [(4*T**2-3*T**3,R(4,3)*T**3-R(3,4)*T**4),(5*T+R(3,2)*T**2,R(5,2)*T**2+T**3/2),(2*T**2-T,R(2,3)*T**3-T**2/2)]:eq(s.diff(v,T),a);eq(at(v,0),0)
for v,x,dist in [(2*T**3-T/3+1,T**4/2-T**2/6+T,42),(T*(2*T**2+T**3)/3,T**4/6+T**5/15,R(297,10)),(5*T**2+3*s.sqrt(T)/2,R(5,3)*T**3+T**R(3,2),45+3*s.sqrt(3))]:eq(s.diff(x,T),v);eq(at(x,3)-at(x,0),dist)
v=10+3*T-2*T**2;eq(s.integrate(v,(T,0,2))+5,R(77,3))
v=4*T**2-20*T+21;eq(s.integrate(v,(T,R(3,2),R(7,2))),-R(16,3))
v=T**2/2-3*T+4;eq(s.integrate(v,(T,2,4)),-R(2,3));eq(at(v,2),0);eq(at(v,4),0)
eq(at(R(5,2)*T**2+9*T+3,R(2,5)),7)
x=T**2*(30-T**2)/8;eq(at(s.diff(x,T),2),11);eq(s.diff(x,T,2),R(3,2)*(5-T**2));eq(at(x,0),0)
v=5+8*T**2-2*T**3;eq(at(s.diff(v,T),R(8,3)),0);eq(s.integrate(v,(T,0,R(8,3))),R(3128,81))
for x,a in [(3*T-2*T**3,-12*T),(T**2-7*T,2),(5/T+8,10/T**3),(16-T**2/2,-1),(s.Integer(10),0)]:eq(s.diff(x,T,2),a)
eq(at(32*T-R(3,10)*T**2,50),850)
x=3*T**2-5*T+6
for expr,result in [(x,8),(s.diff(x,T),7),(s.diff(x,T,2),6)]:eq(at(expr,2),result)
x=T**3-8*T**2+5*T;eq(at(x,R(1,3)),R(22,27));eq(at(x,5),-50);eq(s.diff(x,T,2),6*T-16)
x=T*(T**2-9*T+15);eq(at(x,1),7);eq(at(x,5),-25)
x=T**2*(T**2-6*T+10)/3;eq(s.diff(x,T),R(2,3)*T*(2*T-5)*(T-2));eq(at(x,2),R(8,3));eq(at(x,R(5,2)),R(125,48));eq(at(x,3),3)
eq(2*at(x,2)-2*at(x,R(5,2))+at(x,3),R(25,8))
eq(s.integrate(6+5*T-T**2,(T,0,6)),54);eq(at(6+5*T-T**2,6),0)
v=9*T-3*T**2;eq(at(v,R(3,2)),R(27,4));eq(s.integrate(v,(T,0,3)),R(27,2))
x=13*T**2-2*T**3;eq(s.diff(x,T,2),26-12*T);eq(at(s.diff(x,T),R(13,3)),0);eq(2*at(x,R(13,3))-at(x,5),R(2369,27));eq(at(x,R(13,2)),0)
eq(s.integrate(2*T**2-3*T+4,(T,0,R(3,4))),R(39,16))
v=R(5,8)*T**2-R(15,4)*T+10;eq(at(v,2),5);eq(at(s.diff(v,T),3),0);eq(at(s.diff(v,T),4),R(5,4));eq(s.integrate(v,(T,2,3)),R(55,12))
t=80-8*s.sqrt(70);eq(at(25*T-R(3,10)*T**2,t),480-15*t-t**2/20)
assert 275.45<float(at(25*T-R(3,10)*T**2,t))<275.55;n+=1
derivative((2-T)**4,4*(T-2)**3,12*(T-2)**2)
x=R(3,2)*T**2-1/T-4*T+R(7,2);derivative(x,3*T+T**-2-4,3-2*T**-3);eq(at(x,1),0);eq(at(s.diff(x,T),1),0)
v=6-4*T**-2;eq(at(v,1),2);eq(s.limit(v,T,s.oo),6);eq(s.diff(v,T),8*T**-3)
print(n,'independent symbolic and motion checks passed')
