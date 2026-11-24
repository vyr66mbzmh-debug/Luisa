from fractions import Fraction as F
from math import comb
assert 1-3*F(2,10)-F(1,10)==F(3,10)
ages=[5,45,90,130,60,1]
assert sum(ages)==331 and round(40+(331/2-140)/5.2,1)==44.9
assert 58.9+1.5*(58.9-27.3)>90
assert 155>26>3 and 16>2>1
mass=lambda n,k:comb(n,k)*.14**k*.86**(n-k)
assert round(mass(18,1),3)==.194
assert round(1-sum(mass(18,k) for k in range(4)),3)==.238
assert sum(mass(75,k) for k in range(5))<.025
# Enumerate both transfers. Each bag has its original total at the end.
answers={}
for n in range(1,8):
    a=[4,3,n];b=[5,3,1]
    for i in range(3):
        for j in range(3):
            final=[count-(k==i)+(k==j) for k,count in enumerate(a)]
            if len(set(final))==1:
                answers[n]=answers.get(n,F(0))+F(a[i],sum(a))*F(b[j]+(i==j),10)
assert answers=={2:F(2,45),5:F(1,8)}
