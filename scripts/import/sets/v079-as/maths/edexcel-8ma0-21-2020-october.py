"""October 2020 Statistics, calculations from the printed questions and figures."""
from math import comb,sqrt
from fractions import Fraction
areas=[8,16,12,36,12,4]
assert round(100*(8+8)/sum(areas),1)==18.2
assert 5300>1100+2.5*1600
c=Fraction(1,3)-Fraction(1,10)-Fraction(15,100)
assert 2*c*Fraction(15,100)+Fraction(1,10)**2==Fraction(7,200)
assert [n//10 for n in (450,300,850)]==[45,30,85]
assert round(sqrt(3053/160-(692/160)**2),3)==.613
tail=lambda n,k:sum(comb(n,i)*(1/6)**i*(5/6)**(n-i) for i in range(k,n+1))
prob=tail(9,3)
assert .17<prob<.19 and .39<5*prob*(1-prob)**4<.42
assert tail(35,11)<.05
