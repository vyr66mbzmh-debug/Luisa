"""Independent recurrence checks for hypothesis-testing practice working."""
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
CASES=[{'n': 50, 'p': 0.65, 'lo': 0, 'hi': 24, 'result': 0.010043644067996389}, {'n': 50, 'p': 0.6, 'lo': 45, 'hi': 50, 'result': 2.674531664946129e-06}, {'n': 20, 'p': 0.4, 'lo': 0, 'hi': 3, 'result': 0.01596116279000825}, {'n': 25, 'p': 0.45, 'lo': 17, 'hi': 25, 'result': 0.01735689533793306}, {'n': 40, 'p': 0.9, 'lo': 0, 'hi': 33, 'result': 0.099516423965551}, {'n': 50, 'p': 0.1, 'lo': 0, 'hi': 1, 'result': 0.03378585969243189}, {'n': 10, 'p': 0.3, 'lo': 7, 'hi': 10, 'result': 0.010592078399999994}, {'n': 26, 'p': 0.05, 'lo': 4, 'hi': 26, 'result': 0.038741396189987724}, {'n': 15, 'p': 0.4, 'lo': 0, 'hi': 3, 'result': 0.090501902401536}, {'n': 40, 'p': 0.7, 'lo': 34, 'hi': 40, 'result': 0.02376094641254017}, {'n': 200, 'p': 0.05, 'lo': 16, 'hi': 200, 'result': 0.044355629167060845}, {'n': 120, 'p': 0.125, 'lo': 25, 'hi': 120, 'result': 0.006846175538109817}, {'n': 50, 'p': 0.02, 'lo': 3, 'hi': 50, 'result': 0.07842774835096901}, {'n': 15, 'p': 0.0369900902677794, 'lo': 4, 'hi': 15, 'result': 0.0018404132161848423}, {'n': 15, 'p': 0.65, 'lo': 13, 'hi': 15, 'result': 0.06173409536528498}, {'n': 50, 'p': 0.4, 'lo': 28, 'hi': 50, 'result': 0.016034763503380206}, {'n': 300, 'p': 0.004, 'lo': 5, 'hi': 300, 'result': 0.0076003471667100775}, {'n': 30, 'p': 0.2, 'lo': 0, 'hi': 3, 'result': 0.12271080639416354}, {'n': 25, 'p': 0.2, 'lo': 6, 'hi': 6, 'result': 0.1633459187726983}, {'n': 25, 'p': 0.2, 'lo': 9, 'hi': 25, 'result': 0.046774242177772915}, {'n': 42, 'p': 0.36, 'lo': 22, 'hi': 42, 'result': 0.02180363182892766}]
CRITICAL=[{'n': 8, 'p': 0.6, 'alpha': 0.05, 'direction': 'low', 'closest': False, 'thresholds': {'low': 2}, 'actual': 0.049807360000000016}, {'n': 15, 'p': 0.3, 'alpha': 0.1, 'direction': 'high', 'closest': False, 'thresholds': {'high': 8}, 'actual': 0.050012540053775964}, {'n': 25, 'p': 0.42, 'alpha': 0.1, 'direction': 'two', 'closest': False, 'thresholds': {'low': 6, 'high': 16}, 'actual': 0.07153508361324744}, {'n': 30, 'p': 0.2, 'alpha': 0.05, 'direction': 'low', 'closest': False, 'thresholds': {'low': 2}, 'actual': 0.044178985151997086}, {'n': 20, 'p': 0.6, 'alpha': 0.1, 'direction': 'high', 'closest': False, 'thresholds': {'high': 16}, 'actual': 0.0509519531941665}, {'n': 50, 'p': 0.05, 'alpha': 0.2, 'direction': 'two', 'closest': False, 'thresholds': {'low': 0, 'high': 6}, 'actual': 0.11472114826649038}, {'n': 25, 'p': 0.3, 'alpha': 0.05, 'direction': 'two', 'closest': True, 'thresholds': {'low': 3, 'high': 13}, 'actual': 0.05071025711690047}, {'n': 30, 'p': 0.6, 'alpha': 0.05, 'direction': 'high', 'closest': False, 'thresholds': {'high': 23}, 'actual': 0.043524118996554916}, {'n': 50, 'p': 0.1, 'alpha': 0.1, 'direction': 'two', 'closest': False, 'thresholds': {'low': 1, 'high': 10}, 'actual': 0.058323795397023384}, {'n': 30, 'p': 0.25, 'alpha': 0.1, 'direction': 'two', 'closest': True, 'thresholds': {'low': 3, 'high': 12}, 'actual': 0.08810760577535248}, {'n': 30, 'p': 0.36, 'alpha': 0.05, 'direction': 'two', 'closest': False, 'thresholds': {'low': 5, 'high': 17}, 'actual': 0.03455080055027585}, {'n': 35, 'p': 0.45, 'alpha': 0.1, 'direction': 'two', 'closest': True, 'thresholds': {'low': 10, 'high': 21}, 'actual': 0.08900635166495145}, {'n': 20, 'p': 0.4, 'alpha': 0.05, 'direction': 'two', 'closest': False, 'thresholds': {'low': 3, 'high': 13}, 'actual': 0.0369900902677794}, {'n': 25, 'p': 0.3, 'alpha': 0.05, 'direction': 'two', 'closest': True, 'thresholds': {'low': 3, 'high': 13}, 'actual': 0.05071025711690047}, {'n': 15, 'p': 0.34, 'alpha': 0.1, 'direction': 'two', 'closest': True, 'thresholds': {'low': 2, 'high': 9}, 'actual': 0.10692139462584022}]
for c in CASES:
 d=distribution(c['n'],c['p']);eq(sum(d[c['lo']:c['hi']+1]),c['result']);eq(sum(d),1)
for c in CRITICAL:
 d=distribution(c['n'],c['p']);target=c['alpha']/2 if c['direction']=='two' else c['alpha'];actual=0
 for side,k in c['thresholds'].items():
  probs=([0]+[sum(d[:j+1]) for j in range(c['n']+1)]) if side=='low' else ([sum(d[j:]) for j in range(c['n']+1)]+[0])
  indexes=list(range(-1,c['n']+1)) if side=='low' else list(range(c['n']+2))
  value=probs[indexes.index(k)];actual+=value
  if c['closest']:eq(abs(value-target),min(abs(v-target) for v in probs))
  else:
   assert value<=target+1e-12;n+=1
   adjacent=k+1 if side=='low' else k-1
   assert probs[indexes.index(adjacent)]>target;n+=1
 eq(actual,c['actual'])
d=distribution(50,.05);eq(d[0]+sum(d[5:]),.180615762138,.0001)
print(n,'independent tail, boundary and significance checks passed')
