from sympy import I, Matrix, Rational as R, arg, expand, eye, integrate, pi, simplify, sqrt, symbols
z,n,y=symbols('z n y')
assert arg(sqrt(3)-3*I)==-pi/3
assert expand((z+5)*(4*z**2-32*z+65))==4*z**3-12*z**2-95*z+325
M=Matrix([[2,3],[-1,-1]])
assert M+M.inv()==eye(2)
assert 6*3/2==9 and R(9,2)/9==R(1,2)
assert abs(R(1,2)+sqrt(3)*I/2-1)==1
assert simplify((n+1)**2*(n+2)**2/4-n**2*(n+1)**2/4-(n+1)**3)==0
volume=pi*integrate((12+y)**2*(144-y**2)/350,(y,-12,12))
assert 3500<float(volume)<3700
assert 10*11*12/6==22*10
normal=Matrix([1,-2,8]);W=Matrix([6,-2,-4])
assert normal.dot(W+normal/3)==1
n1=Matrix([1,1,-1]);n2=Matrix([2,3,5])
assert n1.dot(n2)==0 and 2*n2-3*n1==Matrix([1,3,13])
assert expand((z-1)*(z-7)*(z-13))==z**3-21*z**2+111*z-91
