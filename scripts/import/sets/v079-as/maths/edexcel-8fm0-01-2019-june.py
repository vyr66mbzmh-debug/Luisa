from sympy import I, Matrix, Rational as R, expand, integrate, simplify, sqrt, symbols

n,x = symbols('n x', positive=True)
matrix = Matrix([[4,-5],[2,-7]])
assert matrix.det() == -18 and R(63,18) == R(7,2)
assert matrix*Matrix([1,2]) == -6*Matrix([1,2])
assert expand(2*(x-3)**3+6*(x-3)**2-3*(x-3)+12) == 2*x**3-12*x**2+15*x+21
assert simplify(n/(2*n+1)+1/((2*n+1)*(2*n+3))-(n+1)/(2*n+3)) == 0
assert R(1,1*3) == R(1,3)
normal=Matrix([1,-2,1])
assert normal.dot(Matrix([1,-1,-3])) == 0 and normal.dot(Matrix([-2,5,4])) != -7
# A real polynomial needs both conjugates: five distinct roots would be necessary.
zs=[-2,-1+2*I,1+I]
assert len(set(zs+[-1-2*I,1-I])) == 5
assert simplify((zs[1]-zs[0])/(zs[2]-zs[0])) == R(1,2)*(1+I)
assert (2-R(1,3))/(1+2*R(1,3)) == 1
# The squared-distance inequality simplifies to 6x+2y <= -2.
y=symbols('y',real=True)
assert expand((x+2)**2+y**2-(x-1)**2-(y-1)**2) == 6*x+2*y+2
assert simplify((10+7+3*n)/2-(3*n+17)/2) == 0
assert round(float(sqrt(9*R(85**2-1,12))),1) == 73.6
assert expand((x-4)*((x-2)**2+2)) == x**3-8*x**2+22*x-24
P,Q,M=Matrix([-300,400,-150]),Matrix([300,300,-50]),Matrix([100,200,100])
assert M.dot(Matrix([2,3,-5])) == 300
v=Q-P
foot=P+v*((M-P).dot(v)/v.dot(v))
assert foot == Matrix([150,325,-75]) and (M-foot).norm() == 25*sqrt(78)
assert (M-foot).norm() < min(P.norm(),Q.norm())
area=integrate((2*x**R(1,3)+x**-R(2,3))**2,(x,R(1,8),8))
assert 461/area == R(40,9)
# Solve the second population equation together with J0+A0=64000.
juveniles = (R(82,100)*64000-43008)/(R(82,100)-R(8,100))
adults = 64000-juveniles
rate=(15360-R(15,100)*adults)/juveniles
assert juveniles == 12800 and rate == R(3,5) and 15360-juveniles == 2560
