from sympy import *
from sympy.stats import Normal, Binomial, P as Pr, cdf
import math
# Q1
mid = [2.5, 6.5, 9.5, 11.5, 13]; f = [12, 6, 8, 3, 2]; n = sum(f); S = sum(a*b for a, b in zip(mid, f)); S2 = sum(a*a*b for a, b in zip(mid, f))
mean = S/n; sd = math.sqrt(S2/n - mean**2); print('Q1 fd 8/(1.5)... width 5*0.5 =', 2.5, 'height', 12/5 / (8/3) * 8, 'mean', round(mean, 3), 'sd', round(sd, 3))
print('Q1(e)', round(31*(1 - float(cdf(Normal('Z', 0, 1))(1))), 3))
# Q2 critical value r(9, 5% one-tail) = 0.5822
print('Q2 r = 0.609 > 0.5822 reject H0')
Z = Normal('Z', 0, 1); mu = 50.98 - 1.96*0.5; L = Normal('L', mu, 0.5)
p = float(Pr((L > 49) & (L < 50.75))); print('Q3 mu', round(mu, 3), 'P(use)', round(p, 4))
q = 1 - p; print('Q3(b)', round(sum(math.comb(10, k)*q**k*(1 - q)**(10 - k) for k in range(4)), 4))
print('Q3(c) p', round(1 - float(cdf(Z)((50.4 - 50.1)/(0.6/math.sqrt(15)))), 4))
pAB = 0.13; print('Q4(a)', round((1 - (0.35 + 0.45 - 0.13))/0.55, 4), 'P(A)P(B)', 0.35*0.45, 'B∩C', 0.45*0.2, 'P((BuC)\')', round(1 - (0.45 + 0.2 - 0.09), 4))
pt = sum(math.comb(24, k)*0.55**k*0.45**(24 - k) for k in range(15, 25)); print('Q5 P(tray>=15)', round(pt, 4), 'P(>=5 trays)', round(sum(math.comb(10, k)*pt**k*(1 - pt)**(10 - k) for k in range(5, 11)), 4))
mu5, s5 = 240*0.55, math.sqrt(240*0.55*0.45); print('Q5(d)', round(1 - float(cdf(Z)((149.5 - mu5)/s5)), 4))
t = symbols('t', nonnegative=True); v = Matrix([20 + integrate(5*t, (t, 0, t)), integrate(-15*sqrt(t), (t, 0, t))]); v4 = v.subs(t, 4); print('Q6 v(4)', list(v4), 'speed', sqrt(v4.dot(v4)))
mu_ = symbols('mu'); sa, ca = Rational(3, 5), Rational(4, 5); print('Q7 mu', solve(Eq(sa + mu_*ca, Rational(4, 5)), mu_), 'remain? need mu >= tan =', Rational(3, 4))
a = (Matrix([10.5, -0.9]) - Matrix([0, 0.6]))/15; r = Matrix([0, 0.6])*t + a*t**2/2; print('Q8 a', list(a), 'r', [nsimplify(x) for x in r], 'NE pos t', solve(Eq(r[0], r[1]), t), 'NE vel t', solve(Eq(a[0]*t, 0.6 + a[1]*t), t))
W, al = symbols('W alpha', positive=True); tn = Rational(5, 2); c, s_ = 2/sqrt(29), 5/sqrt(29)
S_ = symbols('S'); Sb = solve(Eq(S_*2*s_, W*c + 7*W*2*c), S_)[0]; print('Q9 S', simplify(Sb), 'P range', simplify(Sb - 8*W/4), 'to', simplify(Sb + 8*W/4))
U, T = symbols('U T', positive=True); sol = solve([Eq(U*Rational(4, 5)*T, 36), Eq(U*Rational(3, 5)*T - 5*T**2, -18)], [U, T], dict=True); print('Q10', sol)
Uv = sol[0][U]; vy2 = (Uv*Rational(3, 5))**2 + 2*10*(18 - 10.8 - 0)*1  # drop of 7.2 m below O
print('Q10(b) speed', N(sqrt((Uv*Rational(4, 5))**2 + (Uv*Rational(3, 5))**2 + 2*10*7.2), 3))
