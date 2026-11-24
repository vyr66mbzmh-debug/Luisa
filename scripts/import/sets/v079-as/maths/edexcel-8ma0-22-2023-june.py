from sympy import Rational as R, diff, integrate, solve, symbols
t,x=symbols('t x',real=True)
distance=4*(R(55,2)-R(5,2))
assert R(4,5)==R(8,10) and distance==100
speed=min(solve(x*(R(55,2)-x/2)-distance,x))
assert round(float(speed),2)==3.92
g=R(98,10)
assert -(4*g*10-g*10**2/2)==98 and 2*R(245,10)/g==5
v=15-t**2-2*t
assert v.subs(t,3)==0 and abs(diff(v,t).subs(t,3))==8
assert integrate(v,(t,0,3))-integrate(v,(t,3,4))==R(94,3)
a,res=symbols('a R')
motion=solve([7400-2400-2*res-1200*a,2400-res-400*a],(a,res))
assert motion=={a:R(1,2),res:2200}
