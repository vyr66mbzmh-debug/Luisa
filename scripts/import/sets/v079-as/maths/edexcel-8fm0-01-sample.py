from sympy import Matrix, Rational as R, asin, expand, factor, integrate, pi, solve, sqrt, summation, symbols
x,n,r=symbols('x n r')
# Product gives third root 3; the other two have sum 4 and product 5.
assert expand((x-3)*((x-2)**2+1))==x**3-7*x**2+17*x-15
normal=Matrix([3,-1,2]);pt=Matrix([7,3,-2]);v=Matrix([-1,-5,3])
assert normal.dot(Matrix([5,-3,-4]))==10
assert round(float(asin(abs(normal.dot(v))/(normal.norm()*v.norm()))*180/pi),1)==21.2
assert normal.dot(pt-v/2)==10
assert Matrix([[1,1,1],[-1,1,0],[15,35,-25]]).inv()*Matrix([5000,400,79000])==Matrix([1800,2200,1000])
assert expand((x+1)**3+3*(x+1)**2-8*(x+1)+6)==x**3+6*x**2+x+2
M=Matrix([[1,-sqrt(3)],[sqrt(3),1]])
assert M.det()==4 and 5*M.det()==20 and M[:,0].norm()==2
s=n*(n+1)*(2*n+1)/6
assert expand(s-s.subs(n,n-1)-n**2)==0
series=summation(r*(r+6)*(r-6),(r,1,n))
assert factor(series)==n*(n-8)*(n+1)*(n+9)/4
assert 25 in solve(series-17*s,n)
assert (R(116,100)-1)/R(2,10)**2==4
vol=2*pi*integrate(x*(1+4*x*x),(x,0,R(1,5)))
assert round(float(vol),3)==.136
assert round(float(pi/2+asin(R(3,4))),2)==2.42
A=Matrix([-3,1,-7]);B=Matrix([9,4,11]);v=B-A
t=-A.dot(v)/v.dot(v)
assert 0<t<1 and (A+t*v).norm()>2
