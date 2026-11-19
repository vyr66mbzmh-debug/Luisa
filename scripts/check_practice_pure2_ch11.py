#!/usr/bin/env python3
"""Independent finite-difference, quadrature, model and geometry checks.
Verification dependencies: SymPy and mpmath (not runtime dependencies).
"""
import json
import sympy as s
import mpmath as mp
mp.mp.dps = 45
x = s.Symbol('x', positive=True)
CASES = [['antiderivative', 'exp(x) + 2*sin(x)', 'exp(x) - 2*cos(x)'],
 ['antiderivative', '4*cos(x) - 3/x**2', '4*sin(x) + 3/x'],
 ['antiderivative', '-2*exp(x) + 5/x', '-2*exp(x) + 5*log(x)'],
 ['antiderivative', 'sqrt(x) + 3*sin(x)/4', '2*x**(3/2)/3 - 3*cos(x)/4'],
 ['antiderivative', '11*x**2 + exp(x)/2 - 6/x', '11*x**3/3 + exp(x)/2 - 6*log(x)'],
 ['antiderivative', '3*cos(x) - 1/sqrt(x)', '-2*sqrt(x) + 3*sin(x)'],
 ['antiderivative', 'sin(x)**(-2)', '-cot(x)'],
 ['antiderivative', 'sin(x)/cos(x)**2', 'sec(x)'],
 ['antiderivative', 'cos(x)/sin(x)**2', '-csc(x)'],
 ['antiderivative', '4/cos(x)**2', '4*tan(x)'],
 ['antiderivative', '4/(1 - cos(x)**2)', '-4*cot(x)'],
 ['antiderivative', '8*cos(x)/(cos(x)**2 - 1)', '8*csc(x)'],
 ['antiderivative', '(tan(x) + sec(x))*sec(x)', 'tan(x) + sec(x)'],
 ['antiderivative', '(7*x**2 - 5)/x', '7*x**2/2 - 5*log(x)'],
 ['antiderivative', '(3*exp(x)*sin(x)**2 - 5)*csc(x)**2', '3*exp(x) + 5*cot(x)'],
 ['antiderivative', '(x**2 - x + 1)/x', 'x**2/2 - x + log(x)'],
 ['definite', 'exp(x)', 'exp(x)', 'log(5)', 'log(20)'],
 ['definite', '(1 - 3*x**3)/x', '-x**3 + log(x)', '2', '5'],
 ['definite', '4*exp(x) + sin(x)/cos(x)**2', '4*exp(x) + sec(x)', '0', 'pi/3'],
 ['definite', '(-cos(x)*tan(x) + 4)*sec(x)**2', '4*tan(x) - sec(x)', '0', 'pi/4'],
 ['definite', 'exp(2*x) + exp(x)', 'exp(2*x)/2 + exp(x)', 'log(2)', 'log(6)'],
 ['definite', '(x + 1)/x', 'x + log(x)', '4', '9'],
 ['definite',
  '(-3*exp(x)*cos(x)**2 + cot(x)**2 - 1)*sec(x)**2',
  '-3*exp(x) - tan(x) - cot(x)',
  'pi/6',
  'pi/3'],
 ['antiderivative', '6*exp(3*x)', '2*exp(3*x)'],
 ['antiderivative', 'cos(3*x + 2)', 'sin(3*x + 2)/3'],
 ['antiderivative', '(4*x + 1)**5', '(4*x + 1)**6/24'],
 ['antiderivative', 'cot(4*x)*csc(4*x)', '-csc(4*x)/4'],
 ['antiderivative', 'sec(8*x - 1)**2', 'tan(8*x - 1)/8'],
 ['antiderivative', 'csc(5*x - 1)**2', '-cot(5*x - 1)/5'],
 ['antiderivative', '5/(2*x - 3)', '5*log(2*x - 3)/2'],
 ['antiderivative', '11*exp(4 - x)', '-11*exp(4 - x)'],
 ['antiderivative', '-(4*x - 3)**2 + (4*x - 3)**(-2)', '-(4*x - 3)**3/12 - 1/(16*x - 12)'],
 ['antiderivative', '(exp(5*x)*cos(3*x)**2/2 - 2)*sec(3*x)**2', 'exp(5*x)/10 - 2*tan(3*x)/3'],
 ['antiderivative', '(exp(2*x) - exp(-2*x))**2', '-2*x + exp(4*x)/4 - exp(-4*x)/4'],
 ['antiderivative', '(5 - 3*cos(2*x))/sin(2*x)**2', '-5*cot(2*x)/2 + 3*csc(2*x)/2'],
 ['definite', '4/(6 - 4*x)', '-log(6 - 4*x)', '-2', '0'],
 ['definite', '(exp(x) - 4)**2', '16*x + exp(2*x)/2 - 8*exp(x)', '0', 'log(4)'],
 ['definite', 'sin(x)**(-2)', '-cot(x)', '5*pi/8', '3*pi/4'],
 ['definite', '(exp(x) + 2)**2', '4*x + exp(2*x)/2 + 4*exp(x)', 'log(2)', 'log(8)'],
 ['antiderivative', 'sin(x)**2', 'x/2 - sin(2*x)/4'],
 ['antiderivative', '3*cot(x)**2', '-3*x - 3*cot(x)'],
 ['antiderivative', '(cos(x) + 1)**2', '3*x/2 + 2*sin(x) + sin(2*x)/4'],
 ['antiderivative', 'sin(x)**2/cos(x)**2', '-x + tan(x)'],
 ['definite', 'cos(2*x)/sin(x)**2', '-2*x - cot(x)', 'pi/6', 'pi/4'],
 ['definite', '(sin(x) - csc(x))**2', '-3*x/2 - sin(2*x)/4 - cot(x)', 'pi/4', '3*pi/4'],
 ['definite', '(1 - cos(x))**2/sin(x)**2', '-x - 2*cot(x) + 2*csc(x)', 'pi/3', '2*pi/3'],
 ['definite', '(-tan(x) + sec(x))**2', '-x + 2*tan(x) - 2*sec(x)', '0', 'pi/4'],
 ['antiderivative', '4*cos(2*x)*cos(5*x)', '2*sin(3*x)/3 + 2*sin(7*x)/7'],
 ['definite', 'cos(x)**2', 'x/2 + sin(2*x)/4', 'pi/6', 'pi/2'],
 ['definite', 'tan(2*x)**2', '-x + tan(2*x)/2', 'pi/12', 'pi/6'],
 ['antiderivative', '3*sin(6*x)*cos(x)', '-3*cos(5*x)/10 - 3*cos(7*x)/14'],
 ['antiderivative', '6*x*sqrt(x**2 - 7)', '2*(x**2 - 7)**(3/2)'],
 ['antiderivative', '5*exp(cos(2*x))*sin(2*x)', '-5*exp(cos(2*x))/2'],
 ['antiderivative', '(6*x**2 + 8)*(4*x**3 + 16*x - 5)**(3/2)', '(4*x**3 + 16*x - 5)**(5/2)/5'],
 ['antiderivative', 'sqrt(tan(x) + 1)*sec(x)**2', '2*(tan(x) + 1)**(3/2)/3'],
 ['antiderivative', 'exp(cot(3*x))*csc(3*x)**2', '-exp(cot(3*x))/3'],
 ['antiderivative', 'sin(5*x)*cos(5*x)**4', '-cos(5*x)**5/25'],
 ['antiderivative', '4*x/(2 - x**2)', '-2*log(2 - x**2)'],
 ['antiderivative', 'sin(x)/(4 - 3*cos(x))', 'log(4 - 3*cos(x))/3'],
 ['antiderivative', '(6*x**2 - 9)/(-2*x**3 + 9*x + 14)', '-log(-2*x**3 + 9*x + 14)'],
 ['antiderivative', 'sin(2*x)/cos(x)**2', '-2*log(cos(x))'],
 ['antiderivative', 'sin(x)*cos(x)/(8 - 2*cos(2*x))', 'log(4 - cos(2*x))/8'],
 ['antiderivative', 'exp(-3*x)/(1 + exp(-3*x))', '-log(1 + exp(-3*x))/3'],
 ['definite', 'sin(4*x)**2*cos(4*x)', 'sin(4*x)**3/12', '3*pi/8', 'pi/2'],
 ['definite', 'tan(3*x)', '-log(cos(3*x))/3', '0', 'pi/9'],
 ['definite', '6*exp(3*x)/(exp(3*x) + 1)', '2*log(exp(3*x) + 1)', 'log(2)', 'log(3)'],
 ['definite', 'exp(csc(3*x))*cot(3*x)*csc(3*x)', '-exp(csc(3*x))/3', 'pi/6', 'pi/4'],
 ['definite', '(cot(x) + 1)**3*csc(x)**2', '-(cot(x) + 1)**4/4', 'pi/6', 'pi/4'],
 ['antiderivative', 'sin(x)**5', '-cos(x)**5/5 + 2*cos(x)**3/3 - cos(x)'],
 ['definite', '(x + 1)*sqrt(2*x**2 + 4*x)', '(2*x**2 + 4*x)**(3/2)/6', '0', '4'],
 ['definite', 'exp(cos(4*x))*sin(4*x)', '-exp(cos(4*x))/4', '0', 'pi/8'],
 ['definite', 'sec(x)**2/(3 - tan(x))**4', '1/(3*(3 - tan(x))**3)', '0', 'pi/4'],
 ['antiderivative', 'x*(x - 8)**4', '(x - 8)**6/6 + 8*(x - 8)**5/5'],
 ['antiderivative', '(cos(x) + 1)**5*sin(x)*cos(x)', '-(cos(x) + 1)**7/7 + (cos(x) + 1)**6/6'],
 ['antiderivative',
  'sqrt(cot(x) + 2)*cot(x)*csc(x)**2',
  '-2*(cot(x) + 2)**(5/2)/5 + 4*(cot(x) + 2)**(3/2)/3'],
 ['antiderivative', 'x*cos(x)', 'x*sin(x) + cos(x)'],
 ['antiderivative', 'x*sec(x)**2', 'x*tan(x) + log(cos(x))'],
 ['antiderivative', 'x*exp(2*x)', 'x*exp(2*x)/2 - exp(2*x)/4'],
 ['antiderivative', 'x*csc(4*x)**2', '-x*cot(4*x)/4 + log(sin(4*x))/16'],
 ['antiderivative', 'x*exp(-4*x)', '-x*exp(-4*x)/4 - exp(-4*x)/16'],
 ['antiderivative', 'x*sin(5*x)', '-x*cos(5*x)/5 + sin(5*x)/25'],
 ['antiderivative', 'x*log(x)', 'x**2*log(x)/2 - x**2/4'],
 ['antiderivative', 'x**3*log(x)', 'x**4*log(x)/4 - x**4/16'],
 ['antiderivative', 'log(x)', 'x*log(x) - x'],
 ['antiderivative', 'x**2*sin(2*x)', '-x**2*cos(2*x)/2 + x*sin(2*x)/2 + cos(2*x)/4'],
 ['antiderivative', 'x**2*exp(-3*x)', '(-9*x**2 - 6*x - 2)*exp(-3*x)/27'],
 ['antiderivative', '2*x**2*(x + 1)**3', 'x**2*(x + 1)**4/2 - x*(x + 1)**5/5 + (x + 1)**6/30'],
 ['antiderivative', 'x*sin(x)', '-x*cos(x) + sin(x)'],
 ['definite', 'x*sin(x)', '-x*cos(x) + sin(x)', '0', 'pi/4'],
 ['antiderivative', 'x*sqrt(6 - x)', '-2*x*(6 - x)**(3/2)/3 - 4*(6 - x)**(5/2)/15'],
 ['definite', 'x*sqrt(6 - x)', '-2*x*(6 - x)**(3/2)/3 - 4*(6 - x)**(5/2)/15', '2', '5'],
 ['antiderivative', 'x*csc(x)**2', '-x*cot(x) + log(sin(x))'],
 ['definite', 'x*csc(x)**2', '-x*cot(x) + log(sin(x))', 'pi/4', '3*pi/4'],
 ['antiderivative', 'x*sec(2*x)**2', 'x*tan(2*x)/2 + log(cos(2*x))/4'],
 ['definite', 'x*sec(2*x)**2', 'x*tan(2*x)/2 + log(cos(2*x))/4', '0', 'pi/6'],
 ['definite', 'x**2*cos(4*x)', 'x**2*sin(4*x)/4 + x*cos(4*x)/8 - sin(4*x)/32', '0', 'pi/4'],
 ['definite', 'x**3*exp(-x)', '(-x**3 - 3*x**2 - 6*x - 6)*exp(-x)', '0', '3'],
 ['antiderivative', '6*x*log(4*x)', '3*x**2*log(4*x) - 3*x**2/2'],
 ['definite', '6*x*log(4*x)', '3*x**2*log(4*x) - 3*x**2/2', '1/2', '2'],
 ['definite', 'x**2*exp(2*x)', '(2*x**2 - 2*x + 1)*exp(2*x)/4', '1', '2'],
 ['antiderivative', 'x*sin(pi*x)', '-x*cos(pi*x)/pi + sin(pi*x)/pi**2'],
 ['definite',
  'x**2*cos(pi*x)',
  'x**2*sin(pi*x)/pi + 2*x*cos(pi*x)/pi**2 - 2*sin(pi*x)/pi**3',
  '3/2',
  '5/2'],
 ['definite', '2*x**2*cot(x)*csc(x)**2', '-x**2*csc(x)**2 - 2*x*cot(x) + 2*log(sin(x))', 'pi/4', 'pi/2'],
 ['antiderivative', 'x*cos(2*x)', 'x*sin(2*x)/2 + cos(2*x)/4'],
 ['antiderivative', 'x*sin(x)**2', 'x**2/4 - x*sin(2*x)/4 - cos(2*x)/8'],
 ['antiderivative', '(8*x - 4)/((x - 4)*(x + 2))', '14*log(x - 4)/3 + 10*log(x + 2)/3'],
 ['partial', '(4*x + 17)/((x + 2)*(x + 5))', '1/(x + 5) + 3/(x + 2)'],
 ['antiderivative', '(4*x + 17)/((x + 2)*(x + 5))', '3*log(x + 2) + log(x + 5)'],
 ['partial', '(7*x + 6)/((2 - x)*(x + 3))', '-3/(x + 3) - 4/(x - 2)'],
 ['antiderivative', '(7*x + 6)/((2 - x)*(x + 3))', '-4*log(x - 2) - 3*log(x + 3)'],
 ['partial', '(x + 17)/((x - 1)*(x + 2))', '-5/(x + 2) + 6/(x - 1)'],
 ['antiderivative', '(x + 17)/((x - 1)*(x + 2))', '6*log(x - 1) - 5*log(x + 2)'],
 ['partial', '6/((x - 4)*(2*x - 1))', '-12/(7*(2*x - 1)) + 6/(7*(x - 4))'],
 ['antiderivative', '6/((x - 4)*(2*x - 1))', '6*log(x - 4)/7 - 6*log(2*x - 1)/7'],
 ['partial', '(14 - 2*x**2)/((x + 4)*(2*x - 1))', '-1 + 3/(2*x - 1) + 2/(x + 4)'],
 ['antiderivative', '(14 - 2*x**2)/((x + 4)*(2*x - 1))', '-x + 2*log(x + 4) + 3*log(2*x - 1)/2'],
 ['partial', '(16*x**2 - 37*x + 17)/((4 - x)*(2*x - 3)**2)', '2/(2*x - 3) - 1/(2*x - 3)**2 - 5/(x - 4)'],
 ['antiderivative',
  '(16*x**2 - 37*x + 17)/((4 - x)*(2*x - 3)**2)',
  '-5*log(4 - x) + log(2*x - 3) + 1/(4*x - 6)'],
 ['definite', '(3*x + 15)/((x - 1)*(x + 2))', '6*log(x - 1) - 3*log(x + 2)', '2', '3'],
 ['definite', '(2*x**2 - 5*x + 5)/(2*x**2 - 5*x + 2)', 'x + log(x - 2) - log(2*x - 1)', '3', '5'],
 ['definite', '(12*x + 6)/((x + 3)*(2*x + 1)**2)', '-6*log(x + 3)/5 + 6*log(2*x + 1)/5', '1', '2'],
 ['definite', '(x**2 + 4)/(x**2 - 1)', 'x + 5*log(x - 1)/2 - 5*log(x + 1)/2', '2', '4'],
 ['definite', '4/(2*x + 1)**2', '-2/(2*x + 1)', '0', '2'],
 ['definite', 'x/pi + 2*cos(x/2) - 1', 'x**2/(2*pi) - x + 4*sin(x/2)', '0', 'pi'],
 ['definite', '-sin(x) - cos(2*x) + 1', 'x - sin(2*x)/2 + cos(x)', 'pi/6', '5*pi/6'],
 ['definite', '-x**3 + 2*x**2', '-x**4/4 + 2*x**3/3', '0', '2'],
 ['definite', '-x**2/10 + x + exp(-4*x)', '-x**3/30 + x**2/2 - exp(-4*x)/4', '0', '1'],
 ['definite', 'x**2*cos(x)', 'x**2*sin(x) + 2*x*cos(x) - 2*sin(x)', '0', 'pi/2'],
 ['definite', 'x**2*log(x)/4 + 1', 'x**3*log(x)/12 - x**3/36 + x', '1', '2'],
 ['definite', '-4*tan(x)**2 + 6*sec(x)**2', '4*x + 2*tan(x)', '0', 'pi/4'],
 ['antiderivative', 'x**3*log(x**2 + 1)', '-x**4/8 + x**2/4 + (x**4 - 1)*log(x**2 + 1)/4'],
 ['definite', '3*x**2*exp(-2*x)', '(-3*x**2/2 - 3*x/2 - 3/4)*exp(-2*x)', '0', '3']]
