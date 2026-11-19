"""Independent recurrence checks for probability-distribution practice working."""
from fractions import Fraction as F
from itertools import product
n=0
def eq(a,b,tol=1e-8):
 global n
 assert abs(a-b)<tol,(a,b)
 n+=1
# Dynamic convolution, independent of the solution's combinatorial formula.
def distribution(trials,p):
 d=[1.0]
 for _ in range(trials):
  out=[0.0]*(len(d)+1)
  for j,v in enumerate(d):out[j]+=v*(1-p);out[j+1]+=v*p
  d=out
 return d
CASES=[{'n': 6, 'p': 0.2, 'lo': 2, 'hi': 2, 'result': 0.2457600000000001}, {'n': 6, 'p': 0.2, 'lo': 4, 'hi': 4, 'result': 0.015360000000000006}, {'n': 6, 'p': 0.2, 'lo': 0, 'hi': 1, 'result': 0.6553600000000003}, {'n': 12, 'p': 0.6, 'lo': 6, 'hi': 6, 'result': 0.17657914982400003}, {'n': 12, 'p': 0.6, 'lo': 10, 'hi': 10, 'result': 0.06385228185599999}, {'n': 12, 'p': 0.6, 'lo': 9, 'hi': 12, 'result': 0.22533728255999996}, {'n': 8, 'p': 0.8, 'lo': 5, 'hi': 5, 'result': 0.14680063999999995}, {'n': 8, 'p': 0.8, 'lo': 3, 'hi': 3, 'result': 0.009175039999999992}, {'n': 8, 'p': 0.8, 'lo': 7, 'hi': 8, 'result': 0.5033164800000002}, {'n': 20, 'p': 0.12, 'lo': 3, 'hi': 3, 'result': 0.22420950302249013}, {'n': 20, 'p': 0.12, 'lo': 0, 'hi': 2, 'result': 0.5631315224061946}, {'n': 50, 'p': 0.8, 'lo': 40, 'hi': 40, 'result': 0.13981900517431545}, {'n': 50, 'p': 0.8, 'lo': 48, 'hi': 50, 'result': 0.0012854149532433082}, {'n': 10, 'p': 0.5, 'lo': 4, 'hi': 4, 'result': 0.205078125}, {'n': 7, 'p': 0.205078125, 'lo': 2, 'hi': 2, 'result': 0.2803368648974083}, {'n': 12, 'p': 0.3, 'lo': 0, 'hi': 2, 'result': 0.2528153478549998}, {'n': 12, 'p': 0.3, 'lo': 0, 'hi': 5, 'result': 0.8821512611379995}, {'n': 12, 'p': 0.3, 'lo': 7, 'hi': 12, 'result': 0.038600843057999976}, {'n': 15, 'p': 0.4, 'lo': 0, 'hi': 7, 'result': 0.786896817389568}, {'n': 15, 'p': 0.4, 'lo': 10, 'hi': 15, 'result': 0.03383330288435201}, {'n': 15, 'p': 0.4, 'lo': 2, 'hi': 6, 'result': 0.604641120878592}, {'n': 35, 'p': 0.61, 'lo': 0, 'hi': 24, 'result': 0.863198661916881}, {'n': 35, 'p': 0.61, 'lo': 28, 'hi': 35, 'result': 0.01379292996088202}, {'n': 35, 'p': 0.61, 'lo': 15, 'hi': 29, 'result': 0.9890253384694612}, {'n': 30, 'p': 0.25, 'lo': 0, 'hi': 9, 'result': 0.8034066369495109}, {'n': 30, 'p': 0.25, 'lo': 14, 'hi': 30, 'result': 0.008179192031380327}, {'n': 30, 'p': 0.25, 'lo': 10, 'hi': 14, 'result': 0.19384382888634874}, {'n': 25, 'p': 0.46, 'lo': 8, 'hi': 8, 'result': 0.06120870774938693}, {'n': 25, 'p': 0.46, 'lo': 13, 'hi': 25, 'result': 0.34286012433474083}, {'n': 6, 'p': 0.34286012433474083, 'lo': 4, 'hi': 6, 'result': 0.10981583980717327}, {'n': 25, 'p': 0.16666666666666666, 'lo': 4, 'hi': 25, 'result': 0.6184335052215822}, {'n': 40, 'p': 0.2, 'lo': 0, 'hi': 4, 'result': 0.07591449544989447}, {'n': 40, 'p': 0.2, 'lo': 0, 'hi': 5, 'result': 0.16132881723216427}, {'n': 40, 'p': 0.2, 'lo': 13, 'hi': 40, 'result': 0.04324162237632371}, {'n': 40, 'p': 0.2, 'lo': 12, 'hi': 40, 'result': 0.08750523592200614}, {'n': 40, 'p': 0.2, 'lo': 4, 'hi': 12, 'result': 0.9282962831639339}, {'n': 15, 'p': 0.4, 'lo': 8, 'hi': 8, 'result': 0.11805577445376003}, {'n': 15, 'p': 0.4, 'lo': 11, 'hi': 15, 'result': 0.009347660775424005}, {'n': 15, 'p': 0.4, 'lo': 8, 'hi': 15, 'result': 0.21310318261043207}, {'n': 5, 'p': 0.2, 'lo': 3, 'hi': 5, 'result': 0.05792000000000003}, {'n': 35, 'p': 0.64, 'lo': 0, 'hi': 17, 'result': 0.04431928103064738}, {'n': 35, 'p': 0.64, 'lo': 5, 'hi': 20, 'result': 0.24906071364914265}, {'n': 30, 'p': 0.15, 'lo': 0, 'hi': 1, 'result': 0.04802889862602792}, {'n': 30, 'p': 0.15, 'lo': 0, 'hi': 2, 'result': 0.1514006073236086}, {'n': 30, 'p': 0.15, 'lo': 10, 'hi': 30, 'result': 0.009657635199554846}, {'n': 30, 'p': 0.15, 'lo': 9, 'hi': 30, 'result': 0.027778207170239457}, {'n': 30, 'p': 0.15, 'lo': 2, 'hi': 9, 'result': 0.9423134661744165}, {'n': 25, 'p': 0.65, 'lo': 15, 'hi': 25, 'result': 0.7711612436085864}, {'n': 10, 'p': 0.7711612436085864, 'lo': 7, 'hi': 7, 'result': 0.23323103959871078}, {'n': 10, 'p': 0.7711612436085864, 'lo': 0, 'hi': 4, 'result': 0.012688848945703102}, {'n': 10, 'p': 0.125, 'lo': 1, 'hi': 1, 'result': 0.37582225166261196}, {'n': 10, 'p': 0.125, 'lo': 2, 'hi': 10, 'result': 0.36110217217355967}, {'n': 25, 'p': 0.25, 'lo': 10, 'hi': 25, 'result': 0.07132826270035508}, {'n': 25, 'p': 0.25, 'lo': 11, 'hi': 25, 'result': 0.02966991193554236}, {'n': 24, 'p': 0.1, 'lo': 2, 'hi': 24, 'result': 0.707523042051468}, {'n': 15, 'p': 0.707523042051468, 'lo': 9, 'hi': 9, 'result': 0.1391936160676888}, {'n': 30, 'p': 0.2, 'lo': 7, 'hi': 30, 'result': 0.39303008027426023}]
for c in CASES:
 d=distribution(c['n'],c['p']);eq(sum(d[c['lo']:c['hi']+1]),c['result']);eq(sum(d),1)
