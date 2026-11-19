"""Independent signed-moment, equilibrium and tipping checks for Moments."""
import argparse,json
from pathlib import Path
import sympy as s
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);args=p.parse_args();checks=[];R=s.Rational;pi=s.pi

def ck(label,a,b):
 ok=s.simplify(a-b)==0;checks.append({'check':label,'passed':bool(ok)})
 if not ok:raise AssertionError((label,a,b))
def near(label,a,b,tol):
 ok=abs(float(a)-b)<tol;checks.append({'check':label,'passed':ok})
 if not ok:raise AssertionError((label,a,b))
def moment(forces,pivot=0):return sum((x-pivot)*fy-y*fx for x,y,fx,fy in forces)
# Counterclockwise is positive. Coordinates and force components are read from diagrams.
for label,forces,pivot,w in [('4.1.1a',[(0,3,-14,0)],0,42),('4.1.1b',[(0,-R(3,10),8,0)],0,R(12,5)),('4.1.1c',[(R(12,5),0,0,-20)],0,-48),('4.1.3',[(0,-R(3,10),5,0)],0,R(3,2)),('4.1.4a',[(R(1,10),s.sqrt(3)/10,0,-8)],0,-R(4,5)),('4.1.4c',[(R(1,10),s.sqrt(3)/10,0,-8)],R(1,5),R(4,5)),('4.1.5a',[(R(1,10),0,0,-10)],0,-1),('4.1.5c',[(R(1,10),0,0,-10)],R(3,10),2),('4.2.1',[(-2,0,0,10),(5,0,0,5)],0,5),('4.2.2',[(-2,0,0,4),(3,0,0,-6),(6,0,0,10)],0,34),('4.2.4',[(-2,0,0,-3),(-1,0,0,-6),(1,0,0,10),(2,0,0,-11)],0,0),('4.2.5',[(-6,0,0,R(19,6)),(2,0,0,-3),(4,0,0,5)],0,-5),('4.2.6 P',[(-1,0,0,-7),(1,0,0,10),(4,0,0,-R(23,6))],0,R(5,3)),('4.2.6 Q',[(-3,0,0,-7),(-1,0,0,10),(2,0,0,-R(23,6))],0,R(10,3)),('exam21',[(-2,0,0,4),(R(3,2),0,0,-3),(R(9,2),0,0,12),(R(15,2),0,0,-R(107,15))],0,-12)]:ck(label,moment(forces,pivot),w)
for label,a,b,tol in [('4.1.2a',5*R(3,2)*s.sin(70*pi/180),7.05,.005),('4.1.2b',80*s.sin(75*pi/180),77.3,.05),('4.2.3',moment([(-3,0,10*s.cos(pi/3),10*s.sin(pi/3)),(-2,0,0,-6),(2,0,-10*s.cos(pi/4),10*s.sin(pi/4))]),.161,.0005),('4.2.7',moment([(-120,20,-2000*s.sin(pi/4),-2000*s.cos(pi/4)),(-120,0,1100*s.cos(pi/3),-1100*s.sin(pi/3))])/1000,312,.5),('4.4.4',R(125,8)*s.cos(pi/9),14.7,.05),('4.4.6',1+4/s.sqrt(13),2.11,.005),('exam21 W',R(107,15),7.13,.005)]:near(label,a,b,tol)
ck('4.1.2c',7*R(6,5)*s.sin(pi/6),R(21,5));ck('4.1.6 angle',12*6*s.sin(pi/6),36);ck('4.1.7 ratio',R(2,5),2*(R(3,5)-R(2,5)))
# Each equilibrium is verified by net vertical force and net moment about A.
g=s.symbols('g',positive=True);m,l,d,W,X=s.symbols('m l d W X',positive=True)
cases=[('4.3.1',[(0,-50),(2,100),(4,-50)]),('4.3.2',[(1,R(50,3)),(4,R(250,3)),(R(7,2),-100)]),('4.3.4',[(0,m*g/3),(3*l/4,2*m*g/3),(l/2,-m*g)]),('4.3.5',[(R(11,4),24),(4,6),(3,-30)]),('4.3.8 unloaded',[(1,10*g/3),(4,20*g/3),(3,-10*g)]),('4.3.8 loaded',[(1,15*g-5*g*(X+4)/3),(4,5*g*(X+4)/3),(3,-10*g),(1+X,-5*g)]),('4.4.1',[(0,W/2),(R(9,5),W/2),(R(9,10),-W)]),('4.4.2',[(0,R(3,5)),(8,R(7,5)),(R(28,5),-2)]),('4.4.3',[(1,4*m*g),(4,4*m*g),(2,-7*m*g),(6,-m*g)]),('4.4.5',[(0,450),(4,350),(R(3,2),-600),(R(5,2),-200)]),('4.4.6',[(1,100-200/s.sqrt(13)),(3,200/s.sqrt(13)),(1+4/s.sqrt(13),-100)]),('4.4.7 uniform',[(R(1,2),10*g/3),(R(5,4),5*g/3),(R(3,4),-5*g)]),('4.4.7 nonuniform',[(R(1,2),4*g),(R(5,4),g),(R(13,20),-5*g)]),('4.5.7 repositioned',[(d,R(5,4)*m*g),(3*d,R(7,4)*m*g),(2*d,-2*m*g),(R(5,2)*d,-m*g)]),('setA bronze',[(0,350),(6,250),(2,-200),(R(11,4),-400)]),('setA silver',[(0,1000),(10,500),(6,-600),(R(14,9),-900)]),('setA gold',[(0,R(3,5)*W),(X,R(6,5)*W),(R(3,4)*X,-R(4,5)*W),(R(3,5)*X,-W)]),('exam37 unloaded',[(0,R(5,2)*g),(4,R(15,2)*g),(3,-10*g)]),('exam37 loaded',[(0,25*g),(4,25*g),(3,-10*g),(R(7,4),-40*g)]),('exam50 repositioned',[(d,m*g),(4*d,m*g),(2*d,-m*g),(3*d,-m*g)])]
for label,forces in cases:
 ck(label+' force',sum(v for z,v in forces),0);ck(label+' moment',sum(z*v for z,v in forces),0)
