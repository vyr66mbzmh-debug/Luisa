"""Independent finite-outcome and probability checks against source inputs."""
from fractions import Fraction as F
from itertools import product,permutations
from statistics import mean,pstdev
n=0
def eq(a,b,tol=1e-8):
 global n
 assert abs(a-b)<tol,(a,b)
 n+=1
word='INTERPOLATION';eq(word.count('N')/len(word),2/13);eq(sum(c in 'AEIOU' for c in word)/len(word),6/13);eq(sum(c<'Q' for c in word)/len(word),10/13)
dice=list(product(range(1,7),range(1,5)))
for predicate,expected in [(lambda a,b:a*b==15,F(1,24)),(lambda a,b:a*b%2==0,F(3,4)),(lambda a,b:a*b>10,F(1,3))]:eq(F(sum(predicate(*d) for d in dice),24),expected)
eq(F(7+22+35,89),F(64,89));eq((35*.2+16+9)/89,32/89)
f=[20*.35,10*.6,10*.8,5*1.8,15,30*.5];eq(sum(f),60);eq(sum(f[:2])/60,13/60);eq((10+15)/60,5/12)
out=list(permutations([4,5,6,7],2));eq(F(sum(a%2==b%2==1 for a,b in out),12),F(1,6));eq(F(sum(a+b<12 for a,b in out),12),F(2,3))
eq(.8+.3-.9,.2);eq(1-.1-.2-.35-.15-.02,.18)
eq(30+32-17,45);eq(25-12-8+2,7);eq(30+32+25-17-8-12+2,52)
eq(.62-.2-.24,.18);eq(1-.21-.18-.2-.24-.06,.11)
eq(.0204/.12,.17);eq(.4-.15,.25);eq(.4*(1-.4-.35+.25),.2)
eq(.65-.3-.2,.15);eq(1-.3-.2-.15-.05,.3)
eq(.2/.4-.2,.3);eq(1-.25-.05-.15-.2-.3,.05)
eq(F(4,9)**2,F(16,81));eq(2*F(4,9)*F(5,9),F(40,81))
eq(F(3,15)*F(2,14),F(1,35));eq(2*F(3,15)*F(12,14),F(12,35))
eq(.4*.1+.6*.7,.46);eq(.6**3,.216);eq(3*.6*.4**2,.288);eq((F(3,5)**3+F(2,5)**3)**3,F(343,15625));eq((.06-.2*.05-.5*.07)/.3,.05)
# Ordered transfers of individually labelled balls, followed by an individual draw.
q=r=qr=F(0)
a='GGGGBBB';b='GGGBBBBB'
for i,j in permutations(range(7),2):
 bag=b+a[i]+a[j]
 for c in bag:
  w=F(1,420);same=a[i]==a[j];blue=c=='B'
  q+=w*same;r+=w*blue;qr+=w*(same and blue)
eq(q,F(3,7));eq(r,F(41,70));eq(qr,F(17,70))
for x in [.42,-.08]:eq(2*x*x-.68*x-.0672,0)
eq(1-.28-.42-(.42-.24),.12);eq((.3+.3)*(.2+.3),.3)
eq(2*F(6,9)*F(3,9),F(4,9));eq((6*5+3*2+2)/(11*10),19/55)
# Recursively enumerate replacement-dependent biscuit paths.
def paths(g,o,draws,eaten):
 if not draws:return F(eaten==2)
 return F(g,g+o)*paths(g,o,draws-1,eaten)+F(o,g+o)*paths(g,o-1,draws-1,eaten+1)
eq(paths(8,7,3,0),F(2348,6825));eq(2*F(4,20)*F(16,19),F(32,95));eq(1-F(16,20)*F(15,19),F(35,95))
eq((1-.3-.2-.15)/2,.175);eq((.05-.2*.03-.4*.04)/.4,.07)
v=[x for x,f in zip([6.5,9.5,12.5,15.5,18.5],[7,5,6,8,4]) for _ in range(f)]
eq(sum(v),366);eq(sum(x*x for x in v),4975.5);eq(mean(v),12.2);eq(pstdev(v),4.12431812546)
lo,hi=mean(v)-pstdev(v),mean(v)+pstdev(v);eq((7+5*(lo-8)/3+4+8*(17-hi)/3)/30,.4309318263224)
eq((50-12-22)/2,8);eq((12+8+22)/50,.84)
print(n,'independent source-input and outcome checks passed')
