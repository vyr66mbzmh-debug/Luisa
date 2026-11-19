#!/usr/bin/env python3
"""Independent exact vector, distance, geometry and mechanics checks (SymPy)."""
import json
import math
import sympy as s
R=s.Rational
checks=0
def check(ok,label):
    global checks
    assert ok,label
    checks+=1
def eq(a,b,label):check(s.simplify(a-b)==0,label)
def v(a):return s.Matrix(a)
def square(a):return v(a).dot(v(a))
def vector(actual,expected,label):
    for a,b in zip(actual,expected):eq(a,b,label)
# Coordinate displacements and lengths from the source coordinates.
for p,q,d,nsq in [
 ([0,0,0],[4,10,3],[4,10,3],125),([0,0,0],[6,4,-8],[6,4,-8],116),
 ([0,0,0],[-2,-4,15],[-2,-4,15],245),([5,3,-2],[-4,5,4],[-9,2,6],121),
 ([-1,-3,6],[9,-14,4],[10,-11,-2],225),([11,-2,-1],[7,0,4],[-4,2,5],45),
 ([5,2,1],[3,7,-2],[-2,5,-3],38),([2,3,-5],[-1,4,2],[-3,1,7],59),
 ([4,4,-3],[7,-1,0],[3,-5,3],43),([4,4,-3],[-1,1,-6],[-5,-3,-3],43),
 ([7,-1,0],[-1,1,-6],[-8,2,-6],104),([1,2,-3],[1,2,3],[0,0,6],36),
 ([1,2,3],[-2,-2,-3],[-3,-4,-6],61),([1,2,-3],[-2,-2,-3],[-3,-4,0],25),
 ([7,6,3],[4,10,-4],[-3,4,-7],74),([6,11,-5],[3,15,-12],[-3,4,-7],74),
 ([6,11,-5],[7,6,3],[1,-5,8],90),([3,15,-12],[4,10,-4],[1,-5,8],90),
 ([7,4,-1],[11,-2,3],[4,-6,4],68),([-2,-3,8],[6,-15,16],[8,-12,8],272)]:
    vector(v(q)-v(p),d,'source displacement');eq(square(d),nsq,'source distance squared')
k=s.symbols('k',real=True)
for p,q,nsq,roots in [
 ([6,-1,3],[3,5,k],49,[1,5]),([-2,4,8],[0,k,7],9,[2,6]),
 ([2,-5,k],[-2,-1,3],81,[-4,10]),([k,-4,6],[8,-5,-1],75,[3,13]),
 ([4,-4,3],[k,4,4],90,[-1,9]),([8,-6,4],[k,-4,-7],225,[-2,18]),
 ([6,3,-3],[-4,k,0],125,[-1,7])]:
    polynomial=s.expand(square(v(q)-v(p))-nsq)
    check(set(s.solve(polynomial,k))==set(roots),'all distance roots')
    for root in roots:eq(polynomial.subs(k,root),0,'distance root substitution')
# Direction angles, independently via law of cosines rather than authored dot quotient.
for a,b,expected in [
 ([2,-1,-2],[1,0,0],48.2),([2,-1,-2],[0,1,0],109.5),([2,-1,-2],[0,0,1],131.8),
 ([1,-2,-1],[-7,5,1],148.1),([5,2,-1],[-2,-8,3],127.1),
 ([5,-6,12],[1,0,0],69.6),([-2,-8,4],[0,1,0],150.8)]:
    A,B=v(a),v(b);cos=(square(A)+square(B)-square(A-B))/(2*s.sqrt(square(A)*square(B)))
    deg=math.degrees(math.acos(float(cos)));check(round(deg,1)==expected,'law of cosines angle')
# Linear combinations and unit vectors.
vector(v([2,-2,3])+2*v([-4,-5,6]),[-6,-12,15],'m+2n')
vector(-v([2,-2,3])-v([-4,-5,6]),[2,7,-9],'-m-n')
vector(4*v([2,-2,3])-v([-4,-5,6]),3*v([4,-1,2]),'parallel vectors')
vector(v([5,-6,-1])-v([4,1,3]),[1,-7,-4],'BC from AC-AB')
for a in [[-2,5,-3],[1,-7,-4]]:eq(square(v(a)/s.sqrt(square(a))),1,'unit vector magnitude')
# Geometry, using cross products independently of authored scalar-product area formulas.
for a,b,target in [([1,10,-3],[8,3,2],7446),([-3,6,1],[11,7,-2],7955)]:
    eq(square(v(a).cross(v(b))),target,'area squared from determinant')
