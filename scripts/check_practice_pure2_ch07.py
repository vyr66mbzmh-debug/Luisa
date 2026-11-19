"""Independent exact identities, equation roots, extrema and model checks."""
import math as m
import sympy as s
x,a,b=s.symbols('x a b',real=True)
R=s.Rational
checks=0
def eq(left,right):
 global checks
 assert s.simplify(s.trigsimp(s.cancel(s.expand_trig((left-right).replace(s.tan,lambda z:s.sin(z)/s.cos(z))))))==0,(left,right)
 checks+=1
def near(left,right,tol=1e-9):
 global checks
 assert abs(left-right)<tol,(left,right)
 checks+=1
sin,cos,tan=s.sin,s.cos,s.tan
for lhs,rhs in [
 (sin(x-s.pi/3),sin(x)/2-s.sqrt(3)*cos(x)/2),
 (cos(x-s.pi/6),s.sqrt(3)*cos(x)/2+sin(x)/2),
 (cos(a-b),cos(a)*cos(b)+sin(a)*sin(b)),
 (2*sin(x+5*s.pi/6)+2*sin(x+10*s.pi/6),(1-s.sqrt(3))*(sin(x)+cos(x))),
 (sin(s.pi/12+s.pi/4),s.sqrt(3)/2),(cos(s.pi/4),s.sqrt(2)/2),
 (tan(s.pi/12),2-s.sqrt(3)),(sin(7*s.pi/12),(s.sqrt(6)+s.sqrt(2))/4),
 (R(3,5)*R(15,17)-R(4,5)*R(8,17),R(13,85)),
 ((R(4,3)-R(8,15))/(1+R(4,3)*R(8,15)),R(36,77)),
 (R(24,25)*R(-5,13)+R(-7,25)*R(-12,13),R(-36,325)),
 ((R(-24,7)-R(12,5))/(1+R(-24,7)*R(12,5)),R(204,253)),
 (R(-7,25)*R(-5,13)-R(24,25)*R(-12,13),R(323,325)),
 (2*R(-5,12)/(1-R(25,144)),R(-120,119)),(1-2*R(5,13)**2,R(119,169)),
 (2-10*cos(2*x),R(4,5)*(5*sin(x))**2-8),
 ((4/cos(x))**2,32/(cos(2*x)+1)),
 (cos(x)**4-sin(x)**4,cos(2*x)),
 (sin(2*x)-tan(x),tan(x)*cos(2*x)),
 (sin(6*x)/(1-cos(6*x)),cos(3*x)/sin(3*x)),
 (1/cos(x)*tan(2*x)/4,sin(x)/(2*cos(2*x))),
 (cos(x-s.pi/6)-cos(x+s.pi/6),sin(x)),
 (2*sin(3*x+s.pi/3),sin(3*x)+s.sqrt(3)*cos(3*x)),
 (cos(3*x),4*cos(x)**3-3*cos(x)),
 (cos(2*x)/sin(2*x)+tan(x),1/sin(2*x)),
 (2*sin(2*x-s.pi/4),2*s.sqrt(2)*sin(x)*cos(x)-s.sqrt(2)+2*s.sqrt(2)*sin(x)**2),
 (7*cos(x)**2-3*sin(x)**2-8*sin(x)*cos(x),5*cos(2*x)-4*sin(2*x)+2),
 (R(15,2)*sin(4*x)-4*cos(4*x)-4*cos(2*x)-4,cos(2*x)*(15*sin(2*x)-8*cos(2*x)-4)),
 (sin(3*x),3*sin(x)-4*sin(x)**3),
 (2*(2*R(13,14)**2-1)**2-1,R(239,4802)),
 (30*sin(x)*cos(x)-16*cos(x)**2,15*sin(2*x)-8*cos(2*x)-8),
 ]:eq(lhs,rhs)
# Enumerate complete two-branch solution sets independently from each periodic form.
def periodic(seeds,period,lo,hi):return sorted({round(v+n*period,13) for v in seeds for n in range(-10,11) if lo-1e-12<=v+n*period<=hi+1e-12})
def roots(f,seeds,period,lo,hi,expected):
 global checks
 found=periodic(seeds,period,lo,hi)
 assert len(found)==len(expected),(found,expected)
 checks+=1
 for r,v in zip(found,expected):near(f(r),0,1e-8);near(r,v,0.00051)
