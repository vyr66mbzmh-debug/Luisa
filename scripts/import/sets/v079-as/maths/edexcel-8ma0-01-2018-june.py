from sympy import Rational as R,diff,discriminant,expand,factor,integrate,simplify,sqrt,symbols
x,k=symbols('x k')
assert diff(x**4/6-4*x**R(3,2)+x,x)==2*x**3/3-6*sqrt(x)+1
assert expand((x-4)**2+1)==x*x-8*x+17 and expand((x+3)**2-x*x)==6*x+9
assert sqrt((-5-4)**2+(-2+5)**2)==3*sqrt(10)
assert R(3,4)*R(9,-6)==-R(9,8)
assert 2*2-1==3
profit=lambda p:100-6.25*(p-9)**2
assert profit(7.21)<80<profit(7.22) and profit(15)<0
assert 10**2+5**2-2*10*5*(-.8)==205
cost=1500/x+2*x/11+60
assert diff(cost,x).subs(x,sqrt(8250))==0 and diff(cost,x,2)==3000/x**3
assert expand((x+2)*(2*x-5)**2)==4*x**3-12*x*x-15*x+50
assert diff(x**3,x)==3*x*x
assert expand((2-x/16)**9).coeff(x)==-144
assert factor(6*x**2-x-2)==(2*x+1)*(3*x-2)
assert round(10**(4.8+.05*30),-5)==2000000
assert expand(discriminant(x*x+(k*x)**2-6*x+10*k*x+9,x))==64*k*k-120*k
assert integrate(32/x**2+3*x-8,(x,2,4))+12*6//2==46
