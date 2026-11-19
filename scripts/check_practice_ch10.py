#!/usr/bin/env python3
"""Independent identities, exact values and interval-root checks for Pure 1 ch10.

Uses bisection on monotone trigonometric branches, independently of the inverse
function enumeration used in authoring. SymPy is an optional checking dependency.
"""
import argparse,json,math
from pathlib import Path
import sympy as s
checks=[]
def record(name,ok):
 checks.append({'case':name,'passed':bool(ok)});assert ok,name
def identity(name,a,b):record(name,s.trigsimp(s.cancel((s.sympify(a)-s.sympify(b)).rewrite(s.sin)))==0)
x=s.symbols('x',real=True);sn=s.sin(x);cs=s.cos(x);tn=s.tan(x)
identity('10.3 1a',2*sn**2-(1-cs**2)+cs**2,1)
identity('10.3 1b',6*s.sin(x/2)**2+6*s.cos(x/2)**2,6)
identity('10.3 1c',(1+cs)**2+(1-cs)**2+2*sn**2,4)
identity('10.3 2c',(1-cs**2)/(1-sn**2),tn**2)
identity('10.3 3',(sn**2-cs**2)/(1-sn**2),tn**2-1)
identity('10.3 5b',4*cs**2-5*sn**2,4-9*sn**2)
identity('10.3 6',4*cs**2-3*sn**2-2,7*cs**2-5)
identity('10.3 7',(cs**2-sn**2)/(cs**2-sn*cs),1+tn)
identity('10.4 8a',4*cs**2-3*sn**2-1,7*cs**2-4)
identity('10.6 3a',2*cs**2-sn**2-4*cs+2,(3*cs-1)*(cs-1))
identity('10.6 4a',6*(1-sn)-5*cs**2,(5*sn-1)*(sn-1))
identity('10.6 4b',8-7*cs-6*sn**2,(3*cs-2)*(2*cs-1))
identity('10.6 4c',3*sn-2*cs**2,(2*sn-1)*(sn+2))
identity('10.6 5',2*sn**2-3*cs**2-1,5*sn**2-4)
identity('10.6 6',2*cs**2+sn**2-s.Rational(10,9),cs**2-s.Rational(1,9))
identity('10.6 7',7*sn-2*cs**2-2,(2*sn-1)*(sn+4))
identity('10.6 8',2*cs**2+3*cs-sn**2,3*cs**2+3*cs-1)
identity('10.6 9',-(15*sn**2+8*cs-16),(5*cs-1)*(3*cs-1))
identity('problem B silver',-(4*cs**2+9*sn-6),(4*sn-1)*(sn-2))
identity('problem B gold',5*cs*(cs-1)-3*sn**2,(cs-1)*(8*cs+3))
identity('exam 7',(2*sn**2-1)/cs**2,tn**2-1)
identity('exam 47',6*tn**2-11*tn-10,(3*tn+2)*(2*tn-5))
identity('exam 60',8*cs**2-6*cs-sn**2,(3*cs-1)**2-2)
identity('exam 84',6*x**3+11*x**2-3*x-2,(x+2)*(2*x-1)*(3*x+1))
identity('exam 85b',8*sn-3*cs**2,(3*sn-1)*(sn+3))
identity('10.2 parallelogram rationalisation',100/(5-2*s.sqrt(3)),100*(5+2*s.sqrt(3))/13)
record('10.3 2b necessary absolute value',s.sqrt(1-s.sin(2*s.pi/3)**2)==abs(s.cos(2*s.pi/3)) and s.sqrt(1-s.sin(2*s.pi/3)**2)!=s.cos(2*s.pi/3))
record('10.3 4 triangle ratios',s.Rational(3,8)**2+(-s.sqrt(55)/8)**2==1)
record('10.3 8 cosine rule',(49+144-81)/168==2/3)
record('10.3 9 obtuse cosine',(-s.sqrt(31)/9)**2+(5*s.sqrt(2)/9)**2==1)
for fn,angle,expected in [('sin',150,s.Rational(1,2)),('sin',-45,-1/s.sqrt(2)),('sin',315,-1/s.sqrt(2)),('sin',240,-s.sqrt(3)/2),('cos',150,-s.sqrt(3)/2),('cos',-60,s.Rational(1,2)),('cos',-135,-1/s.sqrt(2)),('cos',120,-s.Rational(1,2)),('tan',225,1),('tan',-150,s.sqrt(3)/3),('tan',405,1),('tan',-120,s.sqrt(3))]:
 record('10.2 exact '+fn+str(angle),s.simplify(getattr(s,fn)(angle*s.pi/180)-expected)==0)
