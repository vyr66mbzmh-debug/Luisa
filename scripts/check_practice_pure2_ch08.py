"""Independent substitution, interval extrema, intersections and model checks."""
import math as m
import sympy as s
t,x=s.symbols('t x',real=True)
R=s.Rational
n=0
def eq(a,b):
 global n
 assert s.simplify(s.trigsimp(s.expand_trig(a-b)))==0,(a,b)
 n+=1
def near(a,b,tol=1e-9):
 global n
 assert abs(float(a)-b)<tol,(a,b)
 n+=1
# Cartesian equations checked by substitution into original parametrisations.
for X,Y,F in [
(t-3,t*t-1,(x+3)**2-1),(2/t,t*t+1,4/x**2+1),(2*t-1,3/t**2,12/(x+1)**2),
(s.log(t+2),1/(t+3),1/(s.exp(x)+1)),(s.log(t+4),t*t+10*t+25,(s.exp(x)+1)**2),
(s.exp(2*t),s.exp(6*t)+2*s.exp(4*t),x**3+2*x*x),
(s.sqrt(t)+1,2*s.sqrt(t)+7,2*x+5),(2*t+1,4*t*t+14*t+12,x*x+5*x+6),
(s.log(2-t),5-t,s.exp(x)+3),(3*t,(1-t)*(9-t),x*x/9-10*x/3+9),
(s.log(t+5),2*t+12,2*s.exp(x)+2),(s.exp(3*t),s.exp(9*t)-2*s.exp(6*t)-5*s.exp(3*t)+6,(x+2)*(x-1)*(x-3)),
(5*t*t,3*t*t+2,3*x/5+2),(3*s.sqrt(t)-3,9-5*s.sqrt(t),4-5*x/3),
(s.sin(t),s.cos(2*t),1-2*x*x),(s.sin(t),s.sin(2*t)**2,4*x*x-4*x**4),
(2*s.cos(t)/s.sin(t),4/s.sin(t)**2-8,x*x-4),(10*s.sin(t),1/(5*s.sin(t)**2),20/x**2),
(5/s.cos(2*t)**2,2*s.cos(2*t)**2/s.sin(2*t)**2,10/(x-5)),
(2*t+2,t*t,(x-2)**2/4),(t+5,1/t,1/(x-5)),(2*t,R(5,2)-t,R(5,2)-x/2),
(1/t,2/t,2*x),(2*t+1,12-6*t,15-3*x),(t+2,-5*t-t*t,(2-x)*(x+3)),
(R(18,5)*t,R(27,10)*t,3*x/4),(9*s.sqrt(2)*t,-R(54,11)*t*t+9*s.sqrt(2)*t,x-x*x/33),
(t+5,5*t-2,5*x-27),(R(38,5)*t,-R(49,10)*t*t+R(163,10)*t,-R(245,2888)*x*x+R(163,76)*x),
(t+1,(2*t+2)*(2-t),6*x-2*x*x),(s.sqrt(t),2*s.sqrt(t)-4*t*t,2*x-4*x**4),
(s.cos(t)/6,s.cos(3*t),18*x*(48*x*x-1))]:eq(Y,F.subs(x,X))
for X,Y,A,B,k in [(s.sin(t)-1,s.cos(t)+3,-1,3,1),(2+2*s.cos(t),5+2*s.sin(t),2,5,4),(s.sin(t)+3,s.cos(t)-4,3,-4,1),(6*s.cos(t)+5,6*s.sin(t)-2,5,-2,36),(10*s.cos(t)+3,10*s.sin(t)-2,3,-2,100),(5*s.cos(t)-4,5*s.sin(t)+1,-4,1,25)]:eq((X-A)**2+(Y-B)**2,k)
eq((2*s.sin(t))**2/4+(3*s.cos(t))**2/9,1)
eq((4/s.cos(t))**2/16-(2*s.tan(t))**2/4,1)
eq((3/s.sin(t))**2-(3*s.cos(t)/s.sin(t))**2,9)
eq((8*t**3)**2,(4*t*t)**3)
eq((4*t)**2,8*(2*t*t))
# Exact vertices, endpoint images and all table entries.
for F,points in [((x+3)**2-1,[(-6,8),(-3,-1),(0,8)]),(x*x+5*x+6,[(-5,6),(R(-5,2),R(-1,4)),(-3,0),(-2,0),(0,6),(1,12)]),((x-15)**2/9-16,[(0,9),(3,0),(15,-16),(24,-7)]),((2-x)*(x+3),[(-3,0),(R(-1,2),R(25,4)),(0,6),(2,0),(3,-6)])]:
 for v,w in points:eq(F.subs(x,v),w)
for k in range(-4,7):
 v=R(k,2);X=2*v+2;Y=v*v;eq(Y,(X-2)**2/4)