checks = 0
def check(ok, label):
    global checks
    assert ok, label
    checks += 1
def expr(text): return s.sympify(text, locals={'x':x})
def fn(expression):return s.lambdify(x,expression,modules=[{'log':lambda v:mp.log(abs(v))},'mpmath'])
def close(a,b,rtol=mp.mpf('1e-12')):return abs(a-b)<rtol*(1+abs(a)+abs(b))
for kind, ftext, Ftext, *bounds in CASES:
    f,F=fn(expr(ftext)),fn(expr(Ftext))
    points=0
    for text in ['.2','.7','1.1','1.7','2.3','3.9','4.7','6.2','9.3']:
        z=mp.mpf(text);h=mp.mpf('1e-9')
        try:
            target=f(z)
            if abs(mp.im(target))>mp.mpf('1e-35'): continue
            actual=F(z) if kind=='partial' else (F(z+h)-F(z-h))/(2*h)
            check(close(actual,target),(kind,ftext,Ftext,z,actual,target))
            points+=1
            if points==3:break
        except (ValueError,ZeroDivisionError):continue
    check(points==3,('three real-domain probes',ftext))
    if kind=='definite':
        a,b=[mp.mpf(str(s.N(expr(v),42))) for v in bounds]
        numerical=mp.quad(f,[a,(a+b)/2,b])
        check(close(numerical,F(b)-F(a)),('independent quadrature',ftext,bounds))
