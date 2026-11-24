from math import asin,atan2,degrees,log
from sympy import Rational as R,diff,expand,factor,integrate,simplify,sqrt,symbols
x=symbols('x')
assert 6*2**2-4==20 and 13-2*20==-27
assert round(degrees(atan2(-7,-3))%360,1)==246.8
assert simplify((6+3*sqrt(2))*(sqrt(2)-1)-sqrt(18))==0 and 6*R(5,12)-4==-R(3,2)
assert 190-21*19/8==140.125
assert 128<180-degrees(asin(12*.4539905/7))<130
assert factor(120*x**3-30*x)==30*x*(2*x-1)*(2*x+1)
assert 3*R(16,9)+5*R(4,3)-12==0
assert round(8*log(65/17),1)==10.7
assert 3*(1-R(1,3)**2)==8*R(1,3)
assert expand((x-5)*(x+2)*(2*x+7))==2*x**3+x*x-41*x-70
assert (-5+9)**2+(7-1)**2==52
assert round(10**2.379)==239
assert expand((2*x-1)**2)==4*x*x-4*x+1
g=-3*x**3+R(39,4)*x*x-3*x
assert g.subs(x,2)==9 and diff(g,x).subs(x,2)==0 and diff(g,x,2).subs(x,2)<0