for k in range(9):
 X=3*s.sin(k*s.pi/4);Y=5*s.cos(k*s.pi/4);eq(X*X/9+Y*Y/25,1)
# Axis and line intersections verified in the original equations.
for X,Y,values in [(t-3,t+4,[-4,3]),(3*t,3*(t+2)*(t-1),[-2,1,0]),(2*t*t-2,t*t-4*t,[0,4,-1,1])]:
 for v in values:eq((X*Y).subs(t,v),0)
for v in [-1,-6]:eq(((t+1)**2+(t+3)**2+6*(t+1)-4).subs(t,v),0)
for v in [0,s.log(3)]:eq((4*s.exp(t)-4-(s.exp(2*t)-1)).subs(t,v),0)
for v in [s.pi/2,s.pi]:eq((2*s.sin(2*t)+1).subs(t,v),1)
for v in [7*s.pi/12,11*s.pi/12]:eq((2*s.sin(2*t)+1).subs(t,v),0)
for v in [7+3*s.sqrt(3),7-3*s.sqrt(3)]:eq(18*(v-1),(v+2)**2)
eq((R(3,1)*(1+2*t)).subs(t,R(1,2)),6)
eq((R(1,2)*t*t-1).subs(t,3),R(7,2))
for X,Y in [(2,4*s.sqrt(3)),(-4,0)]:eq(3*Y-2*s.sqrt(3)*X-8*s.sqrt(3),0)
# Physical models: exact times, ranges, widths, radii and arrival times.
eq(R(27,10)*R(500,3),450);eq(s.sqrt(600**2+450**2),750);eq(750/R(500,3),R(9,2))
near(16-7.6*17/8-m.cos(17),.125163338051596)
eq((-R(49,10)*t*t+R(21,10)*t).subs(t,R(3,7)),0)
for v in [R(1,7),R(2,7)]:eq((-R(49,10)*t*t+R(21,10)*t).subs(t,v),R(1,5))
for v in [-s.pi/3,s.pi/3]:eq(8-16*s.cos(v),0);eq((18*v-32*s.sin(v))**2,(16*s.sqrt(3)-6*s.pi)**2)
near(64-18*m.pi,7.451332235383724);near(16*m.sqrt(3)-6*m.pi,8.863256999563276)
eq(((t*t-6*t+5)/(t+1)).subs(t,14),R(39,5));eq((5*t-2).subs(t,R(14,5)),12)
for u in [s.pi/2+s.pi/15,3*s.pi/2+s.pi/15]:eq(s.cos(u-s.pi/15),0)
near(-20/(3*m.pi*m.pi/4+8*m.pi),-.614724,1e-6)
# Elimination and extremum proof for the three problem-solving curves.
X=10*s.sin(t);Y=5*s.sin(2*t);eq(100*(Y*Y-X*X)+X**4,0)
X=2*s.sin(t)/s.sqrt(3);Y=4*s.cos(t+s.pi/3);eq((3*X+Y)**2+3*X*X-4,0)
X=2+2*s.cos(t);Y=2*s.sin(t)+s.sin(2*t);eq(Y*Y,X**3*(1-X/4))
eq(s.diff(X+Y,t),2*(s.cos(t)-s.sin(t))*(1+s.cos(t)+s.sin(t)))
for v,target in [(0,4),(s.pi/4,3+2*s.sqrt(2)),(3*s.pi/4,1)]:eq((X+Y).subs(t,v),target)
near(m.hypot(16*m.sin(4),32*m.cos(8-8*m.pi/3)),32.116,0.001)
for v in [0,s.pi/4]:eq(16*s.sin(4*v),0);eq(32*s.cos(8*v-8*s.pi/3),-16)
eq(s.exp(2*(5*s.log(5)-2*s.log(2))),R(9765625,16))
eq(s.sqrt(10)-7+10/s.sqrt(10),2*s.sqrt(10)-7)
# Exam curve extrema, line consistency and parametric area.
T=(23+2*s.sqrt(22))/49;eq(-R(49,10)*T*T+R(23,5)*T+R(19,10),R(14,5))
eq((2*s.sqrt(t)-4*t*t).subs(t,R(1,4)),R(3,4))
for v,target in [(R(-1,12),1),(R(1,12),-1)]:eq((18*x*(48*x*x-1)).subs(x,v),target);eq(s.diff(18*x*(48*x*x-1),x).subs(x,v),0)
for X,Y in [(1,4),(25,28)]:eq(Y,X+3)
for X,Y in [(4,10),(9,16)]:eq(5*Y-6*X-26,0)
eq((80*t-20*t*t).subs(t,4),0);eq((80*t-20*t*t).subs(t,2),80)
eq(((80-40*t)/(20/s.sqrt(t))).subs(t,4),-8)
eq(s.integrate((80*t-20*t*t)*20/s.sqrt(t),(t,0,4)),R(10240,3))
print(f'{n} independent exact/numerical checks passed')