# Manual substitutions and other antiderivatives not emitted by the authoring helpers.
manual=[
 ('sqrt(x**2+1)/x','sqrt(x**2+1)+log((sqrt(x**2+1)-1)/(sqrt(x**2+1)+1))/2'),
 ('2*x*(x+2)**4','(x+2)**6/3-4*(x+2)**5/5'),
 ('x*sqrt(4*x-1)','(4*x-1)**(s.Rational(5,2))/40+(4*x-1)**(s.Rational(3,2))/24'),
 ('4/(sqrt(x)*(sqrt(x)-9))','8*log(sqrt(x)-9)'),
 ('sin(x)/cos(x)**3','1/(2*cos(x)**2)'),
 ('sin(2*x)/(1+sin(x))','2*sin(x)-2*log(1+sin(x))'),
 ('x**3*sqrt(1+x*x)','(1+x*x)**(s.Rational(5,2))/5-(1+x*x)**(s.Rational(3,2))/3'),
 ('1/(1+exp(x))','x-log(1+exp(x))'),
 ('5*x/sqrt(2*x+1)','s.Rational(5,2)*((2*x+1)**(s.Rational(3,2))/3-sqrt(2*x+1))'),
 ('2*sin(2*x)/(1+sin(x))','4*sin(x)-4*log(1+sin(x))'),
 ('x*log(x/2)','x*x*log(x/2)/2-x*x/4'),
 ('x*cos(x)/2','(x*sin(x)+cos(x))/2'),
 ('(x-15)/((2*x+3)*(x-4))','s.Rational(3,2)*log(2*x+3)-log(x-4)'),
 ('exp(5*x)*(1-x)','(6-5*x)*exp(5*x)/25'),
 ('x**3*log(x*x+1)','(x**4-1)*log(x*x+1)/4-x**4/8+x*x/4')]
