# Sample Assessment Material 9MA0/02 Pure Mathematics 2, transcribed from the QP page images (the PDF text layer uses an unreadable font encoding).
from lib import *
CONTEXT = context(SHOW, SIG3)
Q = {}
D = lambda a, b: rf'\dfrac{{\mathrm d{a}}}{{\mathrm d{b}}}'
Q[1] = (eq(r'\mathrm f(x)=2x^3-5x^2+ax+a')
        + p(f'Given that {m("(x+2)")} is a factor of {m(r"\mathrm f(x)")}, find the value of the constant {m("a")}. {mk(3)}'))
Q[2] = (p('Some A level students were given the following question.')
        + p(f'Solve, for {m(r"-90^\circ<\theta<90^\circ")}, the equation') + eq(r'\cos\theta=2\sin\theta')
        + p('The attempts of two of the students are shown below.')
        + fig(2, 60, 'Two boxed attempts. Student A: cos θ = 2 sin θ, tan θ = 2, θ = 63.4°. Student B: cos θ = 2 sin θ, cos² θ = 4 sin² θ, 1 − sin² θ = 4 sin² θ, sin² θ = 1/5, sin θ = ±1/√5, θ = ±26.6°.')
        + parts([f'Identify an error made by student {m("A")}. {mk(1)}'])
        + p(f'Student {m("B")} gives {m(r"\theta=-26.6^\circ")} as one of the answers to {m(r"\cos\theta=2\sin\theta")}.')
        + parts([parts(['Explain why this answer is incorrect.', 'Explain how this incorrect answer arose.'], kind='i') + mk(2)], start=2))
Q[3] = (p(f'Given {m("y=x(2x+1)^4")}, show that') + eq(D('y', 'x') + '=(2x+1)^n(Ax+B)')
        + p(f'where {m("n")}, {m("A")} and {m("B")} are constants to be found. {mk(4)}'))
Q[4] = (p('Given') + eq(r'\mathrm f(x)=\mathrm e^x,\qquad x\in\mathbb R') + eq(r'\mathrm g(x)=3\ln x,\qquad x>0,\ x\in\mathbb R')
        + parts([f'find an expression for {m(r"\mathrm{gf}(x)")}, simplifying your answer. {mk(2)}',
                 f'Show that there is only one real value of {m("x")} for which {m(r"\mathrm{gf}(x)=\mathrm{fg}(x)")} {mk(3)}']))
Q[5] = (p(f'The mass, {m("m")} grams, of a radioactive substance, {m("t")} years after first being observed, is modelled by the equation')
        + eq(r'm=25\mathrm e^{-0.05t}') + p('According to the model,')
        + parts([f'find the mass of the radioactive substance six months after it was first observed, {mk(2)}',
                 f'show that {m(D("m", "t") + "=km")}, where {m("k")} is a constant to be found. {mk(2)}']))
Q[6] = (p('Complete the table below. The first one has been done for you.')
        + p('For each statement you must state if it is always true, sometimes true or never true, giving a reason in each case.')
        + table([['Statement', 'Always True', 'Sometimes True', 'Never True', 'Reason'],
                 [f'The quadratic equation {m(r"ax^2+bx+c=0,\quad(a\neq0)")} has 2 real roots.', '', '✓', '',
                  f'It only has 2 real roots when {m("b^2-4ac>0")}. When {m("b^2-4ac=0")} it has 1 real root and when {m("b^2-4ac<0")} it has 0 real roots.'],
                 [f'(i)<br>When a real value of {m("x")} is substituted into {m("x^2-6x+10")} the result is positive. {mk(2)}', '', '', '', ''],
                 [f'(ii)<br>If {m("ax>b")} then {m(r"x>\dfrac ba")} {mk(2)}', '', '', '', ''],
                 [f'(iii)<br>The difference between consecutive square numbers is odd. {mk(2)}', '', '', '', '']], head=1))
Q[7] = (parts([f'Use the binomial expansion, in ascending powers of {m("x")}, to show that' + eq(r'\sqrt{(4-x)}=2-\frac14x+kx^2+\dots')
               + f'where {m("k")} is a rational constant to be found. {mk(4)}'])
        + p(f'A student attempts to substitute {m("x=1")} into both sides of this equation to find an approximate value for {m(r"\sqrt3")}.')
        + parts([f'State, giving a reason, if the expansion is valid for this value of {m("x")}. {mk(1)}'], start=2))
Q[8] = (fig(8, 50, 'Figure 1: rectangle ABCD with A on the positive y-axis, B on the positive x-axis, D on the negative x-axis just left of O and C below the x-axis; the rectangle is shaded')
        + p(f'Figure 1 shows a rectangle {m("ABCD")}.')
        + p(f'The point {m("A")} lies on the {m("y")}-axis and the points {m("B")} and {m("D")} lie on the {m("x")}-axis as shown in Figure 1.')
        + p(f'Given that the straight line through the points {m("A")} and {m("B")} has equation {m("5y+2x=10")}')
        + parts([f'show that the straight line through the points {m("A")} and {m("D")} has equation {m("2y-5x=4")} {mk(4)}',
                 f'find the area of the rectangle {m("ABCD")}. {mk(3)}']))
Q[9] = (p(f'Given that {m("A")} is constant and') + eq(r'\int_1^4\left(3\sqrt x+A\right)\mathrm dx=2A^2')
        + p(f'show that there are exactly two possible values for {m("A")}. {mk(5)}'))
