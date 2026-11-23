from sympy import *
n, r, k, x, t, th, a, b, z, lam, A_, B_ = symbols('n r k x t theta a b z lambda A B')
S = simplify(summation(1/((r + 1)*(r + 3)), (r, 1, n))); print('Q1', factor(S), '-> a=5, b=13:', simplify(S - n*(5*n + 13)/(12*(n + 2)*(n + 3))))
f = lambda m: 2**(3*m + 1) + 3*5**(2*m + 1); print('Q2', [f(m) % 17 for m in range(1, 8)], 'f(k+1) - 8f(k) =', simplify(expand(f(k + 1) - 8*f(k))), '= 17*3*5^(2k+1)')
q = expand((z**2 - 6*z + 13)*(z**2 + 2*z + 5)); print('Q3', q, 'roots', solve(q, z))
rr = 4 + cos(2*th); tA = solve(Eq(rr, Rational(9, 2)), th); print('Q4 thetaA', tA)
sector = integrate(rr**2/2, (th, 0, pi/6)); tri = Rational(1, 2)*(Rational(9, 2)*cos(pi/6))*(Rational(9, 2)*sin(pi/6)); print('Q4 area R', nsimplify(simplify(sector - tri)))
xs = Function('x'); sol = dsolve(Eq(xs(t).diff(t), 50 - 4*xs(t)/(200 + t)), xs(t), ics={xs(0): 0}); print('Q5', simplify(sol.rhs), 'x(8)', N(sol.rhs.subs(t, 8), 5))
F = integrate((x + 2)/(x**2 + 9), x); print('Q6', simplify(F), 'mean', nsimplify(simplify(integrate((x + 2)/(x**2 + 9), (x, 0, 3))/3)))
y = symbols('y'); print('Q7 check x^2 + y^4 + 2y^3 at theta=0.7:', N(((cos(th) + sin(2*th)/2)**2 + (-(1 + sin(th)))**4 + 2*(-(1 + sin(th)))**3).subs(th, 0.7)), 'V', integrate(-pi*(y**4 + 2*y**3), (y, -2, 0)), N(integrate(-pi*(y**4 + 2*y**3), (y, -2, 0)), 4))
P0, d = Matrix([2, 4, -6]), Matrix([4, -2, 1]); nrm = Matrix([1, -2, 1]); L = solve((P0 + lam*d).dot(nrm) - 6, lam)[0]; X = P0 + L*d
tt = solve((P0 + t*nrm).dot(nrm) - 6, t)[0]; Rf = P0 + 2*tt*nrm; print('Q8 intersection', list(X), 'reflection of (2,4,-6)', list(Rf), 'direction', list(X - Rf))
xx = Function('x'); ode = Eq(3*xx(t).diff(t, 2) + 4*xx(t).diff(t) + xx(t), 200*cos(t)); s9 = dsolve(ode, xx(t), ics={xx(0): 0, xx(t).diff(t).subs(t, 0): 0}); print('Q9', simplify(s9.rhs), 'x(9)', N(s9.rhs.subs(t, 9), 4))
print('Q9 PI check', simplify(3*diff(40*sin(t) - 20*cos(t), t, 2) + 4*diff(40*sin(t) - 20*cos(t), t) + 40*sin(t) - 20*cos(t)))