# Verify independent lever-arm balances at every tipping threshold.
for label,a,b in [('4.2.8 threshold',1250*4*s.cos(pi/4),2500*2*s.cos(pi/4)),('4.3.3 angle',28*s.cos(pi/3),14),('4.3.6 ratio',R(1,5)*s.Symbol('r'),R(3,5)*s.Symbol('a')+R(1,10)*2*(s.Symbol('r')-3*s.Symbol('a'))),('4.3.7 tension',10*g*s.sqrt(2)*s.cos(pi/4)*2,10*g*2),('4.3.8 breaking threshold',5*g*(2+4)/3,10*g),('4.5.1',4*g*R(1,2),1*g*2),('4.5.2',9*g*R(1,4),3*g*R(3,4)),('4.5.3 tension',40*g/7*R(7,4),20*g*R(1,2)),('4.5.3 load position',10*g*(R(3,2)-R(1,2)),20*g*R(1,2)),('4.5.4',80*g*2,80*g*2),('4.5.5',120*(2-R(8,9)),150*R(8,9)),('4.5.6 first',600*(3-2),300*2),('4.5.6 second',1200*(6-5),600*(5-3)),('4.5.7 original',2*m*g*d,m*g*2*d),('4.5.8 original',R(3,5)*g*R(5,2),R(3,2)*g),('4.5.8 limit',R(3,2)*g*R(4,5),R(3,5)*g*2),('setB bronze left',R(400*10+500,900),5),('setB bronze right',(400*10+500*R(68,5))/900,12),('setB silver',250*4,400*R(5,2)),('setB gold',400*(3-2*1200/(W+800)),W*1200/(W+800)),('exam24',W/3*3*l/4,W*l/2*s.cos(pi/3)),('exam28',100*(10-7),50*6),('exam31 tension',m*g/3*3*l/4,m*g*l/4),('exam41 moment',4000*10,5000*R(5,2)+27500),('exam50 tipping',m*g*(4*d-2*d),m*g*2*d)]:ck(label,a,b)
near('exam41 minimum',R(27500,15),1830,5);near('exam41 maximum',R(27500,6),4580,5)
args.output.write_text(json.dumps(checks,indent=2)+'\n');print(len(checks),'independent checks passed')