Q[10] = (p(f'In a geometric series the common ratio is {m("r")} and sum to {m("n")} terms is {m("S_n")}')
         + p('Given') + eq(r'S_\infty=\frac87\times S_6')
         + p(f'show that {m(r"r=\pm\dfrac{1}{\sqrt k}")}, where {m("k")} is an integer to be found. {mk(4)}'))
Q[11] = (fig(11, 30, 'Figure 2: sketch of y = f(x) for x ≥ 0, starting on the positive y-axis, falling to a minimum and then rising as a straight line')
         + p(f'Figure 2 shows a sketch of part of the graph {m(r"y=\mathrm f(x)")}, where') + eq(r'\mathrm f(x)=2|3-x|+5,\qquad x\geqslant0')
         + parts([f'State the range of {m(r"\mathrm f")} {mk(1)}', 'Solve the equation' + eq(r'\mathrm f(x)=\frac12x+30') + mk(3)])
         + p(f'Given that the equation {m(r"\mathrm f(x)=k")}, where {m("k")} is a constant, has two distinct roots,')
         + parts([f'state the set of possible values for {m("k")}. {mk(2)}'], start=3))
Q[12] = parts([f'Solve, for {m(r"-180^\circ\leqslant x<180^\circ")}, the equation' + eq(r'3\sin^2x+\sin x+8=9\cos^2x') + f'giving your answers to 2 decimal places. {mk(6)}',
               'Hence find the smallest positive solution of the equation' + eq(r'3\sin^2(2\theta-30^\circ)+\sin(2\theta-30^\circ)+8=9\cos^2(2\theta-30^\circ)')
               + f'giving your answer to 2 decimal places. {mk(2)}'])
Q[13] = (parts([f'Express {m(r"10\cos\theta-3\sin\theta")} in the form {m(r"R\cos(\theta+\alpha)")}, where {m("R>0")} and {m(r"0<\alpha<90^\circ")}<br>'
                f'Give the exact value of {m("R")} and give the value of {m(r"\alpha")}, in degrees, to 2 decimal places. {mk(3)}'])
         + fig(13, 75, 'Figure 3: a Ferris wheel beside a graph of H against t on a grid, showing two complete cycles of a wave starting near the t-axis')
         + p(f'The height above the ground, {m("H")} metres, of a passenger on a Ferris wheel {m("t")} minutes after the wheel starts turning, is modelled by the equation')
         + eq(r'H=a-10\cos(80t)^\circ+3\sin(80t)^\circ') + p(f'where {m("a")} is a constant.')
         + p(f'Figure 3 shows the graph of {m("H")} against {m("t")} for two complete cycles of the wheel.')
         + p('Given that the initial height of the passenger above the ground is 1 metre,')
         + parts([parts(['find a complete equation for the model,', 'hence find the maximum height of the passenger above the ground.'], kind='i') + mk(2),
                  'Find the time taken, to the nearest second, for the passenger to reach the maximum height on the second cycle.'
                  + p('(<em>Solutions based entirely on graphical or numerical methods are not acceptable</em>.)') + mk(3)], start=2)
         + p('It is decided that, to increase profits, the speed of the wheel is to be increased.')
         + parts([f'How would you adapt the equation of the model to reflect this increase in speed? {mk(1)}'], start=4))
Q[14] = (p('A company decides to manufacture a soft drinks can with a capacity of 500 ml.')
         + p(f'The company models the can in the shape of a right circular cylinder with radius {m("r")} cm and height {m("h")} cm.')
         + p('In the model they assume that the can is made from a metal of negligible thickness.')
         + parts([f'Prove that the total surface area, {m("S")} cm², of the can is given by' + eq(r'S=2\pi r^2+\frac{1000}{r}') + mk(3)])
         + p(f'Given that {m("r")} can vary,')
         + parts([f'find the dimensions of a can that has minimum surface area. {mk(5)}',
                  f'With reference to the shape of the can, suggest a reason why the company may choose not to manufacture a can with minimum surface area. {mk(1)}'], start=2))
Q[15] = (fig(15, 50, 'Figure 4: sketch of the curve C for x ≥ 0 and its tangent l at P; the shaded region R lies between C, l and the y-axis')
         + p(f'Figure 4 shows a sketch of the curve {m("C")} with equation') + eq(r'y=5x^{\frac32}-9x+11,\qquad x\geqslant0')
         + p(f'The point {m("P")} with coordinates {m("(4, 15)")} lies on {m("C")}.')
         + p(f'The line {m("l")} is the tangent to {m("C")} at the point {m("P")}.')
         + p(f'The region {m("R")}, shown shaded in Figure 4, is bounded by the curve {m("C")}, the line {m("l")} and the {m("y")}-axis.')
         + p(f'Show that the area of {m("R")} is 24, making your method clear.')
         + p(f'(<em>Solutions based entirely on graphical or numerical methods are not acceptable.</em>) {mk(10)}'))
Q[16] = (parts([f'Express {m(r"\dfrac{1}{P(11-2P)}")} in partial fractions. {mk(3)}'])
         + p('A population of meerkats is being studied.') + p('The population is modelled by the differential equation')
         + eq(D('P', 't') + r'=\frac1{22}P(11-2P),\qquad t\geqslant0,\qquad 0<P<5.5')
         + p(f'where {m("P")}, in thousands, is the population of meerkats and {m("t")} is the time measured in years since the study began.')
         + p('Given that there were 1000 meerkats in the population when the study began,')
         + parts([f'determine the time taken, in years, for this population of meerkats to double, {mk(6)}',
                  'show that' + eq(r'P=\frac{A}{B+C\mathrm e^{-\frac12t}}') + f'where {m("A")}, {m("B")} and {m("C")} are integers to be found. {mk(3)}'], start=2))
