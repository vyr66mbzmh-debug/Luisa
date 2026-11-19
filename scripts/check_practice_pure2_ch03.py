"""Independent exact finite sums, recurrence, threshold and domain checks."""
import argparse,json,math
from pathlib import Path
import sympy as s
p=argparse.ArgumentParser();p.add_argument('--output',required=True,type=Path);args=p.parse_args();checks=[];R=s.Rational
n,k,x,y=s.symbols('n k x y')
def ck(label,a,b):
 a=R(str(a)) if isinstance(a,float) else a;b=R(str(b)) if isinstance(b,float) else b
 ok=s.simplify(a-b)==0;checks.append({'check':label,'passed':bool(ok)})
 if not ok:raise AssertionError((label,a,b))
def near(label,a,b,tol):
 ok=abs(float(a)-b)<tol;checks.append({'check':label,'passed':ok})
 if not ok:raise AssertionError((label,a,b))
def AS(a,d,N):return sum(s.sympify(a)+i*d for i in range(N))
def GS(a,r,N):return sum(s.sympify(a)*s.sympify(r)**i for i in range(N))
for label,f,values in [('3.1.1a',4*n+3,[7,11,15,19]),('3.1.1b',7-3*n,[4,1,-2,-5]),('3.1.1c',8+n/2,[R(17,2),9,R(19,2),10]),('3.1.1d',2*n-5,[-3,-1,1,3]),('3.1.6',3*n-4,[-1,2,5]),('3.2.5',4*n-5,[-1,3,7]),('3.7.3a',3*n-1,[2,5,8,11,14]),('3.7.3b',2**(1-n),[1,R(1,2),R(1,4),R(1,8),R(1,16)])]:
 for i,val in enumerate(values,1):ck(label+' term '+str(i),f.subs(n,i),val)