# Each fixed case records an authored branch before rounding. Labels identify the
# source question and original subpart; expected roots are verified independently.
CASES = [{'kind': 'sin', 'value': -0.6, 'a': 1.0, 'b': 0.0, 'lo': 0, 'hi': 360, 'openlo': False, 'openhi': False, 'roots': [216.86989764584402, 323.13010235415595], 'label': '10.4/q1 part 2 branch 1'},
 {'kind': 'cos', 'value': 0.7071067811865476, 'a': 1.0, 'b': 0.0, 'lo': 0, 'hi': 360, 'openlo': False, 'openhi': False, 'roots': [45.0, 315.0], 'label': '10.4/q2 part 1 branch 1'},
 {'kind': 'sin', 'value': 0.75, 'a': 1.0, 'b': 0.0, 'lo': 0, 'hi': 360, 'openlo': False, 'openhi': False, 'roots': [48.590377890729144, 131.40962210927086], 'label': '10.4/q3 part 1 branch 1'},
 {'kind': 'tan', 'value': -10.0, 'a': 1.0, 'b': 0.0, 'lo': 0, 'hi': 360, 'openlo': True, 'openhi': False, 'roots': [95.71059313749964, 275.71059313749964], 'label': '10.4/q4 part 1 branch 1'},
 {'kind': 'sin', 'value': 0.0, 'a': 1.0, 'b': 0.0, 'lo': -90, 'hi': 90, 'openlo': True, 'openhi': True, 'roots': [0.0], 'label': '10.4/q5 part 2 branch 1'},
 {'kind': 'cos', 'value': 0.5555555555555556, 'a': 1.0, 'b': 0.0, 'lo': -90, 'hi': 90, 'openlo': True, 'openhi': True, 'roots': [-56.251011404111416, 56.251011404111416], 'label': '10.4/q5 part 2 branch 2'},
 {'kind': 'tan', 'value': 1.6666666666666667, 'a': 1.0, 'b': 0.0, 'lo': 0, 'hi': 360, 'openlo': False, 'openhi': False, 'roots': [59.03624346792648, 239.03624346792648], 'label': '10.4/q6 part 2 branch 1'},
 {'kind': 'cos', 'value': 0.8660254037844386, 'a': 1.0, 'b': 0.0, 'lo': -180, 'hi': 180, 'openlo': False, 'openhi': True, 'roots': [-30.000000000000004, 30.000000000000004], 'label': '10.4/q7 part 1 branch 1'},
 {'kind': 'cos', 'value': -0.8660254037844386, 'a': 1.0, 'b': 0.0, 'lo': -180, 'hi': 180, 'openlo': False, 'openhi': True, 'roots': [-150.0, 150.0], 'label': '10.4/q7 part 1 branch 2'},
 {'kind': 'cos', 'value': 0.7559289460184545, 'a': 1.0, 'b': 0.0, 'lo': 0, 'hi': 360, 'openlo': False, 'openhi': False, 'roots': [40.893394649130904, 319.1066053508691], 'label': '10.4/q8 part 2 branch 1'},
 {'kind': 'cos', 'value': -0.7559289460184545, 'a': 1.0, 'b': 0.0, 'lo': 0, 'hi': 360, 'openlo': False, 'openhi': False, 'roots': [139.1066053508691, 220.8933946491309], 'label': '10.4/q8 part 2 branch 2'},
 {'kind': 'tan', 'value': -2.0, 'a': 1.0, 'b': 0.0, 'lo': -180, 'hi': 180, 'openlo': False, 'openhi': True, 'roots': [-63.43494882292202, 116.56505117707798], 'label': '10.4/q9 part 1 branch 1'},
 {'kind': 'sin', 'value': 0.25, 'a': 1.0, 'b': 0.0, 'lo': -180, 'hi': 180, 'openlo': False, 'openhi': True, 'roots': [14.477512185929925, 165.52248781407008], 'label': '10.4/q9 part 1 branch 2'},
 {'kind': 'cos', 'value': 0.16666666666666666, 'a': 1.0, 'b': 0.0, 'lo': 0, 'hi': 360, 'openlo': False, 'openhi': True, 'roots': [80.40593177313954, 279.5940682268605], 'label': '10.4/q9 part 2 branch 1'},
 {'kind': 'cos', 'value': 0.8660254037844386, 'a': 3.0, 'b': 0.0, 'lo': 0, 'hi': 360, 'openlo': False, 'openhi': False, 'roots': [10.000000000000002, 110.0, 130.0, 230.0, 250.0, 350.0], 'label': '10.5/q1 part 1 branch 1'},
 {'kind': 'sin', 'value': 0.7071067811865476, 'a': 0.5, 'b': 0.0, 'lo': 0, 'hi': 360, 'openlo': False, 'openhi': False, 'roots': [90.00000000000001, 270.0], 'label': '10.5/q1 part 2 branch 1'},
 {'kind': 'tan', 'value': -1.7320508075688772, 'a': 2.0, 'b': 0.0, 'lo': 0, 'hi': 360, 'openlo': False, 'openhi': False, 'roots': [60.0, 150.0, 240.0, 330.0], 'label': '10.5/q1 part 3 branch 1'},
 {'kind': 'sin', 'value': 0.2, 'a': 1.0, 'b': 30.0, 'lo': 0, 'hi': 360, 'openlo': False, 'openhi': False, 'roots': [138.4630409671845, 341.5369590328155], 'label': '10.5/q2 part 1 branch 1'},
 {'kind': 'cos', 'value': -0.4, 'a': -1.0, 'b': 60.0, 'lo': -180, 'hi': 180, 'openlo': False, 'openhi': False, 'roots': [-53.578178478201835, 173.57817847820183], 'label': '10.5/q2 part 2 branch 1'},
 {'kind': 'tan', 'value': 9.0, 'a': 1.0, 'b': -20.0, 'lo': 0, 'hi': 360, 'openlo': False, 'openhi': False, 'roots': [103.6598082540901, 283.6598082540901], 'label': '10.5/q2 part 3 branch 1'},
 {'kind': 'tan', 'value': 0.5773502691896257, 'a': 3.0, 'b': 0.0, 'lo': -180, 'hi': 180, 'openlo': False, 'openhi': False, 'roots': [-170.0, -110.0, -50.0, 9.999999999999998, 70.0, 130.0], 'label': '10.5/q3 part 1 branch 1'},
 {'kind': 'tan', 'value': 2.5, 'a': 4.0, 'b': 0.0, 'lo': 0, 'hi': 360, 'openlo': False, 'openhi': False, 'roots': [17.049647628412046, 62.049647628412046, 107.04964762841205, 152.04964762841206, 197.04964762841206, 242.04964762841206, 287.04964762841206, 332.04964762841206], 'label': '10.5/q3 part 2 branch 1'},
 {'kind': 'tan', 'value': -1.6, 'a': 1.0, 'b': 40.0, 'lo': -180, 'hi': 180, 'openlo': False, 'openhi': False, 'roots': [-97.9946167919165, 82.0053832080835], 'label': '10.5/q3 part 3 branch 1'},
 {'kind': 'sin', 'value': 0.75, 'a': 2.0, 'b': -30.0, 'lo': 0, 'hi': 360, 'openlo': False, 'openhi': False, 'roots': [39.29518894536457, 80.70481105463543, 219.29518894536457, 260.70481105463546], 'label': '10.5/q4 part 1 branch 1'},
 {'kind': 'cos', 'value': -0.4, 'a': 3.0, 'b': 20.0, 'lo': 0, 'hi': 180, 'openlo': False, 'openhi': False, 'roots': [31.19272615940061, 75.47394050726605, 151.19272615940062], 'label': '10.5/q4 part 2 branch 1'},
 {'kind': 'tan', 'value': 2.0, 'a': 4.0, 'b': -45.0, 'lo': 0, 'hi': 180, 'openlo': False, 'openhi': False, 'roots': [27.108737205730506, 72.1087372057305, 117.1087372057305, 162.1087372057305], 'label': '10.5/q4 part 3 branch 1'},
 {'kind': 'tan', 'value': 1.5, 'a': 2.0, 'b': 10.0, 'lo': -180, 'hi': 180, 'openlo': False, 'openhi': False, 'roots': [-156.84503376298989, -66.84503376298989, 23.154966237010107, 113.15496623701011], 'label': '10.5/q4 part 4 branch 1'},
 {'kind': 'cos', 'value': -0.5, 'a': 3.0, 'b': 0.0, 'lo': 0, 'hi': 360, 'openlo': False, 'openhi': True, 'roots': [40.00000000000001, 80.0, 160.0, 200.0, 280.0, 320.0], 'label': '10.5/q5 part 1 branch 1'},
 {'kind': 'sin', 'value': -0.7071067811865476, 'a': 1.0, 'b': -20.0, 'lo': 0, 'hi': 360, 'openlo': False, 'openhi': True, 'roots': [245.0, 335.0], 'label': '10.5/q5 part 2 branch 1'},
 {'kind': 'tan', 'value': 0.6, 'a': 2.0, 'b': 0.0, 'lo': 0, 'hi': 360, 'openlo': False, 'openhi': False, 'roots': [15.48187826603676, 105.48187826603676, 195.48187826603677, 285.48187826603674], 'label': '10.5/q6 part 1 branch 1'},
 {'kind': 'sin', 'value': 0.7071067811865476, 'a': 3.0, 'b': -15.0, 'lo': 0, 'hi': 180, 'openlo': False, 'openhi': False, 'roots': [20.000000000000004, 50.0, 140.0, 170.0], 'label': '10.5/q6 part 2 branch 1'},
 {'kind': 'sin', 'value': 0.8, 'a': 1.0, 'b': 30.0, 'lo': 0, 'hi': 360, 'openlo': False, 'openhi': False, 'roots': [23.130102354155987, 96.86989764584402], 'label': '10.5/q7 part 1 branch 1'},
 {'kind': 'tan', 'value': 4.0, 'a': 0.5, 'b': 0.0, 'lo': 0, 'hi': 360, 'openlo': False, 'openhi': False, 'roots': [151.92751306414706], 'label': '10.5/q7 part 2 branch 1'},
 {'kind': 'tan', 'value': -4.0, 'a': 0.5, 'b': 0.0, 'lo': 0, 'hi': 360, 'openlo': False, 'openhi': False, 'roots': [208.07248693585294], 'label': '10.5/q7 part 2 branch 2'},
 {'kind': 'tan', 'value': 2.5, 'a': 5.0, 'b': -20.0, 'lo': -90, 'hi': 90, 'openlo': True, 'openhi': True, 'roots': [-54.36028189727036, -18.36028189727036, 17.63971810272964, 53.63971810272964, 89.63971810272963], 'label': '10.5/q8 part 1 branch 1'},
 {'kind': 'sin', 'value': 0.0, 'a': 2.0, 'b': 0.0, 'lo': 0, 'hi': 180, 'openlo': False, 'openhi': False, 'roots': [0.0, 90.0, 180.0], 'label': '10.5/q9 part 2 branch 1'},
 {'kind': 'cos', 'value': 0.25, 'a': 2.0, 'b': 0.0, 'lo': 0, 'hi': 180, 'openlo': False, 'openhi': False, 'roots': [37.76124390703504, 142.23875609296496], 'label': '10.5/q9 part 2 branch 2'},
 {'kind': 'sin', 'value': 0.3333333333333333, 'a': 1.0, 'b': 0.0, 'lo': 0, 'hi': 360, 'openlo': False, 'openhi': False, 'roots': [19.47122063449069, 160.5287793655093], 'label': '10.6/q1 part 1 branch 1'},
 {'kind': 'sin', 'value': -0.3333333333333333, 'a': 1.0, 'b': 0.0, 'lo': 0, 'hi': 360, 'openlo': False, 'openhi': False, 'roots': [199.4712206344907, 340.5287793655093], 'label': '10.6/q1 part 1 branch 2'},
 {'kind': 'cos', 'value': 0.5, 'a': 1.0, 'b': 0.0, 'lo': 0, 'hi': 360, 'openlo': False, 'openhi': False, 'roots': [59.99999999999999, 300.0], 'label': '10.6/q1 part 2 branch 1'},
 {'kind': 'cos', 'value': -0.5, 'a': 1.0, 'b': 0.0, 'lo': 0, 'hi': 360, 'openlo': False, 'openhi': False, 'roots': [120.00000000000001, 240.0], 'label': '10.6/q1 part 2 branch 2'},
 {'kind': 'sin', 'value': 0.0, 'a': 1.0, 'b': 0.0, 'lo': 0, 'hi': 360, 'openlo': False, 'openhi': False, 'roots': [0.0, 180.0, 360.0], 'label': '10.6/q1 part 3 branch 1'},
 {'kind': 'sin', 'value': 0.2, 'a': 1.0, 'b': 0.0, 'lo': 0, 'hi': 360, 'openlo': False, 'openhi': False, 'roots': [11.536959032815489, 168.4630409671845], 'label': '10.6/q1 part 3 branch 2'},
 {'kind': 'tan', 'value': -4.0, 'a': 1.0, 'b': 0.0, 'lo': 0, 'hi': 360, 'openlo': False, 'openhi': False, 'roots': [104.03624346792647, 284.03624346792645], 'label': '10.6/q1 part 4 branch 1'},
 {'kind': 'tan', 'value': 3.0, 'a': 1.0, 'b': 0.0, 'lo': 0, 'hi': 360, 'openlo': False, 'openhi': False, 'roots': [71.56505117707799, 251.56505117707798], 'label': '10.6/q1 part 4 branch 2'},
 {'kind': 'cos', 'value': 1.0, 'a': 1.0, 'b': 0.0, 'lo': 0, 'hi': 360, 'openlo': False, 'openhi': False, 'roots': [0.0, 360.0], 'label': '10.6/q1 part 5 branch 1'},
 {'kind': 'cos', 'value': 0.3333333333333333, 'a': 1.0, 'b': 0.0, 'lo': 0, 'hi': 360, 'openlo': False, 'openhi': False, 'roots': [70.52877936550931, 289.4712206344907], 'label': '10.6/q1 part 5 branch 2'},
 {'kind': 'tan', 'value': 2.0, 'a': 3.0, 'b': 0.0, 'lo': 0, 'hi': 360, 'openlo': False, 'openhi': False, 'roots': [21.144982940974007, 81.144982940974, 141.14498294097402, 201.14498294097402, 261.144982940974, 321.144982940974], 'label': '10.6/q1 part 6 branch 1'},
 {'kind': 'tan', 'value': -2.0, 'a': 3.0, 'b': 0.0, 'lo': 0, 'hi': 360, 'openlo': False, 'openhi': False, 'roots': [38.85501705902599, 98.855017059026, 158.85501705902598, 218.85501705902598, 278.855017059026, 338.855017059026], 'label': '10.6/q1 part 6 branch 2'},
 {'kind': 'cos', 'value': 1.0, 'a': 3.0, 'b': 0.0, 'lo': 0, 'hi': 360, 'openlo': False, 'openhi': False, 'roots': [0.0, 120.0, 240.0, 360.0], 'label': '10.6/q2 part 1 branch 1'},
 {'kind': 'cos', 'value': -1.0, 'a': 3.0, 'b': 0.0, 'lo': 0, 'hi': 360, 'openlo': False, 'openhi': False, 'roots': [60.0, 180.0, 300.0], 'label': '10.6/q2 part 1 branch 2'},
 {'kind': 'tan', 'value': 0.0, 'a': 1.0, 'b': 0.0, 'lo': 0, 'hi': 360, 'openlo': False, 'openhi': False, 'roots': [0.0, 180.0, 360.0], 'label': '10.6/q2 part 2 branch 1'},
 {'kind': 'tan', 'value': 5.0, 'a': 1.0, 'b': 0.0, 'lo': 0, 'hi': 360, 'openlo': False, 'openhi': False, 'roots': [78.69006752597979, 258.69006752597977], 'label': '10.6/q2 part 2 branch 2'},
 {'kind': 'sin', 'value': -1.0, 'a': 1.0, 'b': 0.0, 'lo': 0, 'hi': 360, 'openlo': False, 'openhi': False, 'roots': [270.0], 'label': '10.6/q2 part 3 branch 1'},
 {'kind': 'sin', 'value': 0.0, 'a': 1.0, 'b': 30.0, 'lo': 0, 'hi': 360, 'openlo': False, 'openhi': False, 'roots': [150.0, 330.0], 'label': '10.6/q2 part 4 branch 1'},
 {'kind': 'cos', 'value': 0.25, 'a': 1.0, 'b': 30.0, 'lo': 0, 'hi': 360, 'openlo': False, 'openhi': False, 'roots': [45.522487814070075, 254.47751218592992], 'label': '10.6/q2 part 4 branch 2'},
 {'kind': 'cos', 'value': 0.3333333333333333, 'a': 1.0, 'b': 0.0, 'lo': 0, 'hi': 360, 'openlo': False, 'openhi': False, 'roots': [70.52877936550931, 289.4712206344907], 'label': '10.6/q3 part 2 branch 1'},
 {'kind': 'cos', 'value': 1.0, 'a': 1.0, 'b': 0.0, 'lo': 0, 'hi': 360, 'openlo': False, 'openhi': False, 'roots': [0.0, 360.0], 'label': '10.6/q3 part 2 branch 2'},
 {'kind': 'sin', 'value': 0.2, 'a': 1.0, 'b': 0.0, 'lo': 0, 'hi': 360, 'openlo': False, 'openhi': False, 'roots': [11.536959032815489, 168.4630409671845], 'label': '10.6/q4 part 1 branch 1'},
 {'kind': 'sin', 'value': 1.0, 'a': 1.0, 'b': 0.0, 'lo': 0, 'hi': 360, 'openlo': False, 'openhi': False, 'roots': [90.0], 'label': '10.6/q4 part 1 branch 2'},
 {'kind': 'cos', 'value': 0.6666666666666666, 'a': 1.0, 'b': 0.0, 'lo': 0, 'hi': 360, 'openlo': False, 'openhi': False, 'roots': [48.18968510422141, 311.81031489577856], 'label': '10.6/q4 part 2 branch 1'},
 {'kind': 'cos', 'value': 0.5, 'a': 1.0, 'b': 0.0, 'lo': 0, 'hi': 360, 'openlo': False, 'openhi': False, 'roots': [59.99999999999999, 300.0], 'label': '10.6/q4 part 2 branch 2'},
 {'kind': 'sin', 'value': 0.5, 'a': 1.0, 'b': 0.0, 'lo': 0, 'hi': 360, 'openlo': False, 'openhi': False, 'roots': [29.999999999999996, 150.0], 'label': '10.6/q4 part 3 branch 1'},
 {'kind': 'sin', 'value': 0.8944271909999159, 'a': 1.0, 'b': 0.0, 'lo': 0, 'hi': 360, 'openlo': False, 'openhi': True, 'roots': [63.43494882292201, 116.56505117707799], 'label': '10.6/q5 part 2 branch 1'},
 {'kind': 'sin', 'value': -0.8944271909999159, 'a': 1.0, 'b': 0.0, 'lo': 0, 'hi': 360, 'openlo': False, 'openhi': True, 'roots': [243.43494882292202, 296.565051177078], 'label': '10.6/q5 part 2 branch 2'},
 {'kind': 'cos', 'value': 0.3333333333333333, 'a': 1.0, 'b': 0.0, 'lo': 0, 'hi': 180, 'openlo': True, 'openhi': True, 'roots': [70.52877936550931], 'label': '10.6/q6 part 1 branch 1'},
 {'kind': 'cos', 'value': -0.3333333333333333, 'a': 1.0, 'b': 0.0, 'lo': 0, 'hi': 180, 'openlo': True, 'openhi': True, 'roots': [109.47122063449069], 'label': '10.6/q6 part 1 branch 2'},
 {'kind': 'sin', 'value': 0.5, 'a': 1.0, 'b': 0.0, 'lo': 0, 'hi': 360, 'openlo': False, 'openhi': False, 'roots': [29.999999999999996, 150.0], 'label': '10.6/q7 part 1 branch 1'},
 {'kind': 'cos', 'value': 0.2637626158259733, 'a': 1.0, 'b': 0.0, 'lo': 0, 'hi': 360, 'openlo': False, 'openhi': True, 'roots': [74.70655980754042, 285.29344019245957], 'label': '10.6/q8 part 2 branch 1'},
 {'kind': 'cos', 'value': 0.2, 'a': 1.0, 'b': 0.0, 'lo': 360, 'hi': 540, 'openlo': False, 'openhi': True, 'roots': [438.4630409671845], 'label': '10.6/q9 part 1 branch 1'},
 {'kind': 'cos', 'value': 0.3333333333333333, 'a': 1.0, 'b': 0.0, 'lo': 360, 'hi': 540, 'openlo': False, 'openhi': True, 'roots': [430.5287793655093], 'label': '10.6/q9 part 1 branch 2'},
 {'kind': 'tan', 'value': 2.5, 'a': 1.0, 'b': 20.0, 'lo': 0, 'hi': 360, 'openlo': False, 'openhi': True, 'roots': [48.198590513648185, 228.19859051364818], 'label': 'problem-a/qbronze part 2 branch 1'},
 {'kind': 'sin', 'value': 0.3333333333333333, 'a': 3.0, 'b': 0.0, 'lo': 0, 'hi': 180, 'openlo': False, 'openhi': False, 'roots': [6.490406878163564, 53.50959312183644, 126.49040687816357, 173.50959312183645], 'label': 'problem-a/qsilver part 1 branch 1'},
 {'kind': 'cos', 'value': -0.75, 'a': 2.0, 'b': -15.0, 'lo': -180, 'hi': 180, 'openlo': False, 'openhi': False, 'roots': [-103.20481105463543, -61.79518894536457, 76.79518894536457, 118.20481105463543], 'label': 'problem-a/qgold part 1 branch 1'},
 {'kind': 'tan', 'value': 1.1547005383792515, 'a': 1.0, 'b': 0.0, 'lo': 0, 'hi': 360, 'openlo': False, 'openhi': True, 'roots': [49.106605350869096, 229.1066053508691], 'label': 'problem-b/qbronze part 2 branch 1'},
 {'kind': 'tan', 'value': -1.1547005383792515, 'a': 1.0, 'b': 0.0, 'lo': 0, 'hi': 360, 'openlo': False, 'openhi': True, 'roots': [130.8933946491309, 310.8933946491309], 'label': 'problem-b/qbronze part 2 branch 2'},
 {'kind': 'sin', 'value': 0.25, 'a': 1.0, 'b': 0.0, 'lo': 0, 'hi': 720, 'openlo': False, 'openhi': True, 'roots': [14.477512185929925, 165.52248781407008, 374.4775121859299, 525.52248781407], 'label': 'problem-b/qsilver part 2 branch 1'},
 {'kind': 'cos', 'value': 1.0, 'a': 3.0, 'b': 0.0, 'lo': 0, 'hi': 90, 'openlo': False, 'openhi': True, 'roots': [0.0], 'label': 'problem-b/qgold part 1 branch 1'},
 {'kind': 'cos', 'value': -0.375, 'a': 3.0, 'b': 0.0, 'lo': 0, 'hi': 90, 'openlo': False, 'openhi': True, 'roots': [37.341437612347384, 82.65856238765262], 'label': 'problem-b/qgold part 1 branch 2'},
 {'kind': 'tan', 'value': -0.6666666666666666, 'a': 1.0, 'b': 0.0, 'lo': 0, 'hi': 360, 'openlo': False, 'openhi': True, 'roots': [146.30993247402023, 326.30993247402023], 'label': 'exam/q47 part 1 branch 1'},
 {'kind': 'tan', 'value': 2.5, 'a': 1.0, 'b': 0.0, 'lo': 0, 'hi': 360, 'openlo': False, 'openhi': True, 'roots': [68.19859051364818, 248.19859051364818], 'label': 'exam/q47 part 1 branch 2'},
 {'kind': 'cos', 'value': 0.804737854124365, 'a': 1.0, 'b': 0.0, 'lo': 0, 'hi': 360, 'openlo': False, 'openhi': True, 'roots': [36.4150539484369, 323.5849460515631], 'label': 'exam/q60 part 2 branch 1'},
 {'kind': 'cos', 'value': -0.13807118745769836, 'a': 1.0, 'b': 0.0, 'lo': 0, 'hi': 360, 'openlo': False, 'openhi': True, 'roots': [97.93624951449458, 262.0637504855054], 'label': 'exam/q60 part 2 branch 2'},
 {'kind': 'sin', 'value': 0.8660254037844386, 'a': 1.0, 'b': 15.0, 'lo': 0, 'hi': 360, 'openlo': False, 'openhi': False, 'roots': [44.99999999999999, 105.0], 'label': 'exam/q66 part 1 branch 1'},
 {'kind': 'cos', 'value': -0.7071067811865476, 'a': 2.0, 'b': 0.0, 'lo': 0, 'hi': 360, 'openlo': False, 'openhi': False, 'roots': [67.5, 112.5, 247.5, 292.5], 'label': 'exam/q66 part 2 branch 1'},
 {'kind': 'cos', 'value': -0.6, 'a': 3.0, 'b': -20.0, 'lo': 0, 'hi': 180, 'openlo': False, 'openhi': True, 'roots': [48.95663254861467, 84.37670078471866, 168.9566325486147], 'label': 'exam/q76 part 1 branch 1'},
 {'kind': 'sin', 'value': 0.5, 'a': 1.0, 'b': 0.0, 'lo': 0, 'hi': 360, 'openlo': True, 'openhi': False, 'roots': [29.999999999999996, 150.0], 'label': 'exam/q84 part 2 branch 1'},
 {'kind': 'sin', 'value': -0.3333333333333333, 'a': 1.0, 'b': 0.0, 'lo': 0, 'hi': 360, 'openlo': True, 'openhi': False, 'roots': [199.4712206344907, 340.5287793655093], 'label': 'exam/q84 part 2 branch 2'},
 {'kind': 'sin', 'value': 0.8, 'a': 2.0, 'b': 60.0, 'lo': 0, 'hi': 360, 'openlo': False, 'openhi': True, 'roots': [33.43494882292201, 176.565051177078, 213.43494882292202, 356.565051177078], 'label': 'exam/q85 part 1 branch 1'},
 {'kind': 'sin', 'value': 0.3333333333333333, 'a': 1.0, 'b': 0.0, 'lo': 360, 'hi': 540, 'openlo': False, 'openhi': False, 'roots': [379.4712206344907, 520.5287793655093], 'label': 'exam/q85 part 2 branch 1'}]