for ftext,Ftext in manual:
    f=fn(s.sympify(ftext,locals={'x':x,'s':s}));F=fn(s.sympify(Ftext,locals={'x':x,'s':s}))
    for z in [mp.mpf('1.1'),mp.mpf('1.7'),mp.mpf('3.1')]:
        h=mp.mpf('1e-9');check(close((F(z+h)-F(z-h))/(2*h),f(z)),('manual primitive',ftext,z))
# Direct integration independently confirms selected exact areas and corrected keys.
for integrand,a,b,target in [
 (1/(1+s.exp(x)),s.log(2),s.log(6),s.log(s.Rational(9,7))),
 (5*x/s.sqrt(2*x+1),0,4,s.Rational(50,3)),
 (1/s.sin(2*s.pi-x)**2,5*s.pi/8,3*s.pi/4,2-s.sqrt(2)),
 (s.sin(x)**2*s.cos(x)**3,0,s.pi/2,s.Rational(2,15)),
 (2*s.sin(x)*s.cos(x)*(1+s.sin(x))**4,0,s.pi/2,s.Rational(43,5)),
 (s.exp(5*x)*(1-x),0,1,(s.exp(5)-6)/25),
 (s.cot(x)**3,s.pi/4,s.pi/2,(1-s.log(2))/2),
 (s.sin(x)**2,s.Integer(0),s.pi/2,s.pi/4)]:
    a,b,target=[mp.mpf(str(s.N(v,42))) for v in [a,b,target]]
    check(close(mp.quad(fn(integrand),[a,(a+b)/2,b]),target),('exact integral',str(integrand)))
