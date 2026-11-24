from math import isclose,sqrt
initial=(.5*9.8*4**2-19.6)/4
assert isclose(initial-9.8*4,-24.5) and isclose(14.7**2/(2*9.8),11.025)
assert 25*120/2==1500
tension=.4*2.5+1.5
assert tension==2.5 and isclose(tension/(10-2.5),1/3)
assert round(sqrt(4/2.5),2)==1.26
assert 16-1==15 and isclose(16-3*(4/sqrt(3))**2,0,abs_tol=1e-12) and 16*4-4**3==0
