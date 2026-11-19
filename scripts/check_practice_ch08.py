#!/usr/bin/env python3
"""Independent exact checks for Pure Year 1 chapter 8 practice solutions.

Uses SymPy for polynomial identities and Python integer combinations for a
separate coefficient calculation. Decimal estimates use exact rational inputs.
"""
import sympy as s,json,math
from pathlib import Path
x,y,p,q,k=s.symbols('x y p q k');checks=[]
def E(t):return s.sympify(t,locals={'x':x,'y':y,'p':p,'q':q,'k':k})
def eq(name,a,b):
 a=E(a);b=E(b);ok=s.simplify(a-b)==0;checks.append({'case':name,'passed':ok,'actual':str(a),'expected':str(b)});assert ok,(name,a,b)
def truncated(t,n):return s.Poly(s.expand(E(t)),x).as_expr().series(x,0,n).removeO()
full=[('(3-x)**5','243-405*x+270*x*x-90*x**3+15*x**4-x**5'),('(2*x+y)**4','y**4+8*x*y**3+24*x*x*y*y+32*x**3*y+16*x**4'),('(3*x-2*y)**5','243*x**5-810*x**4*y+1080*x**3*y*y-720*x*x*y**3+240*x*y**4-32*y**5'),('(1-2*x)*(1+3*x)**3','1+7*x+9*x*x-27*x**3-54*x**4'),('(2+3*x)**4','16+96*x+216*x*x+216*x**3+81*x**4'),('(4+k)**3','64+48*k+12*k*k+k**3'),('(4+x*x-x)**3','64-48*x+60*x*x-25*x**3+15*x**4-3*x**5+x**6'),('(1+x)**5','1+5*x+10*x*x+10*x**3+5*x**4+x**5'),('(2+x)**6','64+192*x+240*x*x+160*x**3+60*x**4+12*x**5+x**6'),('(10+x)**4','10000+4000*x+600*x*x+40*x**3+x**4'),('(3-2*x)**4','81-216*x+216*x*x-96*x**3+16*x**4'),('(4+x/2)**5','1024+640*x+160*x*x+20*x**3+5*x**4/4+x**5/32'),('(x-2)**6','64-192*x+240*x*x-160*x**3+60*x**4-12*x**5+x**6'),('(x-2/x)**5','x**5-10*x**3+40*x-80/x+80/x**3-32/x**5'),('(1+3*x)**4','1+12*x+54*x*x+108*x**3+81*x**4')]
for i,(a,b) in enumerate(full):eq('full expansion '+str(i+1),a,b)
truncs=[('(1+x)**10',4,'1+10*x+45*x*x+120*x**3'),('(1+x)**15',4,'1+15*x+105*x*x+455*x**3'),('(2+x)**9',4,'512+2304*x+4608*x*x+5376*x**3'),('(1-x/2)**10',4,'1-5*x+45*x*x/4-15*x**3'),('(2-x/3)**9',4,'512-768*x+512*x*x-1792*x**3/9'),('(3+2*x)**8',4,'6561+34992*x+81648*x*x+108864*x**3'),('(2-3*x)**5',4,'32-240*x+720*x*x-1080*x**3'),('(3-x)**12',3,'531441-2125764*x+3897234*x*x'),('(1-2*x/3)**9',4,'1-6*x+16*x*x-224*x**3/9'),('(2-3*x)**8',4,'256-3072*x+16128*x*x-48384*x**3'),('(3+p*x)**6',3,'729+1458*p*x+1215*p*p*x*x'),('(1-x/5)**9',4,'1-9*x/5+36*x*x/25-84*x**3/125'),('(1-2*x)**6',3,'1-12*x+60*x*x'),('(3+x/4)**8',4,'6561+4374*x+5103*x*x/4+1701*x**3/8'),('(1+x/4)**9',4,'1+9*x/4+9*x*x/4+21*x**3/16'),('(1-3*x)**6',4,'1-18*x+135*x*x-540*x**3'),('(2-x/2)**7',3,'128-224*x+168*x*x'),('(3-x/5)**10',4,'59049-39366*x+59049*x*x/5-52488*x**3/25'),('(2-p*x)**11',3,'2048-11264*p*x+28160*p*p*x*x'),('(1-5*x)**4',3,'1-20*x+150*x*x'),('(1+2*x/5)**6',4,'1+12*x/5+12*x*x/5+32*x**3/25'),('(2-x/15)**10',3,'1024-1024*x/3+256*x*x/5')]
for i,(a,n,b) in enumerate(truncs):eq('truncated expansion '+str(i+1),truncated(a,n),b)
coeffs=[('(5+2*x)**4',3,160),('(2-3*x)**5',3,-1080),('(3-x/2)**4',3,-s.Rational(3,2)),('(1+x)**14',3,364),('(2+x)**10',3,15360),('(5-x)**7',3,-21875),('(3-2*x)**9',4,489888),('(5+3*x)**7',4,354375),('(1/2+8*x)**12',4,7920),('(3-x)*(2+3*x)**6',3,10800),('(1+2*x/3)**6',3,s.Rational(160,27)),('(1+x/2)*(2-3*x)**8',3,-40320),('(3-2*x)**6',4,2160),('(2+3*x)*(1-5*x)**4',2,240),('(1+6*x)*(2-5*x)**4',2,-360),('(3+12*x)*(1+x/3)**5',3,s.Rational(130,9)),('(1+2/x)**2*(1+2*x/5)**6',1,s.Rational(428,25))]
for i,(f,r,v) in enumerate(coeffs):eq('coefficient '+str(i+1),s.expand(E(f)).coeff(x,r),v)
for i,(a,b) in enumerate([('(3+x)*(1-2*x)**6','3-35*x+168*x*x'),('(1+x/2)*(1-3*x)**6','1-35*x/2+126*x*x')]):eq('product truncation '+str(i+1),truncated(a,3),b)
for n,r,v in [(16,9,11440),(12,5,792),(22,10,646646),(18,11,31824),(14,7,3432)]:eq('combination '+str((n,r)),math.comb(n,r),v)
for n,r in [(5,0),(5,1),(5,2),(5,3),(5,4),(5,5),(6,3),(10,2),(100,3)]:eq('factorial independent coefficient '+str((n,r)),math.comb(n,r),s.binomial(n,r))
for expr,r,v in [('(1-x/5)**9',s.Rational(3,40),s.Rational('0.8728165')),('(3+x/4)**8',s.Rational(1,5),s.Rational('7488.531')),('(1+x/4)**9',s.Rational(3,50),s.Rational('1.1433835')),('(3-x/5)**10',s.Rational(1,40),s.Rational('58072.198320'))]:eq('estimate '+expr,truncated(expr,4).subs(x,r),v)
a=s.Rational('58072.198320');actual=s.Rational('2.995')**10;percent=abs(a-actual)*100/actual;assert abs(float(percent)-1.64433508e-7)<1e-15;checks.append({'case':'percentage error','actual':str(s.N(percent,15)),'passed':True})
prob=sum(s.binomial(100,r)*s.Rational(1,50)**r*s.Rational(49,50)**(100-r) for r in range(4));assert round(float(prob),5)==0.85896;checks.append({'case':'exam29 binomial cumulative','actual':str(s.N(prob,15)),'passed':True})
eq('exam51 surd power',(1+s.sqrt(5))**5,176+80*s.sqrt(5));eq('exam51 log factor',176+80*s.sqrt(5),16*(11+5*s.sqrt(5)))
eq('exam61 even sum',(1+3*x)**4+(1-3*x)**4,2+108*x*x+162*x**4);eq('exam61 derivative',s.diff((1+3*x)**4+(1-3*x)**4,x),216*x*(1+3*x*x))
import argparse
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args()
args.output.write_text(json.dumps(checks,indent=2));print(len(checks),'independent exact checks passed')
