"""Independent exact inequalities and geometry checks for practice Pure1 chapter3.

Run with SymPy in the private authoring environment. This supplements visual,
wording and individual subpart review rather than replacing those checks.
"""
import sympy as s
x,k,p=s.symbols('x k p',real=True);R=s.Rational;I=s.Interval;U=s.Union;oo=s.oo
checks=[]
def eq(label,a,b):
 assert s.simplify(a-b)==0,(label,a,b)
 checks.append(label)
def inequality(label,rel,expected):
 actual=s.solve_univariate_inequality(rel,x,relational=False)
 assert actual==expected,(label,actual,expected)
 checks.append(label)
cases=[
('3.4/1a',x+4>=12,I(8,oo)),('3.4/1b',7-5*x<62,I.open(-11,oo)),('3.4/1c',3*(3-2*x)<=2*(3+2*x),I(R(3,10),oo)),
('3.4/2b',x/3-2*x/9<3,I.open(-oo,27)),('3.4/2c',3*x*(3+x)+x*x>=1+x*(6+4*x),I(R(1,3),oo)),
('3.4/3a1',2*(1+x)<4-x,I.open(-oo,R(2,3))),('3.4/3a2',x-3<4*x+6,I.open(-3,oo)),('3.4/3b1',x/4+3<=6,I(-oo,12)),('3.4/3b2',2*(3*x-5)>=20,I(5,oo)),('3.4/3c1',R('.5')*(4*x+3)<R('2.5'),I.open(-oo,R(1,2))),('3.4/3c2',(x-3)/5>7,I.open(38,oo)),
('3.4/4a',2*x-6>3-x,I.open(3,oo)),('3.4/4b',4*x-5<3+2*x,I.open(-oo,4)),('3.4/5a',20-2*x>15-7*x,I.open(-1,oo)),('3.4/5b',x-5<=3-9*x,I(-oo,R(4,5))),('3.4/6a',3*(3*x+4)>=2-x,I(-1,oo)),('3.4/6b',7*(x-3)<3*(x-3),I.open(-oo,3)),('3.4/7',2*x+2*(x+30)<400,I.open(-oo,85)),('3.4/8a1',3*(2+x)>=2-x,I(-1,oo)),('3.4/8a2',x+7>5*x-1,I.open(-oo,2)),('3.4/8b1',R('.25')*(8*x+4)<R('5.5'),I.open(-oo,R(9,4))),('3.4/8b2',(x-2)/9>11,I.open(101,oo)),
('3.5/1a',x*x<25,I.open(-5,5)),('3.5/1b',x*(2*x+1)<3,I.open(-R(3,2),1)),('3.5/1c',1-3*x*x-2*x<0,U(I.open(-oo,-1),I.open(R(1,3),oo))),('3.5/1d',2*x*x>=5*x,U(I(-oo,0),I(R(5,2),oo))),
('3.5/2a1',x*x-5*x-14<0,I.open(-2,7)),('3.5/2a2',5*x+2>12,I.open(2,oo)),('3.5/2b1',2*x*x-3*x-5>0,U(I.open(-oo,-1),I.open(R(5,2),oo))),('3.5/2b2',x*x+3*x-4<0,I.open(-4,1)),('3.5/2c1',3*x*x+12*x-15<0,I.open(-5,1)),('3.5/2c2',x*x+5*x+6>0,U(I.open(-oo,-3),I.open(-2,oo))),
('3.5/3a',36>1/x**2,U(I.open(-oo,-R(1,6)),I.open(R(1,6),oo))),('3.5/3b',3<5/x,I.open(0,R(5,3))),('3.5/3c',16+6/x>=2/x,U(I(-oo,-R(1,4)),I.open(0,oo))),
('3.5/5a',2*x-2>7-x,I.open(3,oo)),('3.5/5b',x*x-6*x<=40,I(-4,10)),('3.5/6',x*x+4*x-12>0,U(I.open(-oo,-6),I.open(2,oo))),('3.5/7',21*x*x+9*x<702,I.open(-6,R(39,7))),('3.5/8',9*x*x-8*x<0,I.open(0,R(8,9))),('3.5/9',9*x*x-20*x+8<0,I.open((10-2*s.sqrt(7))/9,(10+2*s.sqrt(7))/9)),('3.5/10',3/(x-1)<2,U(I.open(-oo,1),I.open(R(5,2),oo))),
('3.6/1a',8-3*x<7*x-2,I.open(1,oo)),('3.6/1b',2*x-3<5*x+11,I.open(-R(14,3),oo)),('3.6/1c',6-2*x<9-5*x,I.open(-oo,1)),('3.6/2a',x*x+6<=-2*x+9,I(-3,1)),('3.6/2b',4-x*x<=3*x+4,U(I(-oo,-3),I(0,oo))),('3.6/2c',x*x+x-12<=-x-9,I(-3,1)),('3.6/3a',2*x*x+2*x>5*x+2,U(I.open(-oo,-R(1,2)),I.open(2,oo))),('3.6/3b',-x*x+5*x+6>3*x+6,I.open(0,2)),('3.6/3c',x*x+3*x+2>2-x,U(I.open(-oo,-4),I.open(0,oo))),('3.6/4',3*x-7>3-x,I.open(R(5,2),oo)),('3.6/5',8*x-12-x*x>2*x-7,I.open(1,5)),('3.6/6',R(7,2)*x-R(31,2)<x*x-3*x-10,U(I.open(-oo,1),I.open(R(11,2),oo))),
('pb/Bronze',x+6<x*x+5*x+6,U(I.open(-oo,-4),I.open(0,oo))),('pb/Silver',-x-R('1.75')>x*x+3*x-18,I.open(-R(13,2),R(5,2))),('pb/Gold',3+2*x-x*x<3*x*x+2*x-1,U(I.open(-oo,-1),I.open(1,oo))),('exam32a',3*x-7>3-7*x,I.open(1,oo)),('exam32b',x*x-4*x<=21,I(-3,7)),('exam55',x*x+4*x-12<0,I.open(-6,2)),('exam71b',(x+2)**2>x*x,I.open(-1,oo))]
for row in cases:inequality(*row)
# Check exact linear systems against original equations, not a rounded answer.
for f,g,a,b in [(6*x+s.Symbol('y')-9,4*x-s.Symbol('y')-11,2,-3),(2*x+3*s.Symbol('y')-8,3*x+2*s.Symbol('y')-7,1,2),(4*x-3*s.Symbol('y')-2,5*x-7*s.Symbol('y')-9,-1,-2),(5*x-2*s.Symbol('y')-3,x+4*s.Symbol('y')-5,1,1),(2*x+5*s.Symbol('y')-37,s.Symbol('y')-11+2*x,R(9,4),R(13,2)),(4*x+3*s.Symbol('y')-5,2*x-6*s.Symbol('y')+5,R(1,2),1),(3*(x-s.Symbol('y'))+6,s.Symbol('y')+x-8,3,5),(5*(x-1)+2*s.Symbol('y'),3*x-29-4*s.Symbol('y'),3,-5),((4*x-s.Symbol('y'))/2-11,(5-3*x)/5-s.Symbol('y'),5,-2),(x+s.Symbol('y')-2,2*s.Symbol('y')-18*x+6,R(1,2),R(3,2)),(3*x-s.Symbol('y')+5,s.Symbol('y')/2+2*x-4,R(3,7),R(44,7))]:
 for z in [f,g]:eq('linear system original',z.subs({x:a,s.Symbol('y'):b}),0)
