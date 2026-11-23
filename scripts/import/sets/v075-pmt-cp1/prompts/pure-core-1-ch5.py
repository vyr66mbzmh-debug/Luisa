# PMT Core Pure 1, Ch.5 Volumes of Revolution: transcribed from the rendered page images. Wording, part labels and
# marks exactly as printed.
from lib import *
Q = {}
Q[1] = (p('Diagrams not drawn to scale')
        + fig(1, 95, 'Figure 1: cross-section AOBCD of a bird bath: vertical sides AD and BC of height 1.16 m, base AB of width 0.4 m with O its midpoint, and a curved bowl CD between the tops of the sides. '
              'Figure 2: the curve CD on x and y axes, symmetric about the y-axis, between x = -0.2 and x = 0.2, with dashed vertical lines from D and C down to the x-axis')
        + p(f'Figure 1 shows the central cross-section {m("AOBCD")} of a circular bird bath, which is made of concrete. Measurements of the height and diameter of the bird bath, and the depth of the bowl of the bird bath have been taken in order to estimate the amount of concrete that was required to make this bird bath.')
        + p(f'Using these measurements, the cross-sectional curve {m("CD")}, shown in Figure 2, is modelled as a curve with equation')
        + eq(r'y=1+kx^2\qquad-0.2\leqslant x\leqslant0.2')
        + p(f'where {m("k")} is a constant and where {m("O")} is the fixed origin.')
        + p(f'The height of the bird bath measured 1.16 m and the diameter, {m("AB")}, of the base of the bird bath measured 0.40 m, as shown in Figure 1.')
        + parts([f'Suggest the maximum depth of the bird bath. {mk(1)}',
                 f'Find the value of {m("k")}. {mk(2)}',
                 f'Hence find the volume of concrete that was required to make the bird bath according to this model. Give your answer, in {m(r"\mathrm m^3")}, correct to 3 significant figures. {mk(7)}',
                 f'State a limitation of the model. {mk(1)}'], kind='a')
        + p(f'It was later discovered that the volume of concrete used to make the bird bath was {m(r"0.127\ \mathrm m^3")} correct to 3 significant figures.')
        + parts([f'Using this information and the answer to part (c), evaluate the model, explaining your reasoning. {mk(1)}'], start=5, kind='a'))
Q[2] = (eq(r'\mathrm f(x)=2x^{\frac13}+x^{-\frac23}\qquad x>0')
        + p(f'The finite region bounded by the curve {m(r"y=\mathrm f(x)")}, the line {m(r"x=\dfrac18")}, the {m("x")}-axis and the line {m("x=8")} is rotated through {m(r"\theta")} radians about the {m("x")}-axis to form a solid of revolution.')
        + p(f'Given that the volume of the solid formed is {m(r"\dfrac{461}{2}")} units cubed, use algebraic integration to find the angle {m(r"\theta")} through which the region is rotated. {mk(8)}'))
Q[3] = (fig(3, 45, 'Figure 1: a circle centred at the origin O on x and y axes; the upper half, above the x-axis, is shaded and labelled R')
        + p(f'Figure 1 shows a circle with radius {m("r")} and centre at the origin.<br>The region {m("R")}, shown shaded in Figure 1, is bounded by the {m("x")}-axis and the part of the circle for which {m("y>0")}<br>'
            f'The region R is rotated through {m(r"360^\circ")} about the {m("x")}-axis to create a sphere with volume {m("V")}')
        + p(f'Use integration to show that {m(r"V=\dfrac43\pi r^3")} {mk(5)}'))
Q[4] = (fig(4, 40, 'Figure 2: vertical cross-section AOBCDE of a candle on x and y axes: A and B on the x-axis either side of O, curved sides rising from A to E and from B to C, and a curved top through E, D (on the y-axis) and C')
        + p(f'Figure 2 shows the vertical cross-section, {m("AOBCDE")}, through the centre of a wax candle.')
        + p(f'In a model, the candle is formed by rotating the region bounded by the {m("y")}-axis, the line {m("OB")}, the curve {m("BC")}, and the curve {m("CD")} through {m(r"360^\circ")} about the {m("y")}-axis.')
        + p(f'The point {m("B")} has coordinates (3, 0) and the point {m("C")} has coordinates (5, 15).')
        + p('The units are in centimetres.')
        + p(f'The curve {m("BC")} is represented by the equation') + eq(r'y=\frac{\sqrt{225x^2-2025}}{a}\qquad3\leqslant x<5')
        + p(f'where {m("a")} is a constant.')
        + parts([f'Determine the value of {m("a")} according to this model. {mk(2)}'], kind='a')
        + p(f'The curve {m("CD")} is represented by the equation') + eq(r'y=16-0.04x^2\qquad0\leqslant x<5')
        + parts([f'Using algebraic integration, determine, according to the model, the exact volume of wax that would be required to make the candle. {mk(9)}',
                 f'State a limitation of the model. {mk(1)}'], start=2, kind='a')
        + p(f'When the candle was manufactured, {m(r"700\ \mathrm{cm}^3")} of wax were required.')
        + parts([f'Use this information and your answer to part (b) to evaluate the model, explaining your reasoning. {mk(1)}'], start=4, kind='a'))
Q[5] = (fig(5, 90, 'Figure 1: sketch of a vase 16 cm tall with a flat circular base of diameter 8 cm and a circular opening of diameter 8 cm, wider near the base and narrower near the top. '
              'Figure 2: a curve on x and y axes from (-8, a) at the base, through (0, a), to (8, a) at the top, rising above y = a for negative x and dipping below it for positive x')
        + p('Figure 1 shows a sketch of a 16 cm tall vase which has a flat circular base with diameter 8 cm and a circular opening of diameter 8 cm at the top.')
        + p('A student measures the circular cross-section halfway up the vase to be 8 cm in diameter.')
        + p(f'The student models the shape of the vase by rotating a curve, shown in Figure 2, through {m(r"360^\circ")} about the {m("x")}-axis.')
        + parts([f'State the value of {m("a")} that should be used when setting up the model. {mk(1)}'], kind='a')
        + p('Two possible equations are suggested for the curve in the model.')
        + eq(r'\begin{aligned}&\text{Model A}\qquad y=a-2\sin\left(\frac{45}{2}x\right)^{\circ}\\&\text{Model B}\qquad y=a+\frac{x(x-8)(x+8)}{100}\end{aligned}')
        + p('For each model,')
        + parts(['' + parts(['find the distance from the base at which the widest part of the vase occurs,', 'find the diameter of the vase at this widest point.'], kind='i') + mk(7)], start=2, kind='a')
        + p('The widest part of the vase has diameter 12 cm and is just over 3 cm from the base.')
        + parts([f'Using this information and making your reasoning clear, suggest which model is more appropriate. {mk(1)}',
                 f'Using algebraic integration, find the volume for the vase predicted by Model B.<br>You must make your method clear. {mk(5)}'], start=3, kind='a')
        + p('The student pours water from a full one litre jug into the vase and finds that there is 100 ml left in the jug when the vase is full.')
        + parts([f'Comment on the suitability of Model B in light of this information. {mk(1)}'], start=5, kind='a'))
