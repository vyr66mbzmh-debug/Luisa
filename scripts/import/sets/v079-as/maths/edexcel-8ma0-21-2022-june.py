from math import comb
from sympy import Rational as R, integrate, symbols
assert -R(11,10)*3==-R(33,10)
def damp(n,x):
    return comb(n,x)*0.08**x*0.92**(n-x)
assert round(damp(35,2),3)==0.243
assert round(1-sum(damp(35,i) for i in range(4)),3)==0.306
assert sum(damp(70,i) for i in range(3))<0.1
# The first three histogram classes have areas 15, 35 and 75. Median rank 128 falls in the fourth.
assert round(3.5+(128-125)/55,2)==3.55
x=symbols('x')
assert 256/integrate(x*(8-x),(x,0,8))==3
# The density is symmetric about x=4. The pressure chart has one printed tick (1200);
# its unlabelled intervals prevent an exact numerical median or range from being recovered.
assert R(3,4)*R(1,3)==R(1,4) and R(1,4)*R(2,3)==R(1,6)
assert 2*6+8==20 and 3*6+4*8==50
