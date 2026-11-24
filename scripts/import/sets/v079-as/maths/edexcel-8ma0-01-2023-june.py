"""Independent calculations for June 2023 AS Pure Mathematics, in question order."""
from math import cos, radians, sqrt as root, exp
from sympy import Rational as R, diff, expand, factor, integrate, solve, sqrt, symbols
x = symbols('x')
assert factor(2*x*x-7*x-4) == (x-4)*(2*x+1)
assert solve(6*x*x+7*x-20,x)==[-R(5,2),R(4,3)]
assert round(root(8.2**2+15.6**2-2*8.2*15.6*cos(radians(33))),1)==9.8
assert solve(16/x<=2,x).subs(x,-1) and not solve(16/x<=2,x).subs(x,1)
assert integrate(20-4*x*x,(x,0,sqrt(5)))==40*sqrt(5)/3
assert expand((x-3)**2+25-34)==x*x-6*x
assert (25-40)/(200-80)==-1/8 and 50-400/8==0
assert 2*10*(10-6)==2*10+60==80
assert solve((3*x-2)**2-25*x,x)==[R(1,9),4]
assert (R(40,3)-6)/(R(3,5)+R(5,3))==R(55,17)
assert round(34*exp(-.8),1)==15.3
assert 2*1800*3/360==30
assert sqrt((-18)**2+12**2)==6*sqrt(13) and -3+R(2,3)*12==5
assert expand((5+8*x*x)*(3-x/2)**6).coeff(x,5)==-R(8685,16)
assert expand(-(x-1)*(x*x-4*x-6))== -x**3+5*x*x+2*x-6
a,b=symbols('a b')
assert solve([16+2*a+b,32+R(16,3)*a+4*b-8],(a,b))=={a:-15,b:14}
assert (6**3-1)%5==0 and expand((2*x+2)**3-(2*x)**3)/8==3*x**2+3*x+1