# Tangency/repeated-root parameter quadratics and exact intersections.
m=s.symbols('m')
eq('3.2/6 discriminant',(2+8*m)**2-32*(1+m*m),4*(8*m*m+8*m-7))
for v in [(-2-3*s.sqrt(2))/4,(-2+3*s.sqrt(2))/4]:eq('3.2/6 slopes',8*v*v+8*v-7,0)
eq('3.2/7 k5 discriminant',16*5**2-80*5,0)
eq('3.5/7 park area',3*x*(5*x+2)+3*x*(2*x+1),21*x*x+9*x)
eq('3.5/9 discriminant',(3*p+2)**2-4*(8*p-1),9*p*p-20*p+8)
eq('3.7/1 area',R(1,2)*4*8,16)
eq('3.7/4 area',R(1,2)*R(7,2)*R(3,2),R(21,8))
eq('3.7/5 area',R(1,2)*R(5,2)*R(17,5),R(17,4))
eq('3.7/7 intersection',2*s.sqrt(R(25,4))-3,10-R('1.28')*R(25,4))
for v in [5-2*s.sqrt(3),5+2*s.sqrt(3)]:eq('exam10 intersections',v*v-8*v+18,2*v+5)
eq('exam13 discriminant',(k-4)**2-4*(k/2+3),k*k-10*k+4)
for v in [5-s.sqrt(21),5+s.sqrt(21)]:eq('exam13 repeated root',v*v-10*v+4,0)
eq('exam62 discriminant',(4+12*m)**2-80*(1+m*m),64*m*m+96*m-64)
for v in [R(1,2),-2]:eq('exam62 slopes',2*v*v+3*v-2,0)
eq('exam65 tangent',44+4*(-11),0)
print(f'{len(checks)} exact independent checks pass')
