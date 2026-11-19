"""Independent raw-data, interpolation and coding checks for practice Statistics 1 chapter 2."""
from fractions import Fraction as F
from math import sqrt
from statistics import mean,pstdev,median
count=0
def check(actual,expected,tolerance=1e-8):
 global count
 assert abs(float(actual)-expected)<=tolerance,(actual,expected)
 count+=1
def expanded(values,freq):return [x for x,f in zip(values,freq) for _ in range(f)]
def quantile(bins,freq,p):
 target=sum(freq)*p;cum=0
 for (lo,hi),f in zip(bins,freq):
  if cum+f>=target:return lo+(target-cum)*(hi-lo)/f
  cum+=f
 raise AssertionError('quantile outside range')
check(mean([550,450,300,400,450,500,450,300,600]),4000/9)
check(median([550,450,300,400,450,500,450,300,600]),450)
x=expanded([2,3,4,5,6],[6,11,13,7,2]);check(mean(x),144/39);check(median(x),4)
check(mean(expanded([12.5,17.5,22.5,27.5],[5,14,7,2])),520/28)
check((13*1.60+11*1.71)/24,1.65041666666667)
x=expanded([4,5,6,7,8],[12,15,18,11,7]);check(sum(x),364);check(median(x),6);assert mean(x+[7])>mean(x)
check(mean(expanded([3,5,7,9],[7,9,12,6])),6)
check(mean(expanded([17,19,21,23,25,27],[1,3,2,9,13,3])),729/31)
check(quantile([(1,3),(3,5),(5,7),(7,9)],[6,8,5,3],.5),4.25)
check(quantile([(1,3),(3,5),(5,7),(7,9)],[6,8,5,3],.75),6)
check(median([13,14,12,18,20,14,17,15,15,21,20,15,17,20]),16)
check(quantile([(40,45),(45,50),(50,55),(55,60)],[7,10,14,5],.5),50+5/14)
check(quantile([(25,30),(30,35),(35,40),(40,100)],[25,28,17,12],.5),30+16*5/28)
check(quantile([(25,30),(30,35),(35,40),(40,100)],[25,28,17,12],.7),35+4.4*5/17)
check(quantile([(1,3),(3,5),(5,10),(10,20)],[6,13,18,4],.8),8.83333333333)
x=sorted([45,48,52,60,51,53,47,49,50]);check(median(x[5:])-median(x[:4]),5)
x=sorted([5.5,3.8,7.5,8,5.5,4,5.3,5,3.3,3.5]);check(median(x),5.15);check(median(x[5:])-median(x[:5]),1.7)
bins=[(400,425),(425,450),(450,475),(475,500)];f=[18,25,28,13]
check(quantile(bins,f,.7)-quantile(bins,f,.3),31.90714285714)
check((.7-.3)*84,33.6)
check(pstdev([5,8,6,7,8,4])**2,20/9)
check(sum(v*v for v in expanded([0,1,2,3,4],[4,8,9,17,6])),293)
check(pstdev(expanded([0,1,2,3,4],[4,8,9,17,6])),1.18,.005)
check(pstdev(expanded([37.5,42.5,47.5,52.5,57.5],[5,7,8,6,4]))**2,40.5833333333333)
x=expanded([5,6,7,8],[11,15,23,16]);check(mean(x),6.68,.005);check(pstdev(x),1.02,.005)
x=expanded([4.25,4.75,5.25,5.75,6.25],[5,7,8,3,1]);check(mean(x),5);check(pstdev(x),sqrt(F(7,24)))
check(375.75/11-(57.5/11)**2,6.8347107438)
check(sqrt(7374.7/31-(477.4/31)**2),.8564744,.000001)
check(4*(365.25/10-(43.5/10)**2),70.41)
for a,b in [(1/5000,-20),(-1/5000,46)]:
 check(a*165000+b,13);check(a*a*881250000,35.25)
bins=[(-.5,2.5),(2.5,4.5),(4.5,6.5),(6.5,10.5)];f=[19,47,57,17]
check(quantile(bins,f,.75)-quantile(bins,f,.25),2.6875699888)
bins=[(0,20),(20,40),(40,60),(60,80),(80,100)];f=[12,31,58,44,15]
check(quantile(bins,f,.9)-quantile(bins,f,.1),56.96480938416)
check(quantile(bins,f,.125),25.16129032258)
k=F(4_09,100)*140-F(46625,100);k/=27
x=expanded([3.25,(3.5+float(k))/2,(float(k)+4)/2,4.25,5.25],[17,21,33,54,15]);check(mean(x),4.09);check(pstdev(x),.514,.0005)
x=expanded([11,13.5,17.5,22.5,27.5,40,75],[2,5,12,13,7,8,3]);check(mean(x)*1000,26590)
x=expanded([114.5,124.5,134.5,144.5,154.5],[7,8,11,10,4]);check(mean(x),133.5);check(pstdev(x),12.4,.05)
bins=[(4.5,9.5),(9.5,12.5),(12.5,16.5),(16.5,25.5),(25.5,40.5)];f=[1,3,7,12,2]
check(quantile(bins,f,.75)-quantile(bins,f,.25),8.52678571429)
check(mean(expanded([5,7,9,11],[5,13,8,4])),7.73333333333)
check(pstdev(expanded([5,7,9,11],[5,13,8,4])),1.82,.005)
check(44.625/10-2.1**2,.0525);check(4*sqrt(.0525),.91651513899)
check(sqrt(2700.25/32-(246.5/32)**2),5.004466,.0001)
check(45*(3+11/3)/32,9.375)
print(f'{count} independent source-data/coding checks passed')
