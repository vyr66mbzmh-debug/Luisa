from sympy import I, Matrix, Rational as R, diag, expand, factor, integrate, pi, simplify, sqrt, symbols

x,k,n,r = symbols('x k n r',positive=True)
A = Matrix([[k,3,-1],[3,-1,1],[-16,-k,-k]])
assert expand(A.det()-2*(k-2)*(k+8)) == 0
B=A.subs(k,2)
assert B.rank()==B.row_join(Matrix([3,-2,2])).rank()==2
assert simplify(39*(1+I)/(2+3*I))==15-3*I
assert integrate(pi*(r*r-x*x),(x,-r,r)) == 4*pi*r**3/3
normal=Matrix([1,2,-10])
assert normal.dot(Matrix([8,1,1])) == normal.dot(Matrix([4,3,1])) == 0
assert normal.dot(Matrix([-2,-3,-1])) == 2
distance=abs(normal.dot(Matrix([2,5,R(11,4)]))-2)/normal.norm()
assert round(float(distance),2)==1.71
volume=n*(n+1)*(n+2)*(n+3)/4
assert simplify(volume-volume.subs(n,n-1)-n*(n+1)*(n+2))==0
assert factor(4*(n**4+6*n**3-11710-volume))==(n-10)*(3*n**3+48*n**2+469*n+4684)
for a in (1,3):
    B=Matrix([[2,a],[a-4,-2]])
    assert B**2==diag(1,1)
assert Matrix([[2,1],[-3,-2]])*Matrix([1,-1])==Matrix([1,-1])
P=Matrix([[1,2],[-1,3]])
assert P.det()*3==15 and diag(3,-2)*P==Matrix([[3,6],[2,-6]])
assert expand(((x-2)**2+9)*((x+4)**2+9)) == x**4+4*x**3+6*x**2+4*x+325
f=2**(n+2)+3**(2*n+1)
assert f.subs(n,1)%7==0 and simplify(f.subs(n,n+1)-2*f-7*3**(2*n+1))==0
assert expand((x**3*(3/x**3+1/x**2-4/x+1)))==x**3-4*x**2+x+3
# A ray from (2,0) in direction (-1,1) passes the centre (3,5).
# Two intersections require 2r strictly between its perpendicular and endpoint distances.
assert abs(1+5)/sqrt(2)==3*sqrt(2) and Matrix([1,5]).norm()==sqrt(26)
