"""Independent calculations for AS Pure Mathematics Specimen Paper."""
from math import degrees,asin,log
from sympy import Rational as R, diff, expand, factor, integrate, simplify, sqrt, symbols
x=symbols('x',positive=True)
assert expand(2*(x-1)*(3*x+1))==6*x*x-4*x-2
assert (6-4,-3-2)==(2,-5) and (8,-20)==(4*2,4*(-5))
assert round((2.8-4)/36,6)==round(-1/30,6) and 4+24/30==4.8
assert 2*(-1.5)==-3 and 7-1==6
assert simplify((x**3+3*x*x-4*x-12)/(x**3+5*x*x+6*x)-(1-2/x))==0
assert 8**2-8-1==55 and 55%5==0
assert expand((1+3/x)**2*(1+3*x/4)**6).coeff(x,1)==R(2097,16)
assert integrate(sqrt(x),(x,1,2**R(8,3)))==10
assert factor((2-x)**2-4*(x+5))==x*x-8*x-16
assert (2+2)**2+(5-3)**2==20 and 3-2*(2+2)==-5
assert round((degrees(asin(-.6))-10)/2,1)==-23.4
assert 3*R(64,25)-2*R(8,5)==8*R(64,25)-16
assert round(24*log(500)/.3)==497
f=(x-2)**2*(x+3)
assert integrate(f,(x,-R(4,3),2))==R(2500,81)
