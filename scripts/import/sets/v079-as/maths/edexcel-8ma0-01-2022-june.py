from sympy import Rational as R,diff,expand,factor,log,pi,sqrt,symbols
x=symbols('x')
assert diff(2*x**4-3*sqrt(x)+5*x,x)==8*x**3-3/(2*sqrt(x))+5
assert expand((x+3)*(2*x*x-x+5))==2*x**3+5*x**2+2*x+15
assert 10**2+(-20)**2==500 and 5+R(3,5)*(-20)==-7
assert 17*3**2-35*3-48==0
assert round(2*10**(.5+8*.03))/2==5.5
assert expand((3-2*x/9)**8).coeff(x)==-3888
assert (9*x-x**3).subs(x,sqrt(3))==6*sqrt(3)
assert round(float(2*log(7)),1)==3.9
assert 2*(-2-2)+3*(-2)/2==-11
assert diff(x*x/3-2*sqrt(x)+3,x).subs(x,4)==R(13,6)
assert 25+16-32==9
r=(28.4/(.26*float(pi)))**(1/3)
assert round(r,2)==3.26 and round(.13*float(pi)*r*r+28.4/r)==13
assert 1+R(2,3)==3*(1-R(2,3)**2)
assert expand(x*(x+1)*(x+2))==x**3+3*x*x+2*x
