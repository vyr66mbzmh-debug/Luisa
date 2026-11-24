from sympy import Matrix, Rational as R, asin, diag, eye, factor, integrate, pi, simplify, sqrt, summation, symbols
n,r,x=symbols('n r x')
A=Matrix([[4,-1],[7,2],[-5,8]])
B=Matrix([[2,3,2],[-1,6,5]])
C=Matrix([[-5,2,1],[4,3,8],[-6,11,2]])
assert A*B-3*C==24*eye(3) and (B*A).shape==(2,2)
assert C.inv()*Matrix([-14,3,7])==Matrix([R(7,2),3,-R(5,2)])
# Unit ray direction is (1/2,sqrt(3)/2); the perpendicular foot is forward of its endpoint.
delta=Matrix([4*sqrt(3),6])
direction=Matrix([R(1,2),sqrt(3)/2])
assert delta.dot(direction)>0 and abs(delta[0]*direction[1]-delta[1]*direction[0])==3
P=Matrix([8,3,2]);Q=Matrix([8,-3,2])
rot=Matrix([[-R(1,2),0,sqrt(3)/2],[0,1,0],[-sqrt(3)/2,0,-R(1,2)]])
PR=rot*P-P
assert PR.dot(Q-P)==0 and simplify(PR.dot(PR))==204
assert simplify(PR.cross(Q-P).norm()/2)==6*sqrt(51)
poly=3*x**4+5*x**3-7*x+6
assert poly.subs(x,3)/3==121 and R(-5,3)**2==R(25,9) and 2*R(7,6)==R(7,3)
s=summation(3*r**2-17*r-25,(r,1,n))
assert factor(s)==n*(n**2-7*n-33)
assert factor(s-s.subs(n,4)-45*(n-2)**2)==n*(n-49)*(n-3)
# n >= 5 is required for the printed bounds, yielding n=49.
height=R(84,100)+R(8,10)*x-x*x
assert height.subs(x,R(14,10))==0 and height.subs(x,R(1025,1500))>R(9,10)
vertical=-2
horizontal=sqrt((9-R(46,10)*R(14,10))**2+15**2)
assert round(float(180/pi*asin(2/sqrt(horizontal**2+vertical**2))),1)==7.5
T=Matrix([[-5,9],[-4,7]])
assert (T-eye(2))**2==Matrix.zeros(2)
radius=4+x*(x-8)*(x+8)/100
assert simplify(radius.diff(x).subs(x,-8/sqrt(3)))==0
assert integrate(radius**2,(x,-8,8))==R(18897152,65625)
