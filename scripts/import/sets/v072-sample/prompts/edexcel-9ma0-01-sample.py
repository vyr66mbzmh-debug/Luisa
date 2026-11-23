# Sample Assessment Material 9MA0/01 Pure Mathematics 1, transcribed from the QP page images (the PDF text layer uses an unreadable font encoding).
from lib import *
CONTEXT = context(SHOW, SIG3)
Q = {}
D = lambda a, b: rf'\dfrac{{\mathrm d{a}}}{{\mathrm d{b}}}'
Q[1] = (p(f'The curve {m("C")} has equation') + eq('y=3x^4-8x^3-3')
        + parts([f'Find' + parts([m(D('y', 'x')), m(r'\dfrac{\mathrm d^2y}{\mathrm dx^2}')], kind='i') + mk(3),
                 f'Verify that {m("C")} has a stationary point when {m("x=2")} {mk(2)}',
                 f'Determine the nature of this stationary point, giving a reason for your answer. {mk(2)}']))
Q[2] = (fig(2, 50, 'Figure 1: shape ABCDOA; a shaded sector AOB of one circle centre O on the left and a sector COD of a smaller circle centre O on the right, with angle COD = 0.4 radians, arc CD = 3 cm and AOD a straight line of length 12 cm')
        + p(f'The shape {m("ABCDOA")}, as shown in Figure 1, consists of a sector {m("COD")} of a circle centre {m("O")} joined to a sector {m("AOB")} of a different circle, also centre {m("O")}.')
        + p(f'Given that arc length {m(r"CD=3\text{ cm}")}, {m(r"\angle COD=0.4")} radians and {m("AOD")} is a straight line of length {m(r"12\text{ cm}")},')
        + parts([f'find the length of {m("OD")}, {mk(2)}', f'find the area of the shaded sector {m("AOB")}. {mk(3)}']))
Q[3] = (p(f'A circle {m("C")} has equation') + eq('x^2+y^2-4x+10y=k') + p(f'where {m("k")} is a constant.')
        + parts([f'Find the coordinates of the centre of {m("C")}. {mk(2)}', f'State the range of possible values for {m("k")}. {mk(2)}']))
Q[4] = (p(f'Given that {m("a")} is a positive constant and') + eq(r'\int_a^{2a}\frac{t+1}{t}\,\mathrm dt=\ln 7')
        + p(f'show that {m(r"a=\ln k")}, where {m("k")} is a constant to be found. {mk(4)}'))
Q[5] = (p(f'A curve {m("C")} has parametric equations') + eq(r'x=2t-1,\qquad y=4t-7+\frac{3}{t},\qquad t\neq 0')
        + p(f'Show that the Cartesian equation of the curve {m("C")} can be written in the form') + eq(r'y=\frac{2x^2+ax+b}{x+1},\qquad x\neq -1')
        + p(f'where {m("a")} and {m("b")} are integers to be found. {mk(3)}'))
Q[6] = (p('A company plans to extract oil from an oil field.')
        + p(f'The daily volume of oil {m("V")}, measured in barrels that the company will extract from this oil field depends upon the time, {m("t")} years, after the start of drilling.')
        + p('The company decides to use a model to estimate the daily volume of oil that will be extracted. The model includes the following assumptions:')
        + ul(['The initial daily volume of oil extracted from the oil field will be 16 000 barrels.',
              'The daily volume of oil that will be extracted exactly 4 years after the start of drilling will be 9000 barrels.',
              'The daily volume of oil extracted will decrease over time.'])
        + p('The diagram below shows the graphs of two possible models.')
        + fig(6, 80, 'Two graphs of V against t. Model A: a straight line from (0, 16 000) through (4, 9000) crossing the t-axis. Model B: a decreasing curve from (0, 16 000) through (4, 9000) approaching the t-axis.')
        + parts([parts([f'Use model {m("A")} to estimate the daily volume of oil that will be extracted exactly 3 years after the start of drilling.',
                        f'Write down a limitation of using model {m("A")}.'], kind='i') + mk(2),
                 parts([f'Using an exponential model and the information given in the question, find a possible equation for model {m("B")}.',
                        'Using your answer to (b)(i) estimate the daily volume of oil that will be extracted exactly 3 years after the start of drilling.'], kind='i') + mk(5)]))
