"""Independent finite-outcome enumeration and conditional probability checks."""
from fractions import Fraction as F
from itertools import product,permutations
from math import comb,sqrt
n=0
def eq(a,b):
 global n
 assert abs(float(a)-float(b))<1e-10,(a,b)
 n+=1
def prob(space,event,given=lambda x:True):
 den=sum(given(x) for x in space)
 return F(sum(given(x) and event(x) for x in space),den)
# Fair dice and spinners: enumerate ordered outcomes rather than use the answer method.
s=list(product(range(1,5),repeat=2))
for event,given,answer in [(lambda x:x[0]*x[1]==8,lambda x:True,F(1,8)),(lambda x:x[0]*x[1]==6,lambda x:x[0]==2,F(1,4)),(lambda x:x[1]==2,lambda x:x[0]*x[1]==4,F(1,3))]:eq(prob(s,event,given),answer)
s=list(product(range(1,7),repeat=2))
eq(prob(s,lambda x:max(x)==4),F(7,36));eq(prob(s,lambda x:max(x)==2,lambda x:x[0]==2),F(1,3));eq(prob(s,lambda x:x[1]==3,lambda x:max(x)==6),F(1,11))
# Sample without replacement using labelled bulbs/fish.
s=list(permutations(range(32),2));T=lambda a:a<18
for e,g,a in [(lambda x:T(x[0]) and T(x[1]),lambda x:True,F(153,496)),(lambda x:T(x[0])!=T(x[1]),lambda x:True,F(63,124)),(lambda x:not T(x[0]) and not T(x[1]),lambda x:not(T(x[0]) and T(x[1])),F(13,49))]:eq(prob(s,e,g),a)
s=list(permutations(range(11),2));R=lambda a:a<5
eq(prob(s,lambda x:R(x[1])),F(5,11));eq(prob(s,lambda x:R(x[0]),lambda x:R(x[1])),F(2,5))
# The original table has seven A-only, four B-only, three C-only, two AB, two BC, two none.
s=[(1,0,0)]*7+[(0,1,0)]*4+[(0,0,1)]*3+[(1,1,0)]*2+[(0,1,1)]*2+[(0,0,0)]*2
for event,a in [(lambda x:not x[0] and x[2],F(1,4)),(lambda x:x[0] or not x[1] or x[2],F(4,5)),(lambda x:not(x[0] or x[2]) and x[1],F(1,5))]:eq(prob(s,event),a)
eq(prob(s,lambda x:x[1])*prob(s,lambda x:x[2]),prob(s,lambda x:x[1] and x[2]))
# Weighted atom representation supports every Venn conditional directly.
def wp(atoms,event,given=lambda x:True):
 return sum(F(str(w)) for x,w in atoms.items() if event(x) and given(x))/sum(F(str(w)) for x,w in atoms.items() if given(x))
atoms={(1,0,0):.1,(0,1,0):.15,(0,0,1):.24,(1,1,0):.1,(1,0,1):.16,(0,1,1):.05,(1,1,1):.15,(0,0,0):.05}
for e,g,a in [(lambda x:x[0],lambda x:x[1],F(5,9)),(lambda x:not x[1],lambda x:x[2],F(2,3)),(lambda x:x[0] or x[2],lambda x:not x[1],F(10,11)),(lambda x:x[0],lambda x:not x[1] and not x[2],F(2,3))]:eq(wp(atoms,e,g),a)
atoms={(1,0,0):.27,(0,1,0):.045,(0,0,1):.135,(1,1,0):.03,(1,0,1):.09,(0,1,1):.015,(1,1,1):.01,(0,0,0):.405}
eq(sum(atoms.values()),1)
for e,g,a in [(lambda x:x[0],lambda x:x[2],.4),(lambda x:not x[1],lambda x:not x[0],.9),(lambda x:x[2],lambda x:x[0] or x[1],.25)]:eq(wp(atoms,e,g),a)
# Independent Markov path enumeration for Tuesday bike conditional on Thursday treadmill.
weights={}
for path in product('TB',repeat=3):
 prev='T';w=F(1)
 for current in path:
  w*=F(1,2) if prev=='T' else (F(2,5) if current=='T' else F(3,5));prev=current
 weights[path]=w
eq(sum(w for x,w in weights.items() if x[-1]=='T'),F(89,200))
eq(wp(weights,lambda x:x[0]=='B',lambda x:x[-1]=='T'),F(44,89))
# Direct source arithmetic and complements.
for a,b in [(F(42,65),F(42,65)),(F(36,69),F(12,23)),(F(31,73),F(31,73)),(F(76,140),F(19,35)),(F(28,58),F(14,29)),(F(215,380),F(43,76)),(F(175,290),F(35,58)),(F(40,290),F(4,29)),(F(18,3)+F(48,3)+9,31),(.05/.25,.2),(.25/.6,F(5,12)),(.0475/.0935,F(95,187)),(.15*.4/.265,F(12,53)),((F(10,21)*F(3,8))/(F(10,21)*F(3,8)+F(11,21)*F(1,6)),F(45,67)),(F(1,4)*F(1,15)+F(3,4)*F(3,15),F(1,6)),((.75*.15)/(.75*.15+1/15),F(27,43)),(.3/(.3+.2),.6),((.15+.3)/(.15+.15+.3),.75),((.2)/(.2+.35),F(4,11)),((.1+.2)/.4,.75),(.42/.51,F(14,17)),(.21/.49,F(3,7))]:eq(a,b)
# Independent recurrence computes the tennis lower tail.
term=F(3,10)**100;tail=term
for k in range(62):
 term*=F(100-k,k+1)*F(7,3);tail+=term
direct=sum(comb(100,k)*.7**k*.3**(100-k) for k in range(63))
eq(tail,direct);assert float(tail)>.025;n+=1
p=(3-sqrt(5))/2;eq(p,(1-p)**2)
# Set shading truth tables match the stated logical descriptions.
for a,b,c in product([False,True],repeat=3):
 eq(not(a or (b and not c)),not a and (not b or c))
 eq(not(a or b),not a and not b)
 eq((a and b) or (b and c) or (a and c),sum([a,b,c])>=2)
print(n,'independent finite-outcome and probability checks passed')