# ODE solutions: differentiate the candidate and compare with the original right side.
C=s.Rational(5,2)
ode_cases=[
 (s.log(s.Rational(3,4)*s.exp(4*x)+C)/3,lambda y:s.exp(4*x-3*y)),
 (s.asin(x/2-s.sin(2*x)/4),lambda y:s.sin(x)**2/s.cos(y)),
 (C*s.exp(2*x**3+3*x*x),lambda y:6*x*y*(x+1)),
 (-s.log(s.Rational(2,3)*s.cos(x)**3+C)/2,lambda y:s.exp(2*y)*s.sin(x)*s.cos(x)**2),
 (3*(x+1)**2/(4*(x+2)),lambda y:y*(x+3)/((x+1)*(x+2))),
 (-s.sqrt(169-x*x),lambda y:-x/y),
 ((2*x-5)*(x+2)**3/5,lambda y:y*(8*x-11)/((2*x-5)*(x+2))),
 ((x*x+x+2)**2/4,lambda y:y*(4*x+2)/(x*x+x+2)),
 ((2*x+100)**s.Rational(3,2),lambda y:3*y**s.Rational(1,3)),
 (800*s.exp(-x*s.log(s.Rational(16,11))/4),lambda y:-s.log(s.Rational(16,11))*y/4),
 (20+55*s.exp(-x*s.log(s.Rational(11,9))/5),lambda y:-s.log(s.Rational(11,9))*(y-20)/5),
 ((100-40*s.exp(-x/300))/3,lambda y:(100-3*y)/900),
 (80000/(1+4*s.exp(-2*x/3)),lambda y:y*(80000-y)/120000),
 (1000+8000*s.exp(-x/5),lambda y:200-y/5)]