Q[7] = (fig(7, 25, 'Figure 2: sketch of a triangle ABC with A on the left, B at the top and C at the bottom right')
        + p(f'Figure 2 shows a sketch of a triangle {m("ABC")}.')
        + p(f'Given {m(r"\overrightarrow{AB}=2\mathbf i+3\mathbf j+\mathbf k")} and {m(r"\overrightarrow{BC}=\mathbf i-9\mathbf j+3\mathbf k")},')
        + p(f'show that {m(r"\angle BAC=105.9^\circ")} to one decimal place. {mk(5)}'))
Q[8] = (eq(r'\mathrm f(x)=\ln(2x-5)+2x^2-30,\qquad x>2.5')
        + parts([f'Show that {m(r"\mathrm f(x)=0")} has a root {m(r"\alpha")} in the interval {m("[3.5, 4]")} {mk(2)}'])
        + p(f'A student takes 4 as the first approximation to {m(r"\alpha")}.')
        + p(f'Given {m(r"\mathrm f(4)=3.099")} and {m(r"\mathrm f'(4)=16.67")} to 4 significant figures,')
        + parts([f'apply the Newton-Raphson procedure once to obtain a second approximation for {m(r"\alpha")}, giving your answer to 3 significant figures. {mk(2)}',
                 f'Show that {m(r"\alpha")} is the only root of {m(r"\mathrm f(x)=0")} {mk(2)}'], start=2))
Q[9] = parts(['Prove that' + eq(r'\tan\theta+\cot\theta\equiv 2\operatorname{cosec}2\theta,\qquad \theta\neq\frac{n\pi}{2},\ n\in\mathbb Z') + mk(4),
              'Hence explain why the equation' + eq(r'\tan\theta+\cot\theta=1') + f'does not have any real solutions. {mk(1)}'])
Q[10] = (p(f'Given that {m(r"\theta")} is measured in radians, prove, from first principles, that the derivative of {m(r"\sin\theta")} is {m(r"\cos\theta")}')
         + p(f'You may assume the formula for {m(r"\sin(A\pm B)")} and that as {m(r"h\to 0")}, {m(r"\dfrac{\sin h}{h}\to 1")} and {m(r"\dfrac{\cos h-1}{h}\to 0")} {mk(5)}'))
Q[11] = (p('An archer shoots an arrow.')
         + p(f'The height, {m("H")} metres, of the arrow above the ground is modelled by the formula') + eq(r'H=1.8+0.4d-0.002d^2,\qquad d\geqslant 0')
         + p(f'where {m("d")} is the horizontal distance of the arrow from the archer, measured in metres.')
         + p('Given that the arrow travels in a vertical plane until it hits the ground,')
         + parts([f'find the horizontal distance travelled by the arrow, as given by this model. {mk(3)}',
                  f'With reference to the model, interpret the significance of the constant 1.8 in the formula. {mk(1)}',
                  f'Write {m("1.8+0.4d-0.002d^2")} in the form' + eq('A-B(d-C)^2') + f'where {m("A")}, {m("B")} and {m("C")} are constants to be found. {mk(3)}'])
         + p('It is decided that the model should be adapted for a different archer.')
         + p('The adapted formula for this archer is') + eq(r'H=2.1+0.4d-0.002d^2,\qquad d\geqslant 0')
         + p('Hence or otherwise, find, for the adapted model')
         + parts([parts(['the maximum height of the arrow above the ground.',
                         'the horizontal distance, from the archer, of the arrow when it is at its maximum height.'], kind='i') + mk(2)], start=4))
Q[12] = (p(f'In a controlled experiment, the number of microbes, {m("N")}, present in a culture {m("T")} days after the start of the experiment were counted.')
         + p(f'{m("N")} and {m("T")} are expected to satisfy a relationship of the form') + eq(r'N=aT^b,\qquad\text{where } a \text{ and } b \text{ are constants}')
         + parts(['Show that this relationship can be expressed in the form' + eq(r'\log_{10}N=m\log_{10}T+c')
                  + f'giving {m("m")} and {m("c")} in terms of the constants {m("a")} and/or {m("b")}. {mk(2)}'])
         + fig(12, 65, 'Figure 3: graph of log10 N (0 to 5.0) against log10 T (0 to 1.4) on grid paper, with six plotted crosses and a line of best fit from about (0, 1.85) to about (1.2, 4.6)')
         + p(f'Figure 3 shows the line of best fit for values of {m(r"\log_{10}N")} plotted against values of {m(r"\log_{10}T")}')
         + parts([f'Use the information provided to estimate the number of microbes present in the culture 3 days after the start of the experiment. {mk(4)}',
                  f'Explain why the information provided could not reliably be used to estimate the day when the number of microbes in the culture first exceeds 1 000 000. {mk(2)}',
                  f'With reference to the model, interpret the value of the constant {m("a")}. {mk(1)}'], start=2))
Q[13] = (p(f'The curve {m("C")} has parametric equations') + eq(r'x=2\cos t,\qquad y=\sqrt3\cos 2t,\qquad 0\leqslant t\leqslant\pi')
         + parts([f'Find an expression for {m(D("y", "x"))} in terms of {m("t")}. {mk(2)}'])
         + p(f'The point {m("P")} lies on {m("C")} where {m(r"t=\dfrac{2\pi}{3}")}')
         + p(f'The line {m("l")} is the normal to {m("C")} at {m("P")}.')
         + parts([f'Show that an equation for {m("l")} is' + eq(r'2x-2\sqrt3y-1=0') + mk(5)], start=2)
         + p(f'The line {m("l")} intersects the curve {m("C")} again at the point {m("Q")}.')
         + parts([f'Find the exact coordinates of {m("Q")}.<br>You must show clearly how you obtained your answers. {mk(6)}'], start=3))
Q[14] = (fig(14, 30, 'Figure 4: sketch of the curve C, which decreases from the y-axis to a minimum and then increases, with the region S between the curve and the x-axis from x = 1 to x = 3 shaded')
         + p(f'Figure 4 shows a sketch of part of the curve {m("C")} with equation') + eq(r'y=\frac{x^2\ln x}{3}-2x+5,\qquad x>0')
         + p(f'The finite region {m("S")}, shown shaded in Figure 4, is bounded by the curve {m("C")}, the line with equation {m("x=1")}, the {m("x")}-axis and the line with equation {m("x=3")}')
         + p(f'The table below shows corresponding values of {m("x")} and {m("y")} with the values of {m("y")} given to 4 decimal places as appropriate.')
         + table([[m('x'), '1', '1.5', '2', '2.5', '3'], [m('y'), '3', '2.3041', '1.9242', '1.9089', '2.2958']])
         + parts([f'Use the trapezium rule, with all the values of {m("y")} in the table, to obtain an estimate for the area of {m("S")}, giving your answer to 3 decimal places. {mk(3)}',
                  f'Explain how the trapezium rule could be used to obtain a more accurate estimate for the area of {m("S")}. {mk(1)}',
                  f'Show that the exact area of {m("S")} can be written in the form {m(r"\dfrac ab+\ln c")}, where {m("a")}, {m("b")} and {m("c")} are integers to be found. {mk(6)}'])
         + p('<em>(In part c, solutions based entirely on graphical or numerical methods are not acceptable.)</em>'))
Q[15] = (fig(15, 60, 'Figure 5: sketch of y = f(x) starting at the origin, rising to a maximum P, falling through the x-axis to a minimum Q below it, then approaching the x-axis')
         + p(f'Figure 5 shows a sketch of the curve with equation {m(r"y=\mathrm f(x)")}, where') + eq(r'\mathrm f(x)=\frac{4\sin 2x}{\mathrm e^{\sqrt2x-1}},\qquad 0\leqslant x\leqslant\pi')
         + p(f'The curve has a maximum turning point at {m("P")} and a minimum turning point at {m("Q")} as shown in Figure 5.')
         + parts([f'Show that the {m("x")} coordinates of point {m("P")} and point {m("Q")} are solutions of the equation' + eq(r'\tan 2x=\sqrt2') + mk(4),
                  f'Using your answer to part (a), find the {m("x")}-coordinate of the minimum turning point on the curve with equation'
                  + parts([m(r'y=\mathrm f(2x)') + '.', m(r'y=3-2\mathrm f(x)') + '.'], kind='i') + mk(4)]))