for label,a,d,N,ans in [('3.1.2a',2,4,10,38),('3.1.2b',5,-2,10,-13),('3.1.2c',-2,3,10,25),('3.1.2d',8*y,-3*y,10,-19*y),('3.1.3a',2,3,33,98),('3.1.3b',75,-2,41,-5),('3.1.3c',-3,4,30,113),('3.1.3d',-4*k,2*k,53,100*k),('3.1.4 term4',2,5,4,17),('3.1.4 term10',2,5,10,47),('3.1.5a',20,-R(1,2),25,8),('3.1.5b',20,-R(1,2),41,0),('3.1.7 term4',10,-4,4,-2),('3.1.7 term9',10,-4,9,-22),('3.1.7 target',10,-4,17,-54),('3.1.9',4,9,50,445),('3.2.7 term4',112,-3,4,103),('3.2.7 term12',112,-3,12,79),('3.2.7 term25',112,-3,25,40),('3.2.8 term8',3,5,8,38),('3.2.10 term15',-10,R(3,2),15,11),('3.2.10 term20',-10,R(3,2),20,R(37,2)),('3.8.1 term5',6,2,5,14),('3.8.1 marathon',6,2,19,42),('3.8.3 term52',R(1,10),R(1,20),52,R(265,100)),('setA bronze term16',-R(25,2),R(5,2),16,25),('setA bronze term25',-R(25,2),R(5,2),25,R(95,2)),('exam24 term20',2,6,20,116)]:ck(label,s.sympify(a)+(N-1)*d,ans)
for label,a,d,N,total in [('3.2.1a',5,4,20,860),('3.2.1b',3,5,15,570),('3.2.1c',12,-2,40,-1080),('3.2.1d',8,-R(1,2),25,50),('3.2.2a',6,3,16,456),('3.2.2b',52,-5,32,-816),('3.2.2c',-2,3,60,5190),('3.2.2d',120,-8,16,960),('3.2.3',1,1,60,1830),('3.2.4 below',5,3,24,948),('3.2.4 above',5,3,25,1025),('3.2.6',2,2,100,10100),('3.2.7',112,-3,50,1925),('3.2.8',3,5,12,366),('3.2.9',13,-2,20,-120),('3.2.10',-10,R(3,2),60,2055),('3.8.1 total',6,2,20,500),('3.8.3 savings',R(1,10),R(1,20),52,R(715,10)),('3.8.4 option1',120,12,24,6192),('setA bronze sum',-R(25,2),R(5,2),30,R(1425,2)),('setA silver',R(25,2),R(25,2),16,1700),('exam24 sum',2,6,50,7450)]:ck(label,AS(a,d,N),total)
for pv in [-3,R(5,2)]:ck('3.1.8 root '+str(pv),pv**2-15,-pv-pv**2)
ck('3.1.9 differences',(4*4-3)-4,(3*4+10)-(4*4-3));ck('3.2.5 general sum',n*(2*(-1)+(n-1)*4)/2,n*(2*n-3))
ck('3.2.9 pair',13-2+13-10,14);ck('3.2.11 differences',4*5+5-3*5,7*5-(4*5+5));ck('3.2.11 general sum',n*(10+10*(n-1))/2,5*n*n)
ck('3.2.12 differences',4*15+3-3*15,6*15-9-(4*15+3));ck('3.2.12 general sum',n*(18+18*(n-1))/2,9*n*n)
for label,a,r,N,term in [('3.3.1a',2,3,4,54),('3.3.1b',60,R(1,2),4,R(15,2)),('3.3.1c',10,-2,4,-80),('3.3.1d',40,R(3,2),4,135),('3.3.3',5,2,10,2560),('3.3.4 below',4,3,12,708588),('3.3.4 above',4,3,13,2125764),('3.3.5 term4',R(128,125),R(5,2),4,16),('3.3.5 term7',R(128,125),R(5,2),7,250),('3.3.7 term3',243,R(2,3),3,108),('3.3.7 term6',243,R(2,3),6,32),('3.3.9 below',R(5,2),2,12,5120),('3.3.9 above',R(5,2),2,13,10240),('3.4.4 term4',3,2,4,24),('3.4.4 term5',3,2,5,48),('3.4.8 term2',120,R(4,5),2,96),('3.5.3 term5',6,R(4,5),5,R(24576,10000)),('3.5.3 term7',6,R(4,5),7,R(1572864,1000000)),('3.8.2 term2',28000,R(41,40),2,28700),('exam76 term2 positive',405,R(2,3),2,270),('exam76 term4 positive',405,R(2,3),4,120),('exam76 term2 negative',-405,-R(2,3),2,270),('exam76 term4 negative',-405,-R(2,3),4,120),('exam80 term4',R(5,11),-3,4,-R(135,11))]:ck(label,s.sympify(a)*s.sympify(r)**(N-1),term)
for label,a,r,N,total in [('3.4.1a',2,3,10,59048),('3.4.1c',3,-2,8,-255),('3.4.2a',5,2,8,1275),('3.4.2b',13122,R(1,3),9,19682),('3.4.2c',1024,-R(1,4),8,R(13107,16)),('3.4.2d',128,R(3,2),7,4118),('3.4.3 below',3,2,18,786429),('3.4.3 above',3,2,19,1572861),('3.4.4 sum',3,2,20,3145725),('3.4.8 first3',120,R(4,5),3,R(2928,10)),('3.5.5 finite',54,R(1,3),4,80),('3.5.9 finite',80,R(1,3),6,R(29120,243)),('3.6.3',3,2,20,3145725),('3.6.6',4*3**9,3,6,28658448),('3.6.7',30,3,10,885720),('3.6.9 first15',8,2,15,262136),('3.6.9 next5',4*2**16,2,5,8126464),('exam80 sum10',R(5,11),-3,10,-6710)]:ck(label,GS(a,r,N),total)
# Test both adjacent integers for each strict threshold, independently summing terms.
for label,F,limit,qualifies,N in [('3.3.7',lambda n:243*R(2,3)**(n-1),1,'lt',15),('3.4.5',lambda n:GS(10,R(3,5),n),20,'gt',4),('3.4.6',lambda n:GS(20,R(4,5),n),50,'gt',4),('3.5.10',lambda n:GS(6,R(2,5),n),R(999,100),'gt',8),('3.8.5',lambda n:15000*R(3,4)**n,1000,'lt',10),('3.8.7',lambda n:2*R(3,4)**n,R(1,10),'lt',11),('exam64',lambda n:80-GS(30,R(5,8),n),R(1,2),'lt',11),('exam68',lambda n:GS(10,R(3,5),n),R(2499,100),'gt',16),('exam73',lambda n:60000*R(27,25)**(n-1),240000,'gt',20),('exam76',lambda n:GS(405,R(2,3),n),1200,'gt',11)]:
 for m,expected in [(N-1,False),(N,True)]:
  actual=F(m)<limit if qualifies=='lt' else F(m)>limit;ck(label+' threshold '+str(m),int(bool(actual)),int(expected))
