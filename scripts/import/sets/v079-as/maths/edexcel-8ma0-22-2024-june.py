from sympy import Rational as R, diff, integrate, simplify, solve, sqrt, symbols
assert 5*(R(5,2)+15+5)==R(225,2)
t,c=symbols('t c')
v=2*t-7*sqrt(t)+6
assert diff(v,t).subs(t,4)==R(1,4) and simplify(integrate(v,(t,1,2))-(41-28*sqrt(2))/3)==0
assert solve((2+c)**2+2**2-20,c)==[-6,2]
a=R(6,10)
resistance=1740-400-(800+600)*a
assert resistance==500 and 600*a+resistance==860
assert resistance/600==R(5,6) and R(25,2)**2/(2*R(5,6))==R(375,4)
