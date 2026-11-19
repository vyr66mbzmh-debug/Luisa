"""Check displayed derivatives numerically and special cases exactly.

Requires SymPy, its optional ANTLR LaTeX parser and mpmath in the verification
Python environment. These are verification-only dependencies.
"""
import json
from pathlib import Path
import sympy as s
import mpmath as mp
from sympy.parsing.latex import parse_latex
x,y,t=s.symbols('x y t',real=True)
R=s.Rational
n=0
mp.mp.dps=40
rows={r['id'].split('/ch9/')[1]:r for r in json.loads((Path(__file__).resolve().parents[1]/'resources/practice-solutions/pure-year-2/chapter-09.json').read_text())['solutions']}
cases=[('9.1/q1', 0, '6*sin(x)'), ('9.1/q1', 1, '-3*sin(x/2)'), ('9.1/q1', 2, 'sin(5*x)/3'), ('9.1/q1', 3, 'cos(4*x)'), ('9.1/q1', 4, '5*cos(6*x)'), ('9.1/q1', 5, '-cos(7*x)/2'), ('9.1/q2', 0, '4*sin(x) - 3*cos(x)'), ('9.1/q2', 1, '-6*sin(x/4) + sin(2*x)/2 + 4*cos(x)'), ('9.1/q2', 2, '5*x**(3/2) - 6*sin(x/3) - 4/x**2'), ('9.1/q2', 3, '3*cos(x/6) + 8/sqrt(x)'), ('9.2/q1', 0, '6*exp(-3*x)'), ('9.2/q1', 1, '5*exp(2*x) - 7*exp(-x)'), ('9.2/q2', 0, 'log(2*x)'), ('9.2/q2', 1, 'log(x**2)'), ('9.2/q2', 2, 'log(7/x)'), ('9.2/q2', 3, 'log(4*x**3)'), ('9.3/q1', 0, '(4 - 3*x)**3'), ('9.3/q1', 1, 'sqrt(5*x + 6)'), ('9.3/q1', 2, '(2*x**3 + 5)**4'), ('9.3/q1', 3, '(3*x**2 + 7)**(-5)'), ('9.3/q1', 4, '6/sqrt(4 - 5*x)'), ('9.3/q1', 5, '1/(6 - x)'), ('9.3/q1', 6, '(2*x**4 + 3)**(1/3)'), ('9.3/q1', 7, 'sqrt(7*x**3 - 4)'), ('9.3/q2', 0, 'sin(x)**3'), ('9.3/q2', 1, 'log(x**4)'), ('9.3/q2', 2, 'exp(cos(4*x))'), ('9.3/q2', 3, 'log(x)**2'), ('9.3/q2', 4, 'log(cos(x))'), ('9.3/q2', 5, 'sin(exp(-3*x))'), ('9.4/q1', 0, 'x*(4 - 5*x)**3'), ('9.4/q1', 1, '3*x**3*(2*x - 1)**6'), ('9.4/q1', 2, '4*(6*x - 7)**4/x**2'), ('9.4/q1', 3, '8*x**2/(2*x**3 - 4)**3'), ('9.4/q2', 0, 'x**2*cos(2*x)'), ('9.4/q2', 1, 'exp(3*x)*sin(5*x)'), ('9.4/q2', 2, '(2*x**2 + 3)**3*exp(-x)'), ('9.4/q2', 3, '-3*sin(2*x)*cos(4*x)'), ('9.4/q2', 4, 'x**2*log(x)'), ('9.4/q2', 5, 'exp(4*x)*log(cos(3*x))'), ('9.4/q4', 0, '(x**4 - 3*x**2)*exp(-2*x)'), ('9.4/q4', 1, '(-sin(x) + 4*cos(2*x))*exp(3*x)'), ('9.4/q4', 2, '(x**2 - 5*cos(x/2))*log(4*x)'), ('9.4/q5', 0, 'exp(-x)*cos(3*x)'), ('9.4/q5', 1, 'x**4*log(sin(x))'), ('9.5/q1', 0, '(4*x + 3)/(2*x - 9)'), ('9.5/q1', 1, '6*x**2/(3 - 5*x)'), ('9.5/q1', 2, '(1 - 8*x)/(3*x**3 + 2)**2'), ('9.5/q1', 3, '(7*x**2 - 9*x)/sqrt(x**2 + 6)'), ('9.5/q2', 0, '4*x**2/cos(2*x)'), ('9.5/q2', 1, '(x - exp(-x))/log(x)'), ('9.5/q2', 2, 'exp(x)/cos(x)**2'), ('9.5/q2', 3, '(5 - exp(-x))/sin(4*x)'), ('9.6/q1', 0, 'tan(4*x)'), ('9.6/q1', 1, '7*cot(2*x)'), ('9.6/q1', 2, 'cot(x)**5'), ('9.6/q1', 3, '-3*tan(x)**2'), ('9.6/q2', 0, 'csc(6*x)'), ('9.6/q2', 1, '-4*sec(5*x)'), ('9.6/q2', 3, '-2*sec(4*x)**3'), ('9.6/q3', 0, 'x**2*tan(3*x)'), ('9.6/q3', 1, 'exp(sec(x))/(x**2 + 1)'), ('9.6/q3', 3, 'exp(-x)*cot(4*x)'), ('9.6/q3', 4, 'sec(x)**2/log(x)'), ('9.6/q3', 5, '(4*x - 1)**3/cot(x)**2')]
for key,part,source in cases:
    f=s.sympify(source,locals={'x':x})
    tex=rows[key]['steps'][part]['latex'].rsplit('=',1)[1].replace(r'\operatorname{cosec}',r'\csc')
    tex=tex.replace('x '+r'\left', 'x '+r'\cdot\left')
    tex=tex.replace(r'\ln{\left(x \right)}^{2}',r'\ln^{2}(x)')
    g=parse_latex(tex)
    g=g.subs({z:(x if z.name=='x' else s.E) for z in g.free_symbols if z.name in ['x','e']})
    ff=s.lambdify(x,f,'mpmath');gg=s.lambdify(x,g,'mpmath')
    valid=0
    for raw in ['0.13','0.31','0.73','1.17','1.81','2.31','3.07','4.13']:
        point=mp.mpf(raw);h=mp.mpf('1e-8')
        try:
            v=gg(point);f0=ff(point);fp=ff(point+h);fm=ff(point-h)
            if any(abs(mp.im(z))>mp.mpf('1e-20') or not mp.isfinite(z) for z in [v,f0,fp,fm]):continue
            finite=(fp-fm)/(2*h)
            assert abs(v-finite)<mp.mpf('1e-10')*(1+abs(v)),(key,part,point,v,finite)
            n+=1;valid+=1
            if valid==3:break
        except (ValueError,ZeroDivisionError):continue
    assert valid>=1,(key,part,'no real sample')
