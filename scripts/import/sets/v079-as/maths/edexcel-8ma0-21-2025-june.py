"""Calculations from the printed June 2025 AS Statistics questions."""
from math import comb, sqrt

def binomial(n,p,k):
    return comb(n,k)*p**k*(1-p)**(n-k)

assert 0.16 < binomial(20,.37,8) < .18
assert .18 < sum(binomial(20,.37,i) for i in range(6)) < .21
assert 1007 < 1018-1.5*(1025-1018) < 1009
assert round((184-161)/4)==6
assert round((1-.2)/5,2)==.16
upper=lambda k:sum(binomial(40,.2,i) for i in range(k,41))
assert round(upper(11),3)==.161 and upper(12)>.05>upper(13)
assert round(sqrt(394/25),3)==3.970
slope=-3.5/500
assert round(20-1700*slope,1)==31.9
p,q,r,s,t,u=.18,.12,.22,.06,.19,.23
assert round(p+q+s+t,2)==.55 and round(q+s,2)==.18
assert round((p+q)*(q+r+s),2)==q and round(sum([p,q,r,s,t,u]),2)==1
