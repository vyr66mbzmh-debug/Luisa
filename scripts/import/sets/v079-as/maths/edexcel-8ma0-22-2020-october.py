from sympy import Rational, diff, integrate, solve, sqrt, symbols

t = symbols('t', real=True)
g = 10
u = sqrt(19**2 - 2*g*Rational(168,10))
assert u == 5
assert (u+19)/g == Rational(12,5)
assert solve(u*t-g*t**2/2+Rational(12,10),t) == [-Rational(1,5),Rational(6,5)]
# Two equal downward tensions act on the pulley. Work in units of mg.
a_over_g = Rational(4-3,4+3)
tension = 4*(1-a_over_g)
assert tension == 3*(1+a_over_g) and 2*tension == Rational(48,7)
v = (7-2*t)*(t+2)
assert solve(diff(v,t),t) == [Rational(3,4)]
stop = max(solve(v,t))
assert stop == Rational(7,2) and integrate(v,(t,0,stop)) == Rational(931,24)
