from math import comb,sqrt,isclose
median=5+(15-3)*5/15
assert median==9 and 2*median+15==33
assert round(2*sqrt(5675/30-(355/30)**2),1)==14.0
p=lambda n,a,k:comb(n,k)*a**k*(1-a)**(n-k)
assert .8<sum(p(30,.28,k) for k in range(5,12))<.9
assert .01<sum(p(40,.25,k) for k in range(16,41))<.05
assert 1007>1010-1.5*(1013.5-1010) and 1022>1013.5+1.5*(1013.5-1010)
assert 102>50.7+1.5*(50.7-29.2) and 15>29.2-1.5*(50.7-29.2)
assert isclose(.1/.25,.4) and isclose(.2*.25,.05)
assert isclose(1-(.3+.1+.1+.05+.15),.3)