pi=m.pi
roots(lambda t:m.sin(t+pi/3)+4*m.sin(t),[-m.atan(m.sqrt(3)/9)],pi,0,2*pi,[2.951,6.093])
roots(lambda t:m.cos(t+pi/6)-m.sin(t),[pi/6],pi,0,2*pi,[.524,3.665])
beta=m.acos(1/(2*m.sqrt(2)))
roots(lambda t:m.cos(t+pi/4)+m.sin(t+pi/4)-.5,[beta,-beta],2*pi,0,2*pi,[1.209,5.074])
beta=m.acos(1/m.sqrt(5))
roots(lambda t:1+m.cos(2*t)-7*m.cos(t)**2+1,[beta,-beta],pi,0,pi,[1.107,2.034])
for t in [0,m.acos(1/8),pi]:near(m.sin(2*t)-m.sin(t)/4,0)
beta=m.atan(m.sqrt(3/5))
roots(lambda t:m.tan(t)*m.tan(2*t)-3,[beta,-beta],pi,0,pi,[.659,2.483])
roots(lambda t:2*m.sin(t-pi/6)-m.sin(t+pi/2),[m.atan(2/m.sqrt(3))],pi,-pi,pi,[-2.285,.857])
for t in [-pi,-m.acos(.75),m.acos(.75),pi]:near(2*m.sin(t)**2-m.cos(2*t)-m.cos(t),0)
for t in [-pi,-m.atan(2/3),0,pi-m.atan(2/3)]:near(m.cos(t)**2-2*m.sin(t)**2-m.sin(2*t)-1,0)
a=m.atan(2/3);beta=m.acos(1/m.sqrt(13))
roots(lambda t:3*m.cos(2*t)+2*m.sin(2*t)-1,[(a+beta)/2,(a-beta)/2],pi,-pi,pi,[-2.203,-.351,.939,2.791])
a=m.atan(.5);beta=m.asin(1/(2*m.sqrt(5)))
roots(lambda t:2*m.sin(t)-m.cos(t)-.5,[a+beta,a+pi-beta],2*pi,-pi,2*pi,[-2.903,.689,3.380])
a=m.atan(5/12);beta=m.asin(3/13)
roots(lambda t:12-3/m.sin(2*t)-5*m.cos(2*t)/m.sin(2*t),[(a+beta)/2,(a+pi-beta)/2],pi,0,2*pi,[.314,1.652,3.455,4.793])
a=m.atan(4/5);beta=m.acos(2/m.sqrt(41))
roots(lambda t:7*m.cos(t)**2-3*m.sin(t)**2-8*m.sin(t)*m.cos(t)-4,[(-a+beta)/2,(-a-beta)/2],pi,0,2*pi,[.289,2.178,3.431,5.319])
a=m.atan(8/15);beta=m.asin(4/17)
for t in [(a+beta)/2,(a+pi-beta)/2,pi/4,3*pi/4]:near(7.5*m.sin(4*t)-4*(m.cos(4*t)+m.cos(2*t)+1),0)
# A direct counterexample sequence proves no finite reciprocal maximum.
for epsilon in [.1,.01,.001]:
 t=(a+m.asin((8+epsilon)/17))/2
 near(30*m.sin(t)*m.cos(t)-16*m.cos(t)**2,epsilon)
 near(1/(30*m.sin(t)*m.cos(t)-16*m.cos(t)**2),1/epsilon,1e-6)
for t in [-pi/4,0,pi/4,m.atan(2)]:near((1/m.cos(t)**2+3)*(m.sin(2*t)-m.tan(t))-4*m.tan(t)**2*m.cos(2*t),0)
a=m.atan(5/3);beta=m.acos(4/m.sqrt(34))
roots(lambda t:1.5*m.cos(2*t)+2.5*m.sin(2*t)-2,[(a+beta)/2,(a-beta)/2],pi,-pi,pi/2,[-3.034,-2.219,.108,.923])
# Extremum coordinates and all three transformed graph intercepts.
for f,points in [(lambda t:m.sqrt(3)*m.sin(t)-m.cos(t),[(0,-1),(pi/6,0),(2*pi/3,2),(7*pi/6,0),(5*pi/3,-2)]),(lambda t:2*m.cos(t)-m.sqrt(12)*m.sin(t),[(0,2),(pi/6,0),(2*pi/3,-4),(7*pi/6,0),(5*pi/3,4)]),(lambda t:2*m.sin(t)+2*m.cos(t),[(0,2),(pi/4,2*m.sqrt(2)),(3*pi/4,0),(5*pi/4,-2*m.sqrt(2)),(7*pi/4,0)])]:
 for t,v in points:near(f(t),v)
near(30+.2*m.cos(2)+.35*m.sin(2),30.23502473207956)
for n in range(3):
 t=m.atan(7/4)/2+n*pi
 near(30+.2*m.cos(2*t)+.35*m.sin(2*t),30+m.sqrt(65)/20)
near((200+132*m.sin(9.6)-72*m.cos(9.6)-128)*20,2397.7278099148766)
a=m.atan(6.5/12.5);amp=m.sqrt(794)/2
near((pi+a)/1.05,3.448678043411799)
near(16-12.5*m.cos(4.2)-6.5*m.sin(4.2),27.793503,1e-6)
for t in [(a+m.acos(1/amp))/1.05,(a+2*pi-m.acos(1/amp))/1.05]:near(16-12.5*m.cos(1.05*t)-6.5*m.sin(1.05*t),15)
print(f'{checks} independent exact/numerical checks passed')
