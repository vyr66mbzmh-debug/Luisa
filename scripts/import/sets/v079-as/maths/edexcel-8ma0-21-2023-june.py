"""June 2023 AS Statistics, independently checked using the graph and printed counts."""
from math import comb, sqrt
from fractions import Fraction

counts=[6,24,16,4]
values=[61,63,65,67]
mean=sum(n*x for n,x in zip(counts,values))/50
assert mean==63.72
assert 1.587<sqrt(sum(n*(x-mean)**2 for n,x in zip(counts,values))/50)<1.589
assert [n for n in range(46) if n>=12 and 25+n-12<=45]==list(range(12,33))
assert Fraction(12*45,25).denominator!=1
pmf=lambda k: comb(50,k)*.25**k*.75**(50-k)
lower=min(range(13),key=lambda k:abs(sum(pmf(i) for i in range(k+1))-.025))
upper=min(range(14,51),key=lambda k:abs(sum(pmf(i) for i in range(k,51))-.025))
assert (lower,upper)==(6,19) and lower<10<upper
distribution=[Fraction(comb(2,k)*comb(6,3-k),comb(8,3)) for k in range(3)]
assert distribution==[Fraction(5,14),Fraction(15,28),Fraction(3,28)]
assert .017<sum(comb(10,i)*(1/9)**i*(8/9)**(10-i) for i in range(4,11))<.019
