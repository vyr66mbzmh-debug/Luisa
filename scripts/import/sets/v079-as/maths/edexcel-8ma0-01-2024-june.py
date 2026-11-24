"""Independent calculations for June 2024 AS Pure Mathematics, in question order."""
from math import pi, sin, radians, log
from sympy import Matrix, Rational as R, diff, expand, factor, integrate, simplify, sqrt, symbols
x=symbols('x',positive=True)
assert simplify(diff(-4/sqrt(x)+3/x,x)-(2*sqrt(x)-3)/x**2)==0
assert expand((2*x+4)*(x-4)*(x-2))==2*x**3-8*x*x-8*x+32
assert Matrix([6,-3]).dot(Matrix([9,18]))==0
assert round(3*sin(radians(30))/(sin(radians(140))-sin(radians(30))),1)==10.5
assert factor(3*x**3-4*x*x-13*x-6)==(x-3)*(x+1)*(3*x+2)
assert expand((1-R(5,8)*x)**12).coeff(x,2)==R(825,32)
assert round(10**3.3)==1995 and round(10**(-.2),4)==.631
assert integrate(x**3-12*x+16,(x,-4,2))==108
assert 256==16**2 and 80*3.2==256
assert 5*5-3*5-10==0 and (3+1)**2+(15-13)**2==20
assert round(log(6)/.06,1)==29.9
assert diff(2*x+200/x,x).subs(x,10)==0 and (100-25*pi)/20>1
assert factor(3*x*x-4*x-4)==(x-2)*(3*x+2)
assert expand(x*(x+1)+4*x)==x*x+5*x
