from sympy import Matrix, Rational as R, acos, diag, eye, factor, integrate, pi, simplify, sqrt, summation, symbols
k,n,r,y=symbols('k n r y',positive=True)
assert R(3,2)**2-5==-R(11,4) and 3*R(5,-7)==-R(15,7)
assert R(2*5**3-3*5**2+5*5+7,2)==R(207,2)
a=Matrix([-2,4,3]);b=Matrix([2+sqrt(3),2*sqrt(3)-1,3])
assert round(float(acos(a.dot(b)/29)*180/pi),1)==66.9
s=summation(r**2*(r+1),(r,1,n))
assert factor(s)==n*(n+1)*(n+2)*(3*n+1)/12
segment=s.subs(n,3*k)-s.subs(n,k)
assert factor(25*segment-192*k**3*(3*k+1))==-k*(k-5)*(3*k+1)*(76*k+5)/3
A=Matrix([[-1,-2,-7],[3,k,2],[1,1,4]])
B=Matrix([[4*k-2,1,7*k-4],[-10,3,-19],[3-k,-1,6-k]])
assert (A*B).applyfunc(simplify)==(3*k+1)*eye(3)
assert sqrt(5**2+12**2)+10==23 and round(float(100*acos(R(4,5))-48),1)==16.4
direction=Matrix([5,12,1]);base=Matrix([3,4,-2])
assert base+2*direction==Matrix([13,28,0])
assert simplify(n/(n+1)+1/((n+1)*(n+2))-(n+1)/(n+2))==0
assert all((3**(2*i+4)-2**(2*i))%5==0 for i in range(1,30))
radius=-y**2/10+sqrt(y)
assert radius.subs(y,4)==R(2,5) and 8<float(pi*(integrate(radius**2,(y,0,4))+R(2,25)))<10
