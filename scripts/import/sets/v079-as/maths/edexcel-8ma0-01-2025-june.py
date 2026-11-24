"""Independent calculations for June 2025 AS Pure Mathematics, in question order."""
from math import acos, degrees, hypot, sqrt, log
from sympy import Rational as R, diff, expand, factor, integrate, simplify, solve, symbols
x=symbols('x',positive=True)
assert (2-2,-7)==(0,-7)
assert (22-0)/(2.5+3)==4 and 4*(-3)+12==0
assert hypot(-2,-6)==sqrt(40) and round(degrees(acos(31/(sqrt(73)*sqrt(29)))),1)==47.6
assert 25+4-1==28
assert simplify(diff(x**5/20-6*x**R(1,2),x)-(x**5-12*x**R(1,2))/(4*x))==0
a,b=symbols('a b')
assert solve([-3*a+b-5,12*a+4*b+4],(a,b))=={a:-1,b:2}
assert expand(450-(x-130)**2)==-x**2+260*x-16450
assert round(degrees(acos(1/sqrt(5)))/3,1)==21.1
assert expand((3*x+4)*(3*x-4))==9*x*x-16
assert factor((x+1)**2-3*(x+7))==(x-5)*(x+4)
assert diff(180000/x+x*x,x).subs(x,90000**R(1,3)).simplify()==0
assert factor(3*x*x+9*x)==3*x*(x+3)
assert abs(31-31.25*.8-6)<1e-10 and abs(31-31.25*.8**2-11)<1e-10
assert expand((1+x)**8).coeff(x,2)==28
assert 1**3+4==5 and 2**3+8==16 and expand(x*(x*x+5))==x**3+5*x
