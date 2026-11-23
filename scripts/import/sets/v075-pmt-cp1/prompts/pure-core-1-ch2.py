# PMT Core Pure 1, Ch.2 Argand Diagrams: transcribed from the rendered page images. Wording, part labels and
# marks exactly as printed (source notes are in questions.json and the evidence file).
from lib import *
Q = {}
Q[1] = (parts([p('Shade on an Argand diagram the set of points')
               + eq(r'\{z\in\mathbb C:|z-1-\mathrm i|\leqslant3\}\cap\left\{z\in\mathbb C:\frac{\pi}{4}\leqslant\arg(z-2)\leqslant\frac{3\pi}{4}\right\}') + mk(5)], kind='a')
        + p(f'The complex number {m("w")} satisfies') + eq(r'|w-1-\mathrm i|=3\ \text{ and }\ \arg(w-2)=\frac{\pi}{4}')
        + parts([f'Find, in simplest form, the exact value of {m("|w|^2")} {mk(4)}'], start=2, kind='a'))
Q[2] = (p(f'Given that there are two distinct complex numbers {m("z")} that satisfy')
        + eq(r'\{z:|z-3-5\mathrm i|=2r\}\cap\left\{z:\arg(z-2)=\frac{3\pi}{4}\right\}')
        + p(f'determine the exact range of values for the real constant {m("r")}. {mk(7)}'))
Q[3] = (parts([p('Shade on an Argand diagram the set of points')
               + eq(r'\{z\in\mathbb C:|z-4\mathrm i|\leqslant3\}\cap\left\{z\in\mathbb C:-\frac{\pi}{2}<\arg(z+3-4\mathrm i)\leqslant\frac{\pi}{4}\right\}') + mk(6)], kind='a')
        + p(f'The complex number {m("w")} satisfies') + eq(r'|w-4\mathrm i|=3')
        + parts([f'Find the maximum value of arg {m("w")} in the interval {m(r"(-\pi,\pi]")}.<br>Give your answer in radians correct to 2 decimal places. {mk(2)}'], start=2, kind='a'))
Q[4] = (eq(r'\mathrm f(z)=z^3+z^2+pz+q') + p(f'where {m("p")} and {m("q")} are real constants.')
        + p(f'The equation {m(r"\mathrm f(z)=0")} has roots {m("z_1")}, {m("z_2")} and {m("z_3")}<br>When plotted on an Argand diagram, the points representing {m("z_1")}, {m("z_2")} and {m("z_3")} form the vertices of a triangle of area 35')
        + p(f'Given that {m("z_1=3")}, find the values of {m("p")} and {m("q")}. {mk(7)}'))
Q[5] = (p(f'{m(r"\mathrm f(z)=z^3+az+52")}&emsp;&emsp;where {m("a")} is a real constant')
        + p(f'Given that {m(r"2-3\mathrm i")} is a root of the equation {m(r"\mathrm f(z)=0")}')
        + parts([f'write down the other complex root. {mk(1)}',
                 'Hence' + parts([f'solve completely {m(r"\mathrm f(z)=0")}', f'determine the value of {m("a")}'], kind='i') + mk(4),
                 f'Show all the roots of the equation {m(r"\mathrm f(z)=0")} on a single Argand diagram. {mk(1)}'], kind='a'))
Q[6] = (fig(6, 70, 'Figure 1: Argand diagram with axes x and y, origin O, and the points z1 on the negative real axis, z2 above and to the left of O, and z3 above and to the right of O', 1)
        + p(f'The complex numbers {m("z_1=-2")}, {m(r"z_2=-1+2\mathrm i")} and {m(r"z_3=1+\mathrm i")} are plotted in Figure 1, on an Argand diagram for the complex plane with {m(r"z=x+\mathrm iy")}')
        + parts([f'Explain why {m("z_1")}, {m("z_2")} and {m("z_3")},cannot all be roots of a quartic polynomial equation with real coefficients. {mk(2)}',
                 f'Show that arg {m(r"\left(\dfrac{z_2-z_1}{z_3-z_1}\right)=\dfrac{\pi}{4}")} {mk(3)}',
                 f'Hence show that {m(r"\arctan(2)-\arctan\left(\dfrac13\right)=\dfrac{\pi}{4}")} {mk(2)}',
                 fig(6, 70, 'Diagram 1: a copy of Figure 1 (axes x and y, origin O, points z1, z2 and z3) for shading', 2)
                 + p('Shade, on Diagram 1, the set of points of the complex plane that satisfy the inequality') + eq(r'|z+2|\leqslant|z-1-\mathrm i|') + mk(2)], kind='a'))
