#!/usr/bin/env python3
"""Exact independent checks for Pure Year 1 chapter 7 practice working.

Requires SymPy in an authoring environment. Checks exact rational identities,
division reconstruction, factors, proof identities and finite exhaustions.
"""
import sympy as s,json
from pathlib import Path
x,n,k=s.symbols('x n k',real=True);checks=[]
def E(expr):return s.sympify(expr,locals={'x':x,'n':n,'k':k})
def eq(label,a,b):
 a=E(a);b=E(b);ok=s.simplify(a-b)==0;checks.append({'case':label,'actual':str(a),'expected':str(b),'passed':ok});assert ok,label
fractions=[('(6*x**4+8*x**3-4*x*x)/(2*x)','3*x**3+4*x*x-2*x'),('(12*x-24*x*x+9*x**3)/(3*x)','4-8*x+3*x*x'),('(8*x**6-4*x**3+2*x**4)/(-2*x*x)','-4*x**4+2*x-x*x'),('(x*x-9)/(x-3)','x+3'),('(x*x-3*x+2)/(x-2)','x-1'),('(2*x*x+5*x-3)/(x+3)','2*x-1'),('(2*x*x-3*x-2)/(x*x+x-6)','(2*x+1)/(x+3)'),('(3*x*x+x-2)/(2*x*x+5*x+3)','(3*x-2)/(2*x+3)'),('(6*x*x+11*x-10)/(2*x*x-3*x-20)','(3*x-2)/(x-4)'),('(15*x*x-16*x-15)/(3*x*x-5*x)','5+3/x'),('(x*x-2*x-15)/(x*x+2*x-3)','(x-5)/(x-1)'),('(4*x*x+8*x-5)/(6*x*x-7*x+2)','(2*x+5)/(3*x-2)'),('(6*x**3-2*x*x-4*x)/(2*x*x-7*x+5)','2*x*(3*x+2)/(2*x-5)')]
for i,(a,b) in enumerate(fractions):eq('7.1 identity '+str(i+1),a,b)
divs=[('2*x**3-5*x*x+8*x-5','x-1','2*x*x-3*x+5',0),('3*x**3+8*x*x+3*x-2','x+2','3*x*x+2*x-1',0),('2*x**3+x*x-17*x-12','x-3','2*x*x+7*x+4',0),('4*x**3+13*x*x-11*x+4','x+4','4*x*x-3*x+1',0),('3*x**4+8*x**3-x*x-13*x-6','x+2','3*x**3+2*x*x-5*x-3',0),('4*x**4-8*x**3+x*x-x-2','2*x+1','2*x**3-5*x*x+3*x-2',0),('9*x**4-3*x**3-17*x*x+13*x-2','3*x-2','3*x**3+x*x-5*x+1',0),('4*x**4-12*x**3-5*x*x+15*x+9','2*x-3','2*x**3-3*x*x-7*x-3',0),('2*x**3+6*x*x-4','x+1','2*x*x+4*x-4',0),('3*x**3+7*x*x+18','x+3','3*x*x-2*x+6',0),('4*x**3-11*x-10','x-2','4*x*x+8*x+5',0),('2*x**3+7*x*x+75','x+5','2*x*x-3*x+15',0),('2*x**3+3*x*x-4*x+15','x+3','2*x*x-3*x+5',0),('3*x**3+10*x*x-8*x-5','x-2','3*x*x+16*x+24',43),('10*x**3-29*x*x+4*x+15','x-1','10*x*x-19*x-15',0),('x**3-9*x*x+2*x+48','x-4','x*x-5*x-18',-24),('2*x**3-15*x*x+32*x+20','2*x+1','x*x-8*x+20',0)]
for i,(f,d,q,r) in enumerate(divs):eq('division reconstruction '+str(i+1),f,E(d)*E(q)+r)
for label,f,r,expected in [('7.2/4a','x**3+3*x*x+5*x-8',-4,-44),('7.2/4b','2*x**3-5*x*x+12*x-20',3,25),('7.2/4c','3*x**3+2*x*x-40*x+45',-5,-80),('7.2/5','-15*x**3+26*x*x-13*x+5',s.Rational(2,5),3),('7.2/6a','6*x**3-13*x*x-13*x+30',-3,-210),('7.3/1a','2*x**3+7*x*x-5',-1,0),('7.3/1b','x**3+4*x*x+3*x-2',-2,0),('7.3/1c','2*x**3-3*x*x-7*x-6',3,0),('7.3/1d','x**4-3*x**3-15*x-4',4,0)]:eq(label,E(f).subs(x,r),expected)
factors=[('6*x**3-13*x*x-13*x+30','(x-2)*(2*x+3)*(3*x-5)'),('10*x**3-29*x*x+4*x+15','(x-1)*(2*x-5)*(5*x+3)'),('2*x**3+x*x-13*x+6','(x-2)*(x+3)*(2*x-1)'),('2*x**3+17*x*x+38*x+15','(x+3)*(x+5)*(2*x+1)'),('6*x**3-x*x-11*x+6','(x-1)*(3*x-2)*(2*x+3)'),('15*x**3+61*x*x-2*x-24','(x+4)*(5*x-3)*(3*x+2)'),('x**3+2*x*x-21*x+18','(x-1)*(x-3)*(x+6)'),('2*x**3+13*x*x+13*x-10','(x+2)*(x+5)*(2*x-1)'),('3*x**3+2*x*x-41*x-60','(x+3)*(x-4)*(3*x+5)'),('2*x**3-11*x*x+5*x+18','(x-2)*(x+1)*(2*x-9)'),('2*x**3-3*x*x-39*x+20','(x-5)*(x+4)*(2*x-1)'),('6*x**3+37*x*x+50*x-21','(x+3)*(2*x+7)*(3*x-1)'),('6*x**3-17*x*x-15*x+36','(x-3)*(2*x+3)*(3*x-4)'),('9*x**3+24*x*x-44*x+16','(x+4)*(3*x-2)**2'),('2*x**3-3*x*x-5*x+6','(x-1)*(x-2)*(2*x+3)'),('x**3+2*x*x-19*x-20','(x+1)*(x-4)*(x+5)'),('25*x**3+55*x*x-56*x+12','(x+3)*(5*x-2)**2'),('x**3-9*x*x+2*x+48','(x+2)*(x-3)*(x-8)'),('9*x**3-6*x*x-20*x-8','(x-2)*(3*x+2)**2'),('x**3-x*x-17*x-15','(x+1)*(x+3)*(x-5)'),('2*x**3-x*x-13*x-6','(x+2)*(x-3)*(2*x+1)'),('x**3+9*x*x+8*x-60','(x-2)*(x+5)*(x+6)'),('6*x**3+5*x*x-3*x-2','(x+1)*(2*x+1)*(3*x-2)'),('4*x**3-16*x*x-35*x+147','(x+3)*(2*x-7)**2'),('2*x**3+5*x*x-4*x-3','(x-1)*(2*x+1)*(x+3)'),('2*x**3-7*x*x-24*x+45','(x-5)*(2*x-3)*(x+3)'),('x**3-2*x*x+x+18','(x+2)*(x*x-4*x+9)')]
for i,(a,b) in enumerate(factors):eq('factorisation '+str(i+1),a,b)
for i,(a,b) in enumerate([('(x-4)*(x+6)*(2*x+3)','2*x**3+7*x*x-42*x-72'),('(x+5)**2-4*x-9','(x+3)**2+7'),('x*x-6*x+10','(x-3)**2+1'),('(2*n+3)**2-(2*n+1)**2','8*(n+1)'),('(2*n+1)**3-(2*n+1)**2','2*(4*n**3+4*n*n+n)'),('(k-3)**2-4*(3-2*k)','(k+3)*(k-1)'),('(1+2*x)**2-(1+4*x*x)','4*x'),('((2*n-1)**2+(2*n+1)**2)/2','4*n*n+1'),('x**3-2*x*x+x','x*(x-1)**2')]):eq('proof identity '+str(i+1),a,b)
for n0 in range(5,11):
 prime=n0*n0+n0+17;assert s.isprime(prime);checks.append({'case':'7.5/1 primality n='+str(n0),'value':prime,'passed':True})
for n0 in range(1,7):
 assert (2*n0+1)**2>2**(n0+1);checks.append({'case':'7.5/6 exhaustion n='+str(n0),'passed':True})
for n0 in range(2,8):
 assert (n0*n0+2)%4!=0;checks.append({'case':'7.5/9 exhaustion n='+str(n0),'passed':True})
for n0,expected in [(4,-24),(5,-42),(6,-48),(7,-36)]:eq('setA bronze n='+str(n0),n0**3-9*n0*n0+2*n0+48,expected)
eq('7.4/2 Pythagoras',18**2+6**2+2**2+6**2,16**2+12**2)
eq('exam57 double root included',E('4*x**3-16*x*x-35*x+147').subs(x,s.Rational(7,2)),0)
assert round(float(s.log(s.Rational(3,2))/s.log(5)),2)==0.25;checks.append({'case':'exam75 logarithmic root rounding','passed':True})
import argparse
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args()
args.output.write_text(json.dumps(checks,indent=2));print(len(checks),'exact mathematical checks passed')
