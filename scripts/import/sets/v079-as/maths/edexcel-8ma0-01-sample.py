"""Independent calculations for AS Pure Mathematics Sample Assessment Material."""
from math import sin,radians,log10,sqrt as root,pi
from sympy import Rational as R, diff, expand, factor, integrate, solve, sqrt, symbols
x=symbols('x',positive=True)
assert 1+3*3==-2+3*4==10
assert diff(2*x*x-12*x+16,x).subs(x,5)==8
assert sqrt(5**2+10**2)==5*sqrt(5)
assert expand((x-3)*(4*x*x+2))==4*x**3-12*x*x+2*x-6
assert integrate(2*x+3+12/x**2,(x,1,2*sqrt(2)))==16+3*sqrt(2)
h=symbols('h')
assert expand(3*(x+h)**2-3*x*x)==6*x*h+3*h*h
assert expand((2-x/2)**7).coeff(x,2)==168 and 2-.01/2==1.995
assert round(450*sin(radians(70))*sin(radians(60))/sin(radians(50)))==478
assert expand(-(3*x-1)*(4*x-1))==12*(1-x*x)+7*x-13
assert factor(16*x*x-12*x)==4*x*(4*x-3)
assert expand((x-h)**2)==x*x-2*x*h+h*h and root((-1)*(-1))>(-1-1)/2
assert solve(16*x*x-9*x,x)==[R(9,16)]
assert factor(x**3+10*x*x+25*x)==x*(x+5)**2
assert round(200*log10(2))==60 and 10**5==100000
assert diff(4*x*x-6*x+4,x).subs(x,R(1,2))==-2
assert round(2*root(250*(2+pi/2)),1)==59.8
assert 6+5+12*10/5-(6-5-12*10/5)==58