def eq(a,b):
    global n
    assert s.simplify(s.trigsimp(s.expand_trig(a-b)))==0,(a,b)
    n+=1
def near(a,b,tol=1e-9):
    global n
    assert abs(float(a)-b)<tol,(a,b)
    n+=1
# Independently specified exact derivatives, tangents and stationary values.
for f,d in [(6*s.sin(x)-3*s.cos(2*x),6*s.cos(x)*(1+2*s.sin(x))),((1-s.exp(2*x))**2/s.exp(2*x),2*s.exp(2*x)-2*s.exp(-2*x)),(2*x**4*(2-5*x*x)**3,x**3*(2-5*x*x)**2*(16-100*x*x)),(s.log(s.cot(2*x)),-4/s.sin(4*x)),(s.exp(-x)*s.cos(2*x),s.exp(-x)*(-s.cos(2*x)-2*s.sin(2*x)))]:eq(s.diff(f,x),d)
for v,height in [(s.pi/2,9),(7*s.pi/6,R(-9,2)),(3*s.pi/2,-3),(11*s.pi/6,R(-9,2))]:
 f=6*s.sin(x)-3*s.cos(2*x);eq(f.subs(x,v),height);eq(s.diff(f,x).subs(x,v),0)
# Given point inconsistent with its original equation: no tangent there.
assert 2*6**2-4*6!=3;n+=1
eq(s.diff(2*y*y-4*y,y).subs(y,6),20)
for f,point,m in [(x-s.cos(2*x),s.pi/4,3),(6*s.sin(2*x)-4*s.cos(2*x),s.pi,12),(3*s.sin(x)-4*s.cos(x)+x*x/2,s.pi/2,4+s.pi/2),(4**x,R(-1,2),s.log(2)),(3*s.exp(x)-s.log(x*x),1,3*s.E-2),(4**x+4**(-x),R(1,2),s.log(8)),((2*x-3)**5,2,10),(3/(6-x)**3,4,R(9,16)),(3*s.sin(x)**2-2*s.cos(x)**2,-5*s.pi/6,5*s.sqrt(3)/2),(2**(x**4),-1,-8*s.log(2)),(4*x**3*(1-2*x*x)**4,1,76),((x-s.pi)*s.sin(2*x),3*s.pi/4,-1),((8-2*x)/(4*x+1),R(1,2),R(-34,9)),((x*x-6*x)/s.exp(2*x),1,6/s.E**2),(s.exp(s.tan(x/2)),0,R(1,2))]:eq(s.diff(f,x).subs(x,point),m)
# Parametric derivative ratios and normal coordinates.
for X,Y,parameter,slope in [(1-t*t,t**3+2*t*t,-3,R(5,2)),(2/s.cos(t),4*s.cos(t)**2,s.pi/3,R(-1,2)),((t-2)**2,t*t+4*t,6,2),(-2/s.cos(2*t),2/s.tan(t),-s.pi/6,-s.sqrt(3)/3),(t/(1-t),1/(1+t*t),R(-1,2),R(36,25))]:eq((s.diff(Y,t)/s.diff(X,t)).subs(t,parameter),slope)
# Implicit differentiation checked from F_x + F_y*y' = 0.
for F,d in [(x**4-y**3-3,4*x**3/(3*y*y)),(3*x*x+4*y*y-5*x*x*y-2,(6*x-10*x*y)/(5*x*x-8*y)),(y*(x*x-y*y)-5*y*y,2*x*y/(10*y+3*y*y-x*x)),(s.cos(x)+s.sin(y)**2-1,s.sin(x)/(2*s.sin(y)*s.cos(y))),(x*s.exp(-y)+y*s.exp(2*x)-7,(s.exp(-y)+2*y*s.exp(2*x))/(x*s.exp(-y)-s.exp(2*x))),(s.exp(-3*y)-s.exp(-2*x)-4*x*y,(2*s.exp(-2*x)-4*y)/(4*x+3*s.exp(-3*y)))]:eq(s.diff(F,x)+s.diff(F,y)*d,0)
F=s.cos(2*x)+s.sin(2*y)-1;pt={x:-s.pi/6,y:s.pi/12};eq(F.subs(pt),0);eq((-s.diff(F,x)/s.diff(F,y)).subs(pt),-1)
F=4*x*x+y*y+6*x-8*y-10;eq(F.subs({x:1,y:8}),0);eq((-s.diff(F,x)/s.diff(F,y)).subs({x:1,y:8}),R(-7,4));eq((4*x-7*y+52).subs({x:1,y:8}),0)
# Second derivative signs and factorisations.
for f,d in [(s.exp(-x)*s.cos(2*x),s.exp(-x)*(4*s.sin(2*x)-3*s.cos(2*x))),(8*x*x+3*s.exp(4*x),16+48*s.exp(4*x)),(s.cos(2*x),-4*s.cos(2*x)),(x*(2*x-1)**5,20*(2*x-1)**3*(6*x-1)),(x*(2*x-5)**4,80*(2*x-5)**2*(x-1)),(s.sin(4*x)/s.exp(2*x),-4*s.exp(-2*x)*(3*s.sin(4*x)+4*s.cos(4*x))),(x**3*s.exp(x),s.exp(x)*x*(x*x+6*x+6)),(4*x**3*s.log(x*x),8*x*(3*s.log(x*x)+5)),(x*x*(2-5*x)**5,2*(2-5*x)**3*(525*x*x-120*x+4))]:eq(s.diff(f,x,2),d)
for v,expected in [(R(95,100),R(-961,25)),(R(105,100),R(841,25))]:eq(s.diff(x*(2*x-5)**4,x,2).subs(x,v),expected)
for v in [0,R(1,10),-R(1,10)]:assert float((-4*s.cos(2*x)).subs(x,v))<0;n+=1
for v in [(12+2*s.sqrt(15))/105,(12-2*s.sqrt(15))/105,R(2,5)]:eq(s.diff(x*x*(2-5*x)**5,x,2).subs(x,v),0)
# Rates, exact tangent targets and triangle areas.
eq((s.diff(s.exp(2*x)/x**2,x)*R(-1,2)).subs(x,4),-3*s.exp(8)/64)
near(23500*s.exp(R(-7,4)),4083.68767110946,1e-6);near(-5875*s.exp(R(-5,2)),-482.249366915405,1e-6)
eq(R(1,2)*(1+s.sqrt(3))*(3+s.sqrt(3)),3+2*s.sqrt(3))
for X,Y in [(s.pi/6,s.pi/3),(5*s.pi/6,-s.pi/3)]:eq(s.cos(Y)+s.sin(X),1);eq(s.cos(X)/s.sin(Y),1)
for f,p,der in [(2*x*x+2*x-s.exp(x),0,1),(2**x+4**(-x),-1,-R(15,2)*s.log(2)),((x*x-4*x)*s.exp(-x),1,1/s.E)]:eq(s.diff(f,x).subs(x,p),der)
eq((s.diff(s.cos(2*x)-s.sin(2*x)**2,x,2)).subs(x,-s.pi/2),-4)
eq(R(1,2)*R(31,32)*R(31,4),R(961,256))
eq(R(1,2)*(3+3/s.E**2)*(3/s.E),9*(s.E**2+1)/(2*s.E**3))
print(f'{n} independent displayed-derivative/exact checks passed')