for c in CASES:
 f=lambda x:getattr(math,c['kind'])(math.radians(c['a']*x+c['b']))-c['value']
 lo,hi=c['lo'],c['hi'];a,b=c['a'],c['b']
 # Every multiple of 90 degrees is a monotonicity boundary. At tangent poles
 # evaluate infinitesimally inside the segment and reject any pole as a root.
 boundaries=sorted(set([lo,hi]+[(90*k-b)/a for k in range(-30,31) if lo<(90*k-b)/a<hi]))
 roots=[]
 def accept(z):
  if c['openlo'] and abs(z-lo)<1e-7:return
  if c['openhi'] and abs(z-hi)<1e-7:return
  if c['kind']=='tan' and abs(math.cos(math.radians(a*z+b)))<1e-8:return
  if abs(f(z))<1e-7 and not any(abs(z-r)<1e-6 for r in roots):roots.append(z)
 for l,r in zip(boundaries,boundaries[1:]):
  accept(l);accept(r)
  ll=l+1e-8;rr=r-1e-8
  if f(ll)*f(rr)<0:
   for _ in range(60):
    m=(ll+rr)/2
    if f(ll)*f(m)<=0:rr=m
    else:ll=m
   accept((ll+rr)/2)
 roots.sort();expected=sorted(c['roots'])
 record(c['label']+' complete roots',len(roots)==len(expected) and all(abs(i-j)<1e-6 for i,j in zip(roots,expected)))
 record(c['label']+' residuals',all(abs(f(z))<1e-9 for z in expected))
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args();args.output.write_text(json.dumps(checks,indent=2));print(len(checks),'independent checks passed')
