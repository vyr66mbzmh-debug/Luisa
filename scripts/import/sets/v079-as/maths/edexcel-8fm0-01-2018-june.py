from sympy import Matrix, Rational as R, asin, cos, expand, factor, integrate, pi, simplify, sqrt, summation, symbols
n,r,x=symbols('n r x',positive=True)
M=Matrix([[2,1,-3],[4,-2,1],[3,5,-2]])
assert M.inv()*Matrix([-4,9,5])==Matrix([2,1,3])
z=(x-1)/2
assert expand(8*(z**3-3*z**2+z+5))==x**3-9*x**2+19*x+29
t=sqrt(R(7,2))
assert simplify((t+1)**2+(t-1)**2)==9 and simplify((2+t)**2+t**2)==11+2*sqrt(14)
v=Matrix([2,3,0]);normal=Matrix([3,-5,-18]);ac=Matrix([0,-1,3])
assert round(float(180/pi*asin(abs(v.dot(normal))/(v.norm()*normal.norm()))),2)==7.58
assert round(float(ac.cross(v).norm()/v.norm()),2)==3.05
A=Matrix([[-1,-sqrt(3)],[sqrt(3),-1]])/2
C=Matrix([[0,-1],[-1,0]])*A
assert (C*Matrix([1,2+sqrt(3)])-Matrix([1,2+sqrt(3)])).applyfunc(simplify)==Matrix([0,0])
s=n*(6*n**2-3*n-1)/2
assert simplify(summation((3*r-2)**2,(r,1,n))-s)==0
assert expand(s-s.subs(n,4)+103*summation(r*cos(r*pi/2),(r,1,28))-3*n**3+(n-29)*(3*n+88)/2)==0
assert expand((x-3)*((x+2)**2+49))==x**3+x**2+41*x-159
T=Matrix([[5,-8],[2,-3]])
assert (T-Matrix.eye(2))**2==Matrix.zeros(2)
f=4**(n+1)+5**(2*n-1)
assert f.subs(n,1)==21 and simplify(f.subs(n,n+1)-4*f-21*5**(2*n-1))==0
# The shoulder joins (1,18) to (4,14): x^2=(274-15y)/4.
y=symbols('y')
assert (224+integrate((274-15*y)/4,(y,14,18))+10)*pi==268*pi