eq(F(1,1)/(1+F(1,2)+F(1,3)),F(6,11))
eq((1-F(1,6)+F(1,8))/5,F(23,120));eq(2*F(23,120)-F(1,8),F(31,120))
p=[.28,.22,.22,.28];eq(sum(p[i-1]*p[j-1] for i,j in product(range(1,5),repeat=2) if i+j>=7),.2016)
eq(sum(F(3,7)**k*F(4,7) for k in range(4))+F(3,7)**4,1)
p=[.2,.3,.35,.15]
eq(sum(p[i-1]*p[j-1] for i,j in product(range(1,5),repeat=2) if i+j==4),.23)
eq(sum(p[i-1]*p[j-1] for i,j in product(range(1,5),repeat=2) if i+j>5),.34)
eq(sum(.1+(k-1)*.05 for k in range(1,6)),1)
eq(F(6*3+6*2+3*2,121),F(36,121))
# Enumerate all distinct-student ordered selections for the minimum sample60.
pets=[k for k,count in enumerate([11,9,22,12,6],1) for _ in range(count)]
pairs=[(a,b) for i,a in enumerate(pets) for j,b in enumerate(pets) if i!=j]
eq(F(sum(a==b==2 for a,b in pairs),len(pairs)),F(6,295))
eq(F(sum(a+b==5 for a,b in pairs),len(pairs)),F(11,59))
print(n,'independent probability, normalization and sampling checks passed')
