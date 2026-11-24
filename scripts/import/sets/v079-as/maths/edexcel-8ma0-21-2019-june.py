from math import comb,sqrt
from sympy import Rational as R
assert 40*84/(84+56)==24 and 40-24==16 and 5.60*.5==2.8
# B and C are disjoint. Remaining unknown probability mass is 0.15.
z=R(25,100)*R(39,100)/(1-R(25,100))
assert z==R(13,100) and R(15,100)-z==R(2,100)
def prob(n,p,k):
    return comb(n,k)*p**k*(1-p)**(n-k)
assert .32 < sum(prob(28,.2,k) for k in range(7,29)) < .34
assert .64 < sum(prob(28,.2,k) for k in range(4,8)) < .67
assert round(1+4*(.75*184-131)/24,2)==2.17
assert round(sqrt(7704.1875/184-(539.75/184)**2),2)==5.77
tail=lambda k:sum(prob(30,.15,j) for j in range(k,31))
assert tail(9)<.05<tail(8) and round(tail(9),4)==.0278