eq(square(v([-6,12,2]).cross(v([22,14,-4]))),16*7955,'scaled triangle area squared')
eq(square([0,0,6])+square([-3,-4,0]),square([-3,-4,-6]),'right triangle')
check(round(math.degrees(math.atan(6/5)),1)==50.2,'right triangle angle')
AB=116+(k-11)**2;AC=s.Integer(134);BC=85+(k-6)**2
candidates=set(s.solve(AB-AC,k)+s.solve(AB-BC,k)+s.solve(AC-BC,k))
check({z for z in candidates if z.is_integer and z>0}=={s.Integer(13)},'all isosceles possibilities')
for a,b in [([0,0,0],[1,1,0]),([0,0,0],[0,1,1]),([1,1,0],[0,1,1])]:eq(square(v(b)-v(a)),2,'integer equilateral counterexample')
# Symbolic cuboid midpoint proofs, covering both ratios independently.
a,b,c=s.eye(3).columnspace();F=a+b+c;G=b+c
for ratio in [R(4,5),R(1,3)]:
    M=ratio*a;N=a+ratio*b;P=F+ratio*(G-F);Q=G+ratio*(c-G)
    vector((M+P)/2,(N+Q)/2,'common segment midpoint')
    vector((M+P)/2,(a+b+c)/2,'cuboid centre')
# Parallelogram fourth vertex and trapezium distinction.
vector(v([6,-8,4])+v([-7,9,-3])-v([-3,-4,2]),[2,5,-1],'parallelogram D')
vector(v([8,-12,8]),2*v([4,-6,4]),'trapezium parallel pair')
check(v([-9,-7,9]).cross(v([-5,-13,13]))!=s.zeros(3,1),'other pair not parallel')
# Simultaneous component equations.
p,q,r=s.symbols('p q r');sol=s.solve([2*q-3*p-13,4*q+p-5,r-2*q+p],[p,q,r]);check(sol=={p:-3,q:2,r:7},'vector equality solution')
a0,b0,c0=s.symbols('a b c');sol=s.solve([-a0-2*b0,b0*c0+6,3*a0+2*b0-8],[a0,b0,c0]);check(sol==[(4,-2,3)],'second vector equality')
# Resultant forces, accelerations and no-reversal displacement lengths.
for forces,target,mass in [
 ([[-5,3,1],[2,0,-5],[0,-4,3]],[-3,-1,-1],1),
 ([[8,-3,6],[-6,9,4]],[2,6,10],4),
 ([[2,3,-7],[0,2,4]],[2,5,-3],3)]:
    resultant=sum([v(f) for f in forces],s.zeros(3,1));vector(resultant,target,'resultant force');vector(resultant/mass,v(target)/mass,'Newton acceleration')
for accel,time,vsq,dsq in [([-3,6,-1],2,184,184),([5,-11,2],4,2400,9600)]:
    eq(square(time*v(accel)),vsq,'velocity squared');eq(square(R(1,2)*time**2*v(accel)),dsq,'displacement squared')
vector(v([6,-3,5])+v([-4,7,-8])+v([-2,-4,3]),[0,0,0],'equilibrium a=-2 b=3')
# Correct force-magnitude roots versus the incorrect supplied values.
p=s.symbols('p');poly=(p+3)**2+(p+6)**2+(1-p)**2-625
roots=[(-8+s.sqrt(1801))/3,(-8-s.sqrt(1801))/3]
for root in roots:eq(poly.subs(p,root),0,'correct acceleration root')
for root in [-3,-R(7,3)]:eq((poly+625).subs(p,root),25,'printed roots give only 5N')
q=s.symbols('q');poly=(3-q)**2+(q+5)**2+(1-q)**2-36
check(set(s.solve(poly,q))=={-s.Integer(1),R(1,3)},'problem A gold roots')
for root in [-2*s.sqrt(3),2*s.sqrt(3)]:eq(50*root**2,600,'scaled vector p')
for root in [-R(9,2),R(9,2)]:eq(24*root**2,486,'scaled vector t')
print(json.dumps({'checksPassed':checks,'checksPerformed':checks}))
