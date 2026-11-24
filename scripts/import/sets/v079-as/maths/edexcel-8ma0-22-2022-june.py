from sympy import Rational as R, diff, solve, sqrt, symbols

u=sqrt(10**2-2*10*R(18,10))
assert u==8 and (u+10)/10==R(9,5)
# Compare the rectangular speed envelope with the two triangular shortfalls.
t=2*(700*25-15000)/(25*5)
assert t==40 and 25/t==0.625 and 25*(700-572)/(4*t)==20
x=symbols('x')
s=x**3/3-5*x**2/2+6*x
times=solve(diff(s,x),x)
assert times==[2,3] and [diff(s,x,2).subs(x,t) for t in times]==[-1,1]
assert sum(abs(s.subs(x,b)-s.subs(x,a)) for a,b in zip([0,2,3],[2,3,4]))==R(17,3)
assert (40+10)*(R(98,10)+R(2,10))==500 and 10*(R(98,10)+R(2,10))==100