Q[7] = parts([f'Express the complex number {m(r"w=4\sqrt3-4\mathrm i")} in the form {m(r"r(\cos\theta\ \theta+\mathrm i\sin\theta)")} where {m("r>0")} and {m(r"-\pi<\theta\leqslant\pi")} {mk(4)}',
              'Show, on a single Argand diagram,' + parts([f'the point representing {m("w")}', f'the locus of points defined by {m(r"\arg(z+10\mathrm i)=\dfrac{\pi}{3}")}'], kind='i') + mk(3),
              f'Hence determine the minimum distance of {m("w")} from the locus {m(r"\arg(z+10\mathrm i)=\dfrac{\pi}{3}")} {mk(3)}'], kind='a')
Q[8] = (fig(8, 95, 'Figure 1: Argand diagram on a unit grid, Re from -5 to 1 and Im from -1 to 3, showing a shaded ring between two circles centred at -2 + i: the outer circle passes through -4 + i, 0 + i, -2 + 3i and -2 - i; the inner circle passes through -2 + 2i and -2 (on the real axis)')
        + p('Figure 1 shows an Argand diagram.')
        + p(f'The set {m("P")}, of points that lie within the shaded region including its boundaries, is defined by')
        + eq(r'P=\{z\in\mathbb C:a\leqslant|z+b+c\mathrm i|\leqslant d\}')
        + p(f'where {m("a")}, {m("b")}, {m("c")} and {m("d")} are integers.')
        + parts([f'Write down the values of {m("a")}, {m("b")}, {m("c")} and {m("d")}. {mk(3)}'], kind='a')
        + p(f'The set {m("Q")} is defined by') + eq(r'Q=\{z\in\mathbb C:a\leqslant|z+b+c\mathrm i|\leqslant d\}\cap\{z\in\mathbb C:|z-\mathrm i|\leqslant|z-3\mathrm i|\}')
        + parts([f'Determine the exact area of the region defined by {m("Q")}, giving your answer in simplest form. {mk(7)}'], start=2, kind='a'))
Q[9] = (eq(r'\mathrm f\ (z)=z^4+az^3+bz^2+cz+d') + p(f'where {m("a")}, {m("b")}, {m("c")} and {m("d")} are real constants.')
        + p(f'Given that {m(r"-1+2\mathrm i")} and {m(r"3-\mathrm i")} are two roots of the equation {m(r"\mathrm f\ (z)=0")}')
        + parts([f'show all the roots of {m(r"\mathrm f\ (z)=0")} on a single Argand diagram, {mk(4)}',
                 f'find the values of {m("a")}, {m("b")}, {m("c")} and {m("d")}. {mk(5)}'], kind='a'))
Q[10] = (eq(r'\mathrm f(z)=z^4+az^3+bz^2+cz+d') + p(f'where {m("a")}, {m("b")}, {m("c")} and {m("d")} are real constants.')
         + p(f'The equation {m(r"\mathrm f(z)=0")} has complex roots {m("z_1")}, {m("z_2")}, {m("z_3")} and {m("z_4")}<br>When plotted on an Argand diagram, the points representing {m("z_1")}, {m("z_2")}, {m("z_3")} and {m("z_4")} form the vertices of a square, with one vertex in each quadrant.<br>'
             f'Given that {m(r"z_1=2+3\mathrm i")}, determine the values of {m("a")}, {m("b")}, {m("c")} and {m("d")}. {mk(6)}'))
Q[11] = (p('Given that') + eq(r'\begin{aligned}z_1&=2+3\mathrm i\\|z_1z_2|&=39\sqrt2\\\arg(z_1z_2)&=\frac{\pi}{4}\end{aligned}')
         + p(f'where {m("z_1")} and {m("z_2")} are complex numbers,')
         + parts([f'write {m("z_1")} in the form {m(r"r(\cos\theta+\mathrm i\sin\theta)")}<br>Give the exact value of {m("r")} and give the value of {m(r"\theta")} in radians to 4 significant figures. {mk(2)}',
                  f'Find {m("z_2")} giving your answer in the form {m(r"a+\mathrm ib")} where {m("a")} and {m("b")} are integers. {mk(6)}'], kind='a'))
