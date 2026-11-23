# Sample Assessment Material 9FM0/01 Core Pure Mathematics 1, transcribed from the QP page images (the PDF text layer uses an unreadable font encoding).
from lib import *
CONTEXT = context(SHOW, SIG3)
Q = {}
D = lambda a, b: rf'\dfrac{{\mathrm d{a}}}{{\mathrm d{b}}}'
Q[1] = (p('Prove that') + eq(r'\sum_{r=1}^{n}\frac{1}{(r+1)(r+3)}=\frac{n(an+b)}{12(n+2)(n+3)}')
        + p(f'where {m("a")} and {m("b")} are constants to be found. {mk(5)}'))
Q[2] = (p(f'Prove by induction that for all positive integers {m("n")},') + eq(r'\mathrm f(n)=2^{3n+1}+3\left(5^{2n+1}\right)')
        + p(f'is divisible by 17 {mk(6)}'))
Q[3] = (eq(r'\mathrm f(z)=z^4+az^3+6z^2+bz+65') + p(f'where {m("a")} and {m("b")} are real constants.')
        + p(f'Given that {m(r"z=3+2\mathrm i")} is a root of the equation {m(r"\mathrm f(z)=0")}, show the roots of {m(r"\mathrm f(z)=0")} on a single Argand diagram. {mk(9)}'))
Q[4] = (fig(4, 60, 'Figure 1: the polar curve C from the initial line to the half-line theta = pi/2, with O, the point A on C, N on the initial line below A, and the shaded region R between C, the initial line and AN')
        + p(f'The curve {m("C")} shown in Figure 1 has polar equation') + eq(r'r=4+\cos2\theta\qquad 0\leqslant\theta\leqslant\frac{\pi}{2}')
        + p(f'At the point {m("A")} on {m("C")}, the value of {m("r")} is {m(r"\dfrac92")}')
        + p(f'The point {m("N")} lies on the initial line and {m("AN")} is perpendicular to the initial line.')
        + p(f'The finite region {m("R")}, shown shaded in Figure 1, is bounded by the curve {m("C")}, the initial line and the line {m("AN")}.')
        + p(f'Find the exact area of the shaded region {m("R")}, giving your answer in the form {m(r"p\pi+q\sqrt3")} where {m("p")} and {m("q")} are rational numbers to be found. {mk(9)}'))
Q[5] = (p('A pond initially contains 1000 litres of unpolluted water.') + p('The pond is leaking at a constant rate of 20 litres per day.')
        + p('It is suspected that contaminated water flows into the pond at a constant rate of 25 litres per day and that the contaminated water contains 2 grams of pollutant in every litre of water.')
        + p('It is assumed that the pollutant instantly dissolves throughout the pond upon entry.')
        + p(f'Given that there are {m("x")} grams of the pollutant in the pond after {m("t")} days,')
        + parts(['show that the situation can be modelled by the differential equation,' + eq(D('x', 't') + r'=50-\frac{4x}{200+t}') + mk(4),
                 f'Hence find the number of grams of pollutant in the pond after 8 days. {mk(5)}',
                 f'Explain how the model could be refined. {mk(1)}']))
Q[6] = (eq(r'\mathrm f(x)=\frac{x+2}{x^2+9}')
        + parts(['Show that' + eq(r'\int\mathrm f(x)\,\mathrm dx=A\ln(x^2+9)+B\arctan\left(\frac x3\right)+c')
                 + f'where {m("c")} is an arbitrary constant and {m("A")} and {m("B")} are constants to be found. {mk(4)}',
                 f'Hence show that the mean value of {m(r"\mathrm f(x)")} over the interval {m("[0, 3]")} is' + eq(r'\frac16\ln2+\frac1{18}\pi') + mk(3),
                 f'Use the answer to part (b) to find the mean value, over the interval {m("[0, 3]")}, of' + eq(r'\mathrm f(x)+\ln k')
                 + f'where {m("k")} is a positive constant, giving your answer in the form {m(r"p+\dfrac16\ln q")}, where {m("p")} and {m("q")} are constants and {m("q")} is in terms of {m("k")}. {mk(2)}']))
Q[7] = (fig(7, 30, 'Figure 2: a teardrop-shaped pendant of height 2 cm, shaded, with a vertical double-headed arrow marking the 2 cm height')
        + p(f'Figure 2 shows the image of a gold pendant which has height 2 cm. The pendant is modelled by a solid of revolution of a curve {m("C")} about the {m("y")}-axis. The curve {m("C")} has parametric equations')
        + eq(r'x=\cos\theta+\frac12\sin2\theta,\qquad y=-(1+\sin\theta)\qquad 0\leqslant\theta\leqslant2\pi')
        + parts([f'Show that a Cartesian equation of the curve {m("C")} is' + eq('x^2=-(y^4+2y^3)') + mk(4),
                 f'Hence, using the model, find, in cm³, the volume of the pendant. {mk(4)}']))
Q[8] = (p(f'The line {m("l_1")} has equation {m(r"\dfrac{x-2}{4}=\dfrac{y-4}{-2}=\dfrac{z+6}{1}")}')
        + p(f'The plane {m(r"\Pi")} has equation {m("x-2y+z=6")}')
        + p(f'The line {m("l_2")} is the reflection of the line {m("l_1")} in the plane {m(r"\Pi")}.')
        + p(f'Find a vector equation of the line {m("l_2")} {mk(7)}'))
Q[9] = (p('A company plans to build a new fairground ride. The ride will consist of a capsule that will hold the passengers and the capsule will be attached to a tall tower. '
          'The capsule is to be released from rest from a point half way up the tower and then made to oscillate in a vertical line.')
        + p(f'The vertical displacement, {m("x")} metres, of the top of the capsule below its initial position at time {m("t")} seconds is modelled by the differential equation,')
        + eq(r'm\frac{\mathrm d^2x}{\mathrm dt^2}+4\frac{\mathrm dx}{\mathrm dt}+x=200\cos t,\qquad t\geqslant0')
        + p(f'where {m("m")} is the mass of the capsule including its passengers, in thousands of kilograms.')
        + p('The maximum permissible weight for the capsule, including its passengers, is 30 000 N.')
        + p(f'Taking the value of {m("g")} to be {m(r"10\,\mathrm{m\,s^{-2}}")} and assuming the capsule is at its maximum permissible weight,')
        + parts([parts([f'explain why the value of {m("m")} is 3', 'show that a particular solution to the differential equation is' + eq(r'x=40\sin t-20\cos t'),
                        'hence find the general solution of the differential equation.'], kind='i') + mk(8),
                 f'Using the model, find, to the nearest metre, the vertical distance of the top of the capsule from its initial position, 9 seconds after it is released. {mk(4)}']))
