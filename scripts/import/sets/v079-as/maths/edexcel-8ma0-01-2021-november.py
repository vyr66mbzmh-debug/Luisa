from math import asin,comb,degrees,log
from sympy import Rational as R,diff,discriminant,expand,factor,integrate,simplify,sqrt,symbols
x,h=symbols('x h')
assert factor(x*x-x-20)==(x-5)*(x+4) and expand(2*(x-1)-(2*x-8+2))==4
assert simplify(diff(3*x*x/4+1/x**2,x)-(3*x**4-4)/(2*x**3))==0
assert 36**2+15**2==39**2 and 2*12==24
assert simplify((3*(2+h)**2-12)/h)==12+3*h
assert expand(x*(x-6)*(3*x+1))==3*x**3-17*x*x-6*x
assert 149<180-degrees(asin(50/98))<150
assert comb(8,5)*8*R(3,2)**5==3402
assert integrate(6/sqrt(x),(x,R(16,9),9))==20
assert factor((2*x+1)**3-(2*x+1))==4*x*(x+1)*(2*x+1)
assert round(log(20/45)/14,4)==-.0579
assert round(10**2.25*5**-.235)==122
assert integrate(3*(x-2)**2,(x,0,2))==8
assert abs(7-3*4)==abs(7-12+3*R(10,3))
f=-2*x**3+15*x*x-39*x+44
assert f.subs(x,2)==10 and f.subs(x,4)==0 and discriminant(diff(f,x),x)<0
