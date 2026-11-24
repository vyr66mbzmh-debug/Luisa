# PMT Core Pure 2, Ch.1 Complex Numbers (CP2): transcribed from the rendered page images. Wording, part labels and
# marks exactly as printed (source notes are in questions.json and the evidence file).
from lib import *
Q = {}
Q[1] = (p('Solve the equation') + eq(r'z^3+32+32\mathrm i\sqrt3=0')
        + p(f'giving your answers in the form {m(r"r\mathrm e^{\mathrm i\theta}")} where {m("r>0")} and {m(r"-\pi<\theta\leqslant\pi")} {mk(6)}'))
Q[2] = (p(f'The infinite series {m(r"\mathrm C")} and {m(r"\mathrm S")} are defined by')
        + eq(r'\mathrm C=\cos\theta+\frac12\cos5\theta+\frac14\cos9\theta+\frac18\cos13\theta+\dots')
        + eq(r'\mathrm S=\sin\theta+\frac12\sin5\theta+\frac14\sin9\theta+\frac18\sin13\theta+\dots')
        + p(f'Given that the series {m(r"\mathrm C")} and {m(r"\mathrm S")} are both convergent,')
        + parts([p('show that') + eq(r'\mathrm C+\mathrm i\mathrm S=\frac{2\mathrm e^{\mathrm i\theta}}{2-\mathrm e^{4\mathrm i\theta}}') + mk(4),
                 p('Hence show that') + eq(r'\mathrm S=\frac{4\sin\theta+2\sin3\theta}{5-4\cos4\theta}') + mk(4)], kind='a'))
Q[3] = parts([p("Use de Moivre's theorem to prove that") + eq(r'\sin7\theta=7\sin\theta-56\sin^3\theta+112\sin^5\theta-64\sin^7\theta') + mk(5),
              p('Hence find the distinct roots of the equation') + eq(r'1+7x-56x^3+112x^5-64x^7=0') + mk(5)
              + p('giving your answer to 3 decimal places where appropriate.')], kind='a')
Q[4] = parts([p(f'Given that {m("|z|<1")}, write down the sum of the infinite series') + eq(r'1+z+z^2+z^3+\dots') + mk(1),
              p(f'Given that {m(r"z=\dfrac12(\cos\theta+\mathrm i\sin\theta)")},')
              + parts([p("use the answer to part (a), and de Moivre's theorem or otherwise, to prove that")
                       + eq(r'\frac12\sin\theta+\frac14\sin2\theta+\frac18\sin3\theta+\dots=\frac{2\sin\theta}{5-4\cos\theta}') + mk(5),
                       f'show that the sum of the infinite series {m(r"1+z+z^2+z^3+\dots")} cannot be purely imaginary, giving a reason for your answer. {mk(2)}'], kind='i')], kind='a')
Q[5] = (p(f'In an Argand diagram, the points {m("A")}, {m("B")} and {m("C")} are the vertices of an equilateral triangle with its centre at the origin. The point A represents the complex number {m(r"6+2\mathrm i")}.')
        + parts([f'Find the complex numbers represented by the points B and C, giving your answers in the form {m(r"x+\mathrm iy")}, where {m("x")} and {m("y")} are real and exact. {mk(6)}'], kind='a')
        + p(f'The points {m("D")}, {m("E")} and {m("F")} are the midpoints of the sides of triangle {m("ABC")}.')
        + parts([f'Find the exact area of triangle {m("DEF")}. {mk(3)}'], start=2, kind='a'))
Q[6] = (p(f'A complex number {m("z")} has modulus 1 and argument {m(r"\theta")}.')
        + parts([p('Show that') + eq(r'z^n+\frac{1}{z^n}=2\cos n\theta,\qquad n\in\mathbb Z^+') + mk(2),
                 p('Hence, show that') + eq(r'\cos^4\theta=\frac18(\cos4\theta+4\cos2\theta+3)') + mk(5)], kind='a'))
Q[7] = parts([f'Find the four roots of the equation {m(r"z^4=8(\sqrt3+\mathrm i)")} in the form {m(r"z=r\mathrm e^{\mathrm i\theta}")} {mk(5)}',
              f'Show these roots on an Argand diagram. {mk(2)}'], kind='a')
Q[8] = parts([p("Use de Moivre's theorem to show that") + eq(r'\sin^5\theta\equiv a\sin5\theta+b\sin3\theta+c\sin\theta')
              + p(f'where {m("a")}, {m("b")} and {m("c")} are constants to be found.') + mk(5),
              f'Hence show that {m(r"\displaystyle\int_0^{\frac{\pi}{3}}\sin^5\theta\,\mathrm d\theta=\frac{53}{480}")} {mk(5)}'], kind='a')
Q[9] = parts([p(f'The point {m("P")} is one vertex of a regular pentagon in an Argand diagram. The centre of the pentagon is at the origin.')
              + p(f'Given that {m("P")} represents the complex number {m(r"6+6\mathrm i")}, determine the complex numbers that represent the other vertices of the pentagon, giving your answers in the form {m(r"r\mathrm e^{\mathrm i\theta}")}') + mk(5),
              parts([p(f'On a single Argand diagram, shade the region, {m("R")}, that satisfies both')
                     + eq(r'|z-2\mathrm i|\leqslant2\qquad\text{and}\qquad\frac14\pi\leqslant\arg z\leqslant\frac13\pi') + mk(2),
                     f'Determine the exact area of {m("R")}, giving your answer in simplest form. {mk(4)}'], kind='a')], kind='i')
Q[10] = parts([f'Express the complex number {m(r"w=4\sqrt3-4\mathrm i")} in the form {m(r"r(\cos\theta\ \theta+\mathrm i\sin\theta)")} where {m("r>0")} and {m(r"-\pi<\theta\leqslant\pi")} {mk(4)}',
               'Show, on a single Argand diagram,' + parts([f'the point representing {m("w")}', f'the locus of points defined by {m(r"\arg(z+10\mathrm i)=\dfrac{\pi}{3}")}'], kind='i') + mk(3),
               f'Hence determine the minimum distance of {m("w")} from the locus {m(r"\arg(z+10\mathrm i)=\dfrac{\pi}{3}")} {mk(3)}'], kind='a')
Q[11] = parts([p('Given that') + eq(r'z_1=6\mathrm e^{\frac{\pi}{3}\mathrm i}\ \text{ and }\ z_2=6\sqrt3\,\mathrm e^{\frac{5\pi}{6}\mathrm i}')
               + p('show that') + eq(r'z_1+z_2=12\mathrm e^{\frac{2\pi}{3}\mathrm i}') + mk(3),
               p('Given that') + eq(r'\arg(z-5)=\frac{2\pi}{3}') + p(f'determine the least value of {m("|z|")} as {m("z")} varies.') + mk(3)], kind='i')
