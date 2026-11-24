"""June 2024 Statistics, independent calculations and checks of the figures."""
from math import comb,isclose
assert isclose(1.72+.28,2) and isclose(1.81+.11,1.92)
assert sum([22,48,56,58])==184 and not (0<=999<=360)
assert 112-64-25-13-3==7
assert 128*(1-1/8)==112
pmf=lambda n,p,k:comb(n,k)*p**k*(1-p)**(n-k)
assert round(pmf(27,.35,10),3)==.154
assert .16<sum(pmf(27,.35,k) for k in range(12,15))<.19
assert .05<sum(pmf(60,.12,k) for k in range(4))<.07
probs=[.2,.8*.2,.8**2*.2,.8**3]
assert isclose(sum(probs),1) and isclose(probs[2],.128)
assert isclose((1-.5-.2)/2,.15) and isclose(sum(probs[1:]),.8)