for y,rhs in ode_cases:
    for z in [s.Rational(1,4),s.Rational(1,2),s.Rational(3,4)]:
        residual=s.N((s.diff(y,x)-rhs(y)).subs(x,z),35)
        check(abs(complex(residual))<1e-25,('ODE residual',str(y),z))
# Formal implicit curve and impossible initial derivative in 11.10 Q5.
z=1-s.exp(1-x*x)/x**2
check(s.simplify(x*s.diff(z,x)/2-(1+x*x)*(1-z))==0,'formal squared curve satisfies separated equation away from zero')
check(z.subs(x,1)==0 and s.diff(z,x).subs(x,1)==4,'vertical tangent at initial point')
check((1+1**2)*(1-0**2)==2,'original equation incompatible with finite derivative at (1,0)')
# Initial conditions and fitted constants.
for actual,expected in [
 (3*(1+1)**2/(4*(1+2)),1),(-s.sqrt(169-144),-5),
 ((2*3-5)*(3+2)**3/5,25),((2*0+100)**s.Rational(3,2),1000),
 (800*s.exp(-s.log(s.Rational(16,11))),550),(20+55*s.exp(-s.log(s.Rational(11,9))),65),
 ((100-40)/3,20),(80000/(1+4),16000),(1000+8000,9000),
 (75*s.cos(s.pi/2)+25,25)]:check(close(mp.mpf(str(s.N(actual,40))),mp.mpf(expected)),'initial/fitted value')
