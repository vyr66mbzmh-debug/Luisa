from fractions import Fraction as F
from math import comb,isclose
assert 4.5*10-47<0
assert isclose((.06-.1*.09-.3*.03)/.6,.07)
p=lambda n,a,k:comb(n,k)*a**k*(1-a)**(n-k)
assert sum(p(32,1/3,k) for k in range(16,33))<.05
counts=[2,3,2,2,3,1,2,1,2]
assert sum(counts)==18 and sum(f*x for f,x in zip(counts,[6,7,8,9,11,12,13,14,16]))==184
assert isclose(sum([.15,.35,.15,.35]),1) and [x for x in range(1,5) if 12/x-x<=4]==[2,3,4]
assert 2+9*2-5*2**2==0
assert .3*80==24 and 24/.5==48 and (4800-24*(80+48)/2)/24+128==264
s=lambda t:t**2*(t-1)**2/2
assert 2*s(F(1,2))+s(2)==F(33,16)
assert 2*(1-F(5,7))==F(4,7) and F(4,7)/(1+F(5,7))==F(1,3)
