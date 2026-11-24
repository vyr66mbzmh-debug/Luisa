"""Independent checks against the printed data in June 2023 AS Core Pure."""
from sympy import I, Matrix, Rational, discriminant, expand, integrate, pi, simplify, solve, sqrt, symbols

x, y, z, k, t = symbols('x y z k t')
assert solve([x-3*z-k, 9-3*y, y-3*z, z-3*y-k], [x,y,z,k]) == {x:-5,y:3,z:1,k:-8}
assert expand((x+7)*((x+3)**2+16)) == x**3+13*x**2+67*x+175
rotation = Matrix([[1,0,0],[0,sqrt(3)/2,-Rational(1,2)],[0,Rational(1,2),sqrt(3)/2]])
second = Matrix([[1,3,0],[sqrt(3),0,5*sqrt(3)],[1,2,0]])
assert (second*rotation)[2,:] == Matrix([[1,sqrt(3),-1]])
assert simplify((2+3*I)/(5+I)) == (1+I)/2
assert 3**10==59049 and expand((1+I)**4)==-4
assert integrate(pi*(2-y),(y,0,2))*900 == 1800*pi
normal=Matrix([1,2,-3])
assert normal.dot(Matrix([3,0,1]))==0
point=Matrix([2,3,2])+t*normal
delta=point-Matrix([3,1,1])
assert solve(delta.dot(delta)-20,t)==[-1,1]
assert point.subs(t,-1)==Matrix([1,1,5])
assert solve([y-sqrt(3)*(x-2),y-(x+1)/sqrt(3)],[x,y])=={x:Rational(7,2),y:3*sqrt(3)/2}
odd_sum=lambda n:n*(4*n**2-1)//3
assert odd_sum(500)-odd_sum(50)==sum(r*r for r in range(101,1000,2))
det=Matrix([[k,-2,7],[-3,-5,2],[k,k,4]]).det()
assert discriminant(det,k)<0
assert solve((x-10)**2+9*(x-4)**2-58,x)==[3,Rational(31,5)]
assert expand((x+1)**4+45*(x+1)**2-2430)==x**4+4*x**3+51*x**2+94*x-2384
assert expand(4*(x-Rational(3,2))*(x-3)*(x+Rational(9,2)))==4*x**3-63*x+81
