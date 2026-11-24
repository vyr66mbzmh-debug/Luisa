from sympy import Rational, diff, integrate, solve, sqrt, symbols

t = symbols('t', real=True)
opening = 10 * 3
landing = opening - 12 * 2
distance = Rational(3 * opening, 2) + (opening + landing)
assert (opening, landing) == (30, 6)
assert round(5 + (550 - distance) / landing) == 83
a = Rational(6, 10) * Rational(98, 10) / Rational(14, 10)
assert a == Rational(42, 10)
fall = Rational(4, 10)
hit = sqrt(2 * fall / a) + (Rational(15, 10) - fall) / sqrt(2 * a * fall)
assert round(float(hit), 2) == 1.04
v = 12 + 4*t - t**2
assert solve(v, t) == [-2, 6] and abs(diff(v,t).subs(t,6)) == 8
assert integrate(v, (t,0,3)) == 45
