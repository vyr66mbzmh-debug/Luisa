#!/usr/bin/env python3
"""Exact independent checks for Pure Year 1 chapter 4 practice solutions.

Run in an authoring environment with SymPy. Checks source-derived equations,
root counts, transformations and the integral independently of display rendering.
The accompanying evidence fingerprints the authored material reviewed.
"""
import sympy as s,json
from pathlib import Path
x=s.Symbol('x',real=True);checks=[]
def eq(label,actual,expected):
 ok=s.simplify(actual-expected)==0;checks.append({'case':label,'actual':str(actual),'expected':str(expected),'passed':ok});assert ok,(label,actual,expected)
def roots(label,expr,expected):
 actual=s.solveset(expr,x,domain=s.S.Reals);ok=actual==s.FiniteSet(*expected);checks.append({'case':label,'actual':str(actual),'expected':str(s.FiniteSet(*expected)),'passed':ok});assert ok,(label,actual)
polys=[('4.1/2a',x**3+2*x**2-3*x,x*(x-1)*(x+3)),('4.1/2b',-x**3-2*x**2+3*x,x*(1-x)*(x+3)),('4.1/2c',6*x**3-3*x**2,3*x**2*(2*x-1)),('4.1/4',x**3+8*x**2+16*x,x*(x+4)**2),('4.1/5',25*x-4*x**3,x*(5-2*x)*(5+2*x)),('4.1/6',s.Rational(1,8)*(x+6)*(x-6)**2,x**3/8-3*x**2/4-9*x/2+27),('4.1/7',(x-1)**2*(x-4),x**3-6*x**2+9*x-4),('4.1/8',3*(x+1)*(x-2)*(x-5),3*x**3-18*x**2+9*x+30),('4.2/3',(x+4)*(x+2)*(x-2)*(x-3),x**4+x**3-16*x**2-4*x+48),('4.2/6',-(x+3)*(x+2)*(x-1)*(x-2),-x**4-2*x**3+7*x**2+8*x-12),('4.2/7',(x+2)**2*(x-3)**2,x**4-2*x**3-11*x**2+12*x+36),('4.5/4',3*(x+1)**2*(x-2),3*x**3-9*x-6),('setA/bronze',(x+2)*(x-1)*(x-3),x**3-2*x**2-5*x+6),('setA/silver',(x+s.Rational(1,2))*(x-2)*(x-5),x**3-s.Rational(13,2)*x**2+s.Rational(13,2)*x+5),('setA/gold',x*(x-4)*(x-2)**2,x**4-8*x**3+20*x**2-16*x),('exam12',(2*x-3)**2*(x+2),4*x**3-4*x**2-15*x+18)]
for label,a,b in polys:eq(label+' expansion',a,b)
roots('4.4/1a',x*(x-4)-x*x*(3-x),[0,1+s.sqrt(5),1-s.sqrt(5)])
roots('4.4/1b',(x*x+x-2)-(x**3+x*x-2*x),[-2,1])
for value in [1+s.sqrt(5),1-s.sqrt(5)]:eq('4.4/1a ordinate',value*(value-4),4-2*value)
roots('4.4/5',2/x-5-(2*x-5),[-1,1])
roots('4.4/6',-4*x*x*(x*x-x-2)-x**3,[0,(3+s.sqrt(137))/8,(3-s.sqrt(137))/8])
roots('4.4/7',1/x+2-(x*x+2),[1])
roots('4.4/9',2/x-(4*x-2),[-s.Rational(1,2),1])
roots('4.4/10',x*x-10*x-15-(10-10*x),[-5,5])
roots('4.4/11b',x*x-9*x+24-(2*x+5),[(11+3*s.sqrt(5))/2,(11-3*s.sqrt(5))/2])
for label,poly,count in [('4.4/3',x**4*(2*x+5)-3,3),('4.4/4a',x*(x+1)*(x-3)**2+1,2),('4.4/4b',x**4*(4*x-9)-7,1),('4.4/8',x*x*(x+3)*(2-x)+4,2)]:
 eq(label+' real intersections',s.Poly(poly,x).count_roots(-s.oo,s.oo),count)
roots('setB/bronze',x*x*(x-2)-3*x,[-1,0,3])
roots('setB/silver',3/(x-3)**2-6/x,[2,s.Rational(9,2)])
roots('setB/gold',4/(x-2)**2-(5-x),[1,4])
for r in [2+s.sqrt(2),2-s.sqrt(2)]:eq('setA/gold height',-2*r*(r-4)*(r-2)**2,8)
eq('exam12 derivative',s.diff((2*x-3)**2*(x+2),x),12*x*x-8*x-15)
roots('exam22 transformed roots',(2*x+1)*(4*x-3)**2,[-s.Rational(1,2),s.Rational(3,4)])
f=36*x-25*x**3
eq('exam49 A',f.subs(x,-1),-11);eq('exam49 B',f.subs(x,1),11);eq('exam49 distance',s.sqrt(2**2+22**2),2*s.sqrt(122))
f=-x**3+2*x*x+15*x
roots('exam72 roots',f,[-3,0,5]);eq('exam72 total area',-s.integrate(f,(x,-3,0))+s.integrate(f,(x,0,5)),s.Rational(863,6))
# Transformation equations and exact intercepts are computed from the source functions.
funcs=[x*x,x**3,1/x]
for i,f in enumerate(funcs):
 for name,g,y0 in [('up1',f+1,[1,1,None][i]),('right2',f.subs(x,x-2),[4,-8,-s.Rational(1,2)][i]),('left3',f.subs(x,x+3),[9,27,s.Rational(1,3)][i]),('down4',f-4,[-4,-4,None][i])]:
  if y0 is not None:eq('4.5/1 '+str(i)+' '+name+' y-intercept',g.subs(x,0),y0)
funcs=[(x-1)**2,x**3+1,1/(x-1)]
expected=[[3,1,-1,1],[3,1,-1,1],[-3,-1,1,-1]]
for i,f in enumerate(funcs):
 for j,g in enumerate([3*f,f.subs(x,x/2),-f,f.subs(x,-x)]):eq('4.6/1 '+str(i)+' '+str(j)+' y-intercept',g.subs(x,0),expected[i][j])
f=x*x*(12-4*x)
eq('4.7/7bi y-intercept',f.subs(x,-2),80);eq('4.7/7bii maximum',f.subs(x,2),16)
f=3*x**3-9*x-6
for x0,y0 in [(-1,0),(0,-6),(1,-12),(2,0)]:eq('4.5/4 source point '+str(x0),f.subs(x,x0),y0)
import argparse
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args()
out=args.output;out.write_text(json.dumps(checks,indent=2));print(len(checks),'exact mathematical checks passed')
