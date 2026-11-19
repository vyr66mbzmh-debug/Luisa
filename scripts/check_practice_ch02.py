"""Independent exact algebra and contextual checks for Pure Year 1 chapter 2. Requires SymPy in a private authoring environment."""
import sympy as s,json
from pathlib import Path
x,k,p,q=s.symbols('x k p q');R=s.Rational
checks=[]
def check(label,ok):
 assert bool(ok),label
 checks.append(label)
def eq(label,a,b): check(label,s.simplify(a-b)==0)
def roots(label,f,rs):
 for i,r in enumerate(rs):eq(label+f' root{i+1}',f.subs(x,r),0)
 check(label+' complete degree',len(rs)==s.degree(f,x) or s.degree(f,x)>2)
# Exact expected roots from independent coefficients, checked by substitution.
for label,f,rs in [
('2.1/1a',x*x+7*x+10,[-5,-2]),('2.1/1b',x*x-5*x-24,[8,-3]),('2.1/1c',x*x+6*x,[0,-6]),
('2.1/2a',7*x*x-21*x,[0,3]),('2.1/2b',4*x*x-49,[-R(7,2),R(7,2)]),('2.1/2c',4*x*x-20*x+25,[R(5,2),R(5,2)]),('2.1/2d',2*x*x-5*x+2,[R(1,2),2]),
('2.1/3a',(x-4)**2,[4,4]),('2.1/3b',2*x*x-x-21,[R(7,2),-3]),('2.1/3c',2*x*x+14*x+24,[-3,-4]),
('2.1/4a',x*x+8*x+6,[-4-s.sqrt(10),-4+s.sqrt(10)]),('2.1/4b',x*x+4*x-1,[-2-s.sqrt(5),-2+s.sqrt(5)]),('2.1/4c',2*x*x-12*x+15,[(6-s.sqrt(6))/2,(6+s.sqrt(6))/2]),
('2.1/5a',10*x-x*x-9,[1,9]),('2.1/5b',64*x*x-100,[-R(5,4),R(5,4)]),('2.1/5c',3*x*x+10*x-25,[R(5,3),-5]),('2.1/5d',3*x*x-12*x+5,[(6-s.sqrt(21))/3,(6+s.sqrt(21))/3]),('2.1/5f',2*x*x+6*x+1,[(-3-s.sqrt(7))/2,(-3+s.sqrt(7))/2]),
('2.1/6',6*x*x-x-35,[R(5,2),-R(7,3)]),('2.1/7',x*x+4*x+1,[-2-s.sqrt(3),-2+s.sqrt(3)]),('2.1/8',x*x+16*x-8,[-8-6*s.sqrt(2),-8+6*s.sqrt(2)]),('2.1/9a',R('1.5')+12*x-4*x*x,[(12-s.sqrt(168))/8,(12+s.sqrt(168))/8]),('2.1/9b',R('1.5')+12*x-4*x*x-R('9.5'),[1,2]),
('2.2/4a',x*x-2*x-10,[1-s.sqrt(11),1+s.sqrt(11)]),('2.2/4b',5*x*x+12*x+6,[(-6-s.sqrt(6))/5,(-6+s.sqrt(6))/5]),('2.2/4c',3*x*x-7*x-2,[(7-s.sqrt(73))/6,(7+s.sqrt(73))/6]),
('2.2/6',4-2*x-3*x*x,[(-1-s.sqrt(13))/3,(-1+s.sqrt(13))/3]),('2.2/7',6*x-2-x*x,[3-s.sqrt(7),3+s.sqrt(7)]),('2.3/2',x*x+2*x-3-(2*x+1),[-2,2]),
('2.3/3a',(x+2)*(x+7),[-2,-7]),('2.3/3b',81-x*x,[-9,9]),('2.3/3c',x**6+7*x**3+12,[-s.real_root(3,3),-s.real_root(4,3)]),('2.3/3d',x**3-4*x*x-21*x,[0,-3,7]),
('2.3/4',x*x+6*x+2,[-3-s.sqrt(7),-3+s.sqrt(7)]),('2.3/6a',x**8+6*x**4-7,[-1,1]),('2.3/6b',6*x**10-5*x**5+1,[s.real_root(R(1,3),5),s.real_root(R(1,2),5)]),('2.4/7',x*x-9*x-10,[-1,10]),
]:roots(label,f,rs)
for r in [0,5]:eq('2.1/5e original radical',r-s.sqrt(5*r),0)
# Complete-square identities, including each model.
for label,a,b in [
('2.2/1a',x*x+2*x,(x+1)**2-1),('2.2/1b',x*x-8*x,(x-4)**2-16),('2.2/1c',x*x-12*x,(x-6)**2-36),
('2.2/2a',x*x-8*x+12,(x-4)**2-4),('2.2/2b',x*x-x-12,(x-R(1,2))**2-R(49,4)),('2.2/2c',x*x-3*x-4,(x-R(3,2))**2-R(25,4)),
('2.2/3a',3*x*x-12*x+17,3*(x-2)**2+5),('2.2/3b',5*x*x-10*x+12,5*(x-1)**2+7),('2.2/3c',3*x*x-7*x+2,3*(x-R(7,6))**2-R(25,12)),
('2.2/5',x*x-7*x-2,(x-R(7,2))**2-R(57,4)),('2.2/6',4-2*x-3*x*x,-3*(x+R(1,3))**2+R(13,3)),('2.2/7',6*x-2-x*x,7-(x-3)**2),
('2.3/4',x*x+6*x+2,(x+3)**2-7),('2.3/5',x*x+6*x+13,(x+3)**2+4),
('2.4/2a',(x-1)**2+9,(x-1)**2+9),('2.4/2b',x*x+x-6,(x+R(1,2))**2-R(25,4)),('2.4/2c',-x*x-13*x-42,-(x+R(13,2))**2+R(1,4)),
('2.4/5',8*x-7-x*x,9-(x-4)**2),('2.4/6',x*x+6*x+4,(x+3)**2-5),('2.4/8',5*x*x-20*x+15,5*(x-2)**2-5),
('2.5/5',(k+3)**2-4*k,(k+1)**2+8),
('2.6/1',x-R('.04')*x*x,-R('.04')*(x-R('12.5'))**2+R('6.25')),
('2.6/2',R('73.5')*x-R('5.25')*x*x-R('107.5'),R('149.75')-R('5.25')*(x-7)**2),
('2.6/4',R('.4')*x-R('.00008')*x*x,500-R('.00008')*(x-2500)**2),
('2.6/5',120+R('12.25')*x-R('4.9')*x*x,R('127.65625')-R('4.9')*(x-R('1.25'))**2),
('2.6/6',125*x-R('6.25')*x*x-465,160-R('6.25')*(x-10)**2),
('problem-a/bronze',2*x-x*x,1-(x-1)**2),('problem-a/silver',114+R('10.4')*x-R('5.2')*x*x,R('119.2')-R('5.2')*(x-1)**2),
('problem-a/gold',125+R('12.75')*x-R('4.5')*x*x,R('134.03125')-R('4.5')*(x-R(17,12))**2),
('exam/38',16-6*x-x*x,25-(x+3)**2),('exam/43',x*x-6*x+16,(x-3)**2+7),('exam/52',x*x-6*x+13,(x-3)**2+4),
('exam/67',R('6.25')*(30*x-x*x)-R('1256.25'),150-R('6.25')*(x-15)**2),('exam/91',500*x-s.pi*x*x,62500/s.pi-s.pi*(x-250/s.pi)**2),
]:eq(label+' identity',a,b)
# Source discrepancy checks and contextual values.
eq('2.3/6c sole root',1-3+2,0);check('2.3/6c reject printed4',s.sqrt(2)-6+2!=0)
eq('2.3/7 factorisation',(2**x-2)*(2**x-4),2**(2*x)-6*2**x+8)
for a,b,c,D in [(-2,-11,-12,25),(1,6,9,0),(3,-12,18,-72),(1,-10,21,16),(-1,-10,-25,0),(1,8,19,-12)]:eq('discriminant',b*b-4*a*c,D)
eq('2.5/4 discriminant',k*k-100,(k-10)*(k+10));eq('2.5/6 discriminant',3**2-4*k*(-5),9+20*k)
check('2.5/6 k0 linear',s.degree((k*x*x+3*x-5).subs(k,0),x)==1)
eq('2.5/7 boundary',49-8*R(49,8),0)
eq('2.6/3 canal origin',R('1.92')*R('1.25')**2-3,0)
check('2.6/3 width',2*s.sqrt(2/R('1.92'))<R('2.1'))
eq('2.6/4 workers',R('.4')*1500-R('.00008')*1500**2,420)
for price,ok in [('7.47',False),('7.48',True)]:check('2.6/6 penny bound '+price,(160-R('6.25')*(R(price)-10)**2>120)==ok)
eq('2.6/7 equilibrium',8*2+8,2**2-14*2+48)
eq('problem-b/bronze',16-8*s.sqrt(2)**2,0);eq('problem-b/silver',24**2-24*24,0)
for val,r in [(2,-1),(6,-3)]:eq('problem-b/gold original',R(3-r*r,r+2),val);eq('problem-b/gold discriminant',val*val-8*val+12,0)
check('problem-b/gold reject-6',(-6)**2-8*(-6)+12>0)
eq('exam/52 length',s.sqrt(3**2+9**2),3*s.sqrt(10));eq('exam/67 loss',150-R('6.25')*(25-15)**2,-475)
# Results are printed for the release evidence; source files remain read-only.
print(len(checks),'exact checks pass')