for label,a,r,total in [('3.5.1',2,R(1,10),R(20,9)),('3.5.2a',5,R(2,5),R(25,3)),('3.5.2c',81,-R(1,3),R(243,4)),('3.5.3 positive',6,R(4,5),30),('3.5.3 negative',6,-R(4,5),R(10,3)),('3.5.4a',8,R(17,25),25),('3.5.4b',32,R(1,5),40),('3.5.5',54,R(1,3),81),('3.5.6',4,R(2,3),12),('3.5.7',R(3,8),R(1,2),R(3,4)),('3.5.9',80,R(1,3),120),('3.5.10 low',6,R(2,5),10),('3.5.10 high',4,R(3,5),10),('3.6.4c',R(10,3),R(2,3),10),('3.6.10',1,R(4,5),5),('setB bronze',R(3,256),R(1,2),R(3,128)),('exam68',10,R(3,5),25),('exam76 positive',405,R(2,3),1215),('exam76 negative',-405,-R(2,3),-243)]:ck(label,s.sympify(a)/(1-r),total)
ck('3.5.8 fifth term',4*R(19,20),R(19,5))
for ratio in [R(19,20)**R(1,4),-R(19,20)**R(1,4)]:ck('3.5.8 signed ratio '+str(ratio),1,20*(1-ratio**4))
for label,terms,total in [('3.6.1a',[4*r-3 for r in range(1,7)],66),('3.6.1b',[2*r**3 for r in range(1,6)],450),('3.6.1c',[s.cos(s.pi*r/2) for r in range(5)],1),('3.6.1d',[3*(-R(1,2))**r for r in range(3,8)],-R(33,128)),('3.6.2',[5*r-1 for r in range(1,13)],378),('3.6.4a',[3*r+2 for r in range(1,11)],185),('3.6.4b',[3]*20,60),('3.6.5',[5-2*r for r in range(8,31)],-759),('3.6.8',[3*r+6 for r in range(1,21)],750),('3.6.11',[4+3*r+2**(r-1) for r in range(1,11)],1228),('setB silver',[2*r-5 for r in range(8,21)],299),('setB gold',[3*r+2**r+R(9,2) for r in range(1,17)],131550),('exam61a',[2+4*r+3**r for r in range(1,13)],797496)]:ck(label,sum(terms),total)
# Iterate the original recurrences rather than using their authored closed forms.
for label,first,func,values in [('3.7.1a',3,lambda a:2*a-1,[3,5,9,17]),('3.7.1b',10,lambda a:a-4,[10,6,2,-2]),('3.7.1c',4,lambda a:a*a/2,[4,8,32,512]),('3.7.3d',1,lambda a:2*a+1,[1,3,7,15,31]),('3.7.3e',8,lambda a:4-a,[8,-4,8,-4,8]),('3.7.5',4,lambda a:2*a-5,[4,3,1]),('3.7.6',5,lambda a:4*a-8,[5,12,40,152,600])]:
 val=s.sympify(first)
 for i,expected in enumerate(values):ck(label+' term '+str(i+1),val,expected);val=func(val)
seq=[s.Integer(3)]
for i in range(1,50):seq.append(1-1/(seq[-1]-2))
ck('3.7.9 first50',sum(seq),75);ck('3.7.9 combined',sum(seq)+sum(seq[:-1]),150)
seq=[s.Integer(3)]
for i in range(1,400):seq.append(seq[-1]+(-1)**i)
ck('3.7.4 sum',sum(seq),1000);ck('3.7.4 term399',seq[398],3)
ck('3.7.7 sine sum',sum(s.sin(s.pi*r/2) for r in range(1,201)),0)
ck('3.7.8 a3',5*(5*k+4)+4,25*k+24);ck('3.7.8 sum',k+(5*k+4)+(25*k+24)+(125*k+124),4*(39*k+38))
seq=[R(3,2)]
for i in range(3):seq.append(3*seq[-1]-5)
ck('exam27 sum',sum(seq),-30)
seq=[R(3,4)]
for i in range(199):seq.append(-1/seq[-1])
ck('exam61 recurrence',sum(seq),-R(175,3))
for label,value,answer,tol in [('3.3.7 term20',243*R(2,3)**19,.110,.0005),('3.3.8 ratio',3**(-R(1,4)),.760,.0005),('3.4.1b',GS(48,R(1,2),12),96,.05),('3.4.1d',GS(810,R(2,3),9),2370,5),('3.4.5 term10',10*R(3,5)**9,.101,.0005),('3.4.7 term20',16*R(3,4)**19,.0677,.00005),('3.4.7 sum20',GS(16,R(3,4),20),63.8,.05),('3.4.8 sum10',GS(120,R(4,5),10),536,.5),('3.4.9 sum20',GS(2,(1+s.sqrt(5))/2,20),48900,50),('3.5.9 difference',80*R(1,3)**3-80*R(1,3)**4,1.98,.005),('3.8.2 population',28000*R(41,40)**9,34968,.5),('3.8.4 option2',GS(110,R(107,100),24),6399.43,.005),('3.8.5 value3',15000*R(3,4)**3,6328,.5),('3.8.6 year4',250*R(21,20)**3,289.41,.005),('3.8.6 total',GS(250,R(21,20),10),3144.47,.005),('3.8.6 discounted',sum(250*R(21,20)**i-min(25*R(21,20)**i,35) for i in range(10)),2836,.5),('3.8.7 distance',2+2*GS(R(3,2),R(3,4),9),13.10,.005),('exam64 sum15',GS(30,R(5,8),15),79.9,.05),('exam68 term20',10*R(3,5)**19,.000609,.0000005),('exam73 total',GS(60000,R(27,25),10),870000,5000)]:near(label,value,answer,tol)
ck('exam80 geometric identity',(4*R(10,11)-5)**2,(6*R(10,11)-5)*(5-R(10,11)))
args.output.write_text(json.dumps(checks,indent=2)+'\n');print(len(checks),'independent checks passed')
