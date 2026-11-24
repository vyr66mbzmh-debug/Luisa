from sympy import Rational as R,diff,integrate,solve,symbols
g,u=R(98,10),R(147,10)
assert 2*u/g==3 and u*u/(2*g)+g*(4-u/g)**2/2==R(833,20)
t=symbols('t')
v=10*t-t*t-24
assert diff(v,t)==10-2*t and solve(v,t)==[4,6]
assert -integrate(v,(t,0,4))+integrate(v,(t,4,6))==R(116,3)
# Once Q reaches the ground, P has risen h and then coasts a further 3h/7.
assert (2+1)+R(5-2,5+2)==R(24,7)
