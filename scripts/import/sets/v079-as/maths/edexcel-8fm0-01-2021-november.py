from sympy import Matrix, Rational as R, acos, diag, expand, factor, integrate, pi, sqrt, summation, symbols
x,n,r,k=symbols('x n r k')
P=Matrix([[0,-1],[1,0]])
assert diag(1,3)*P==Matrix([[0,-1],[3,0]]) and (diag(1,3)*P).det()==3
z=(x+2)/3
assert expand(9*(9*z**3-5*z**2+4*z+7))==3*x**3+13*x**2+28*x+91
s=summation((5*r-2)**2,(r,1,n))
assert expand(6*s-n*(50*n**2+15*n-11))==0 and s.subs(n,11)==94*11**2
M=Matrix([[2,1,4],[k,2,-2],[4,1,-2]])
N=Matrix([[k-7,6,-10],[2,-20,24],[-3,2,-1]])
assert M.subs(k,5)*N.subs(k,5)==-14*diag(1,1,1)
assert M.subs(k,5).inv()*Matrix([2,3,-1])==Matrix([R(-12,7),R(40,7),R(-1,14)])
# The horizontal boundary Im(z)=2 is one unit above the annulus centre.
segment=4*acos(R(1,2))-sqrt(3)
assert 3*pi-segment==5*pi/3+sqrt(3)
normal=Matrix([13,1,-18])
A=Matrix([10,5,-50])
assert normal.dot(A)==1035 and normal.dot(Matrix([5,25,5]))==normal.dot(Matrix([-15,15,-10]))==0
assert round(float(acos(18/normal.norm())*180/pi))==36
assert round(float(R(1035-65-12,18)),1)==53.2
assert expand((x-3)*(x+1)*((x-2)**2+1))==x**4-6*x**3+10*x**2+2*x-15
s=n*(n+1)**2*(n+2)/2
assert expand(s-s.subs(n,n-1)-n*(n+1)*(2*n+1))==0
assert expand(s.subs(n,2*n)-s.subs(n,n-1)-n*(n+1)*(3*n+1)*(5*n+4)/2)==0
# BC has a=4. Integrate horizontal disc areas below and above C.
assert sqrt(225*25-2025)/15==4
assert pi*(integrate(9+(4*x/15)**2,(x,0,15))+integrate(25*(16-x),(x,15,16)))==455*pi/2
