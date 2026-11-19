"""Independent algebra/calculus/domain checks for Pure 1 practice chapter 14."""
import math
import sympy as s
x,t=s.symbols('x t',real=True)
R=s.Rational
n=0
def eq(a,b):
 global n
 assert s.simplify(a-b)==0,(a,b)
 n+=1
def near(a,b,tol=1e-8):
 global n
 assert abs(float(a)-b)<tol,(a,b)
 n+=1
for a,b in [(R(2,3)**3,R(8,27)),(R(4)**-2,R(1,16)),(R(1,5)**-2,25),(R(4,3)**-3,R(27,64))]:eq(a,b)
for k in range(-3,4):
 eq(R(2,3)**k*R(3,2)**k,1)
for f,c,v in [(2**(x+2),0,4),(2**x-2,1,0),(2*2**x,0,2),(-2**x,0,-1),(R(1,2)**(x+3)-4,-5,0),(-2*R(1,2)**x,0,-2)]:eq(f.subs(x,c),v)
eq(8*R(1,4),2);eq(8*R(1,4)**-2,128)
for f,d in [(s.exp(x/2),s.exp(x/2)/2),(s.exp(-5*x),-5*s.exp(-5*x)),(-4*s.exp(6*x),-24*s.exp(6*x)),(7*s.exp(x/3),R(7,3)*s.exp(x/3)),(3*s.exp(2*x)+s.exp(4*x),6*s.exp(2*x)+4*s.exp(4*x)),(6*s.exp(-2*x)+5/s.exp(x),-12*s.exp(-2*x)-5*s.exp(-x)),(s.exp(2*x)*(s.exp(-x)-4),s.exp(x)-8*s.exp(2*x)),((2-s.exp(5*x))/s.exp(3*x),-6*s.exp(-3*x)-2*s.exp(2*x)),(8*x*x-s.exp(-6*x),16*x+6*s.exp(-6*x)),(2*s.exp(-x)*(4*s.exp(5*x)-3),32*s.exp(4*x)+6*s.exp(-x)),(5*s.sqrt(x)+10/x**2-4*s.exp(-2*x),R(5,2)/s.sqrt(x)-20/x**3+8*s.exp(-2*x))]:eq(s.diff(f,x),d)
eq(s.exp(4*x).subs(x,R(1,2)),4*s.exp(2)*R(1,2)-s.exp(2))
for f,d in [(20000*s.exp(t/100),200*s.exp(t/100)),(32000*s.exp(-R(2,25)*t),-2560*s.exp(-R(2,25)*t)),(1300*s.exp(t/8),R(325,2)*s.exp(t/8)),(29000*s.exp(-R(3,25)*t),-3480*s.exp(-R(3,25)*t)),(18000*s.exp(t/50),360*s.exp(t/50)),(250*s.exp(-R(3,20)*t),-R(75,2)*s.exp(-R(3,20)*t)),(150000*s.exp(R(3,50)*t),9000*s.exp(R(3,50)*t))]:eq(s.diff(f,t),d)
for value,rounded,tol in [(200*math.exp(.1),221,.05),(162.5*math.exp(10),3579300,1),(29000*math.exp(-.72),14115.82,.005),(250*math.exp(-.9),101.6,.05),(360*math.exp(.5),594,.5)]:near(value,rounded,tol)
for base,power,result in [(10,3,1000),(2,3,8),(7,2,49),(6,-3,R(1,216)),(4,-4,R(1,256)),(9,1,9),(25,R(1,2),5),(27,R(1,3),3),(8,2,64),(2,-4,R(1,16)),(3,R(1,3),3**R(1,3)),(10,-2,R(1,100)),(9,0,1)]:eq(s.Integer(base)**power,result)
for a,b in [(3**4,81),(3*42-1,125),(9**3,729),(4**2,4*4),(2*R(33,2)-1,8**R(5,3)),(256**R(3,4),64),(125**(-R(4,3)),R(1,625)),(4*9,6**2),(12**2,36*4),((7-1)**2,4*9),(64*R(5,8)**2,25),((2*R(7,17)+5)/(4*R(7,17)-1),9)]:eq(a,b)
# Substitute the unrounded solutions into each original exponential equation.
checks=[(lambda v:6**v-31,math.log(31,6)),(lambda v:3**v-70,math.log(70,3)),(lambda v:5**(2*v)-640,math.log(640)/2/math.log(5)),(lambda v:5**(v+3)-.3,math.log(.3,5)-3),(lambda v:4**(2*v-5)-85,(5+math.log(85,4))/2),(lambda v:7**(1-4*v)-11,(1-math.log(11,7))/4),(lambda v:8**v/5**(v+3)-1,3*math.log(5)/math.log(8/5)),(lambda v:7**(3-v)-3**(2*v),3*math.log(7)/math.log(63)),(lambda v:6**(2*v)-4**(v+3),3*math.log(4)/math.log(9)),(lambda v:7**(2*v-5)-400,(5+math.log(400,7))/2),(lambda v:4**(v+2)/5**(v-1)-1,math.log(80)/math.log(5/4)),(lambda v:math.log(5-v,7)-.8,5-7**.8)]
for f,v in checks:near(f(v),0,1e-6)
for base,roots,A,B,C in [(5,[5,6],1,-11,30),(4,[4,15],1,-19,60),(5,[R(9,5),2],5,-19,18),(3,[R(5,3)],9,-3,-20),(6,[3],1,4,-21),(3,[5],1,-3,-10)]:
 for u in roots:eq(A*u*u+B*u+C,0)
for v in [s.log(8),2*s.log(6),s.log(81)-5,(1+s.log(23))/3,1-s.log(R(29,4)),s.log(R(21,2))/3]:assert v.is_real
for a,b in [(s.exp((1+s.log(23))-1),23),(3-5*((3-s.exp(-1))/5),s.exp(-1)),(5-2*((5-s.exp(R(2,5)))/2),s.exp(R(2,5))),(3*((5+s.exp(R(7,2)))/3)-5,s.exp(R(7,2)))]:eq(a,b)
for roots,A,B,C in [([1,4],1,-5,4),([R(7,2),2],2,-11,14),([4],1,-1,-12),([R(3,2),5],2,-13,15),([4,5],1,-9,20),([2,6],1,-8,12),([R(4,3),5],6,-38,40)]:
 for u in roots:eq(A*u*u+B*u+C,0)
for v in [s.Integer(3),R(10,3)]:eq((7*v-18)/(v-2)**2,3)
near(31*math.exp(-.05*(-20*math.log(18/31)))+7,25)
near(50+700*math.exp(-.4*2.5*math.log(14)),100)
near(.25*math.exp((4*math.log(48))/4),12)
k=math.log(2/3)/5;time=math.log(-1.5/(45*k))/k
near(45*k*math.exp(k*time),-1.5);near(time,10.96,.005)
near(700*math.exp(.035*(math.log(2)/.035)),1400)
near(4**5.2,1350,5);near(4**2.95,60,.5);near(2**9.3,630.3,.05)
print(f'{n} independent exact/numerical checks passed')
