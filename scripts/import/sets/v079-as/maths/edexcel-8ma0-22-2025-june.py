from sympy import Matrix, Rational as R, diff, solve, sqrt, symbols
assert 400/5+(5+15)/2==90
resultant=Matrix([3,-5])+Matrix([-6,9])
assert resultant==Matrix([-3,4]) and resultant.norm()/R(1,4)==20
a=R(98,10)*3/5
speed=sqrt(2*a*R(4,10))
assert a==R(147,25) and round(float(speed),2)==2.17
assert round(float(R(8,10)/speed),3)==0.369
t=symbols('t')
s=2*t**3-12*t**2+18*t
v=diff(s,t)
assert solve(v,t)==[1,3]
assert sum(abs(s.subs(t,b)-s.subs(t,a)) for a,b in zip([0,1,3],[1,3,4]))==24
assert solve(diff(v,t),t)==[2] and abs(v.subs(t,2))==6
