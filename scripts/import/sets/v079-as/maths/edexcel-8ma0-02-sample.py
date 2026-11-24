from math import comb,sqrt,isclose
assert round(sqrt(7600/20-(374/20)**2),2)==5.51
assert 100*(17+45+3)/sum([6,14,17,45,9,5])>67
assert isclose(1-.05-.75,.2) and not isclose(.35*.6,.2)
assert 2.4+1.5*(2.4-.1)<20.6
p=lambda n,a,k:comb(n,k)*a**k*(1-a)**(n-k)
lo=max(k for k in range(21) if sum(p(20,.3,i) for i in range(k+1))<.05)
hi=min(k for k in range(21) if sum(p(20,.3,i) for i in range(k,21))<.05)
assert (lo,hi)==(2,10)
u,a=6,5
assert 2*u+.5*a*2**2==22 and (u+2*a)*4+.5*a*4**2==104
assert 5**2*(5-10)**2/10==62.5
assert isclose((1.5*9.8-12.7)/4,.5) and sqrt(2/.5)==2