# Tables: given source rounding remains the data for each trapezium estimate.
for values,h,target in [
 ([0,.375,1,1.125,0],.5,1.25),([1,.6116,.6103,.7435,.9183],.25,.7311375),
 ([1.25,1.038,.933,.9,.929,1.041,1.333],.5,3.06625),
 ([1,1.0872,1.2281,1.4285,1.6931],.25,1.2725875),
 ([0,.2759,.4060,.3361,.2198,.1263,.0669],.5,.698775)]:
    values=[mp.mpf(str(v)) for v in values];T=mp.mpf(str(h))/2*(values[0]+2*sum(values[1:-1])+values[-1]);check(close(T,mp.mpf(str(target))),'table trapezium sum')
# Geometry areas independently in Cartesian or parameter coordinates.
check(s.simplify(s.integrate(4-x*x/9,(x,3*s.sqrt(3),6))+s.sqrt(3)/3-(16-26*s.sqrt(3)/3))==0,'normal bounded region')
check(s.Rational(9,4)-24*s.integrate(s.sin(x)**2*s.cos(x),(x,0,s.pi/6))==s.Rational(5,4),'parametric tangent bounded region')
check(s.simplify(60*s.integrate(s.sin(x)**2,(x,0,s.pi/2))-30-(15*s.pi-30))==0,'ellipse segment area')
check(s.simplify(s.integrate(8*x*s.sin(x),(x,0,s.pi))-8*s.pi)==0,'parametric arch area')
print(json.dumps({'checksPassed':checks,'checksPerformed':checks,'generatedFormulaCases':len(CASES),'manualPrimitiveCases':len(manual),'odeModels':len(ode_cases)}))
