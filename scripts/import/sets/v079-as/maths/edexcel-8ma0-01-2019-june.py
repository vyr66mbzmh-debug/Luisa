from sympy import Rational as R,diff,expand,factor,integrate,sqrt,symbols
x,k=symbols('x k')
assert 2*R(-5,2)+4*(2*R(-5,2)+7)-3==0
assert 16*R(1,4)**2==2*sqrt(R(1,4)) and factor(x**4+7*x**2-18)==(x**2-2)*(x**2+9)
assert integrate(4/x**3+R(4,15)*x,(x,R(1,2),2))==8
assert round(2.35-(3.28-2.35),2)==1.42
assert diff(3*x**2+24/x+2,x)==6*x-24/x**2
assert 3*(2*sqrt(3))**2*sqrt(3)/2==18*sqrt(3)
assert 16-4*2*(sqrt(2))**2==0
assert expand((2+3*x/4)**6).coeff(x,2)==135
mine=lambda n:1200-3*(n-20)**2
assert mine(1)==117 and mine(5)-mine(4)==93
assert expand((x-2)**2+(k+4)**2-28)==x*x+k*k-4*x+8*k-8
assert expand((x-4)**2*(2*x+3))==2*x**3-13*x*x+8*x+48
assert expand((4-5*x)*(3+2*x))==10*(1-x*x)-7*x+2
assert integrate(2*x**3-17*x*x+40*x,(x,0,4))==R(256,3)
assert 15700+2300==18000 and 15700/4==3925
assert all((i**3+2)%8 for i in range(8))
