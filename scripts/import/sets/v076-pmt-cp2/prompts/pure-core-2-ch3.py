# PMT Core Pure 2, Ch.3 Methods in Calculus: transcribed from the rendered page images. Wording, part labels and
# marks exactly as printed. Q2 prints only the question total.
from lib import *
Q = {}
Q[1] = parts([p('Given that') + eq(r'y=\arcsin x\qquad\qquad-1\leqslant x\leqslant1') + p('show that') + eq(r'\frac{\mathrm dy}{\mathrm dx}=\frac{1}{\sqrt{1-x^2}}') + mk(3),
              eq(r'\mathrm f(x)=\arcsin(\mathrm e^x)\ \ x\leqslant0') + p(f'Prove that {m(r"\mathrm f(x)")} has no stationary points.') + mk(3)], kind='a')
Q[2] = (p('Show that') + eq(r'\int_0^{\infty}\frac{8x-12}{(2x^2+3)(x+1)}\,\mathrm dx=\ln k')
        + p(f'where {m("k")} is a rational number to be found.'))
Q[3] = (p(f'Given that {m(r"y=\operatorname{arsinh}(\tanh x)")}, show that') + eq(r'\frac{\mathrm dy}{\mathrm dx}=\frac{\operatorname{sech}^2x}{\sqrt{1+\tanh^2x}}') + p(mk(5)))
Q[4] = (p(f'The curve {m("C")} has equation') + eq(r'y=\arccos\left(\frac12x\right)\qquad-2\leqslant x\leqslant2')
        + parts([f'Show that {m("C")} has no stationary points. {mk(3)}'], kind='a')
        + p(f'The normal to {m("C")}, at the point where {m("x=1")}, crosses the {m("x")}-axis at the point {m("A")} and crosses the {m("y")}-axis at the point {m("B")}.')
        + p(f'Given that {m("O")} is the origin,')
        + parts([f'show that the area of the triangle {m("OAB")} is {m(r"\dfrac{1}{54}\left(p\sqrt3+q\pi+r\sqrt3\,\pi^2\right)")} where {m("p")}, {m("q")} and {m("r")} are integers to be determined. {mk(5)}'], start=2, kind='a'))
Q[5] = parts([f'Explain why {m(r"\displaystyle\int_1^{\infty}\frac{1}{x(2x+5)}\,\mathrm dx")} is an improper integral. {mk(1)}',
              p('Prove that') + eq(r'\int_1^{\infty}\frac{1}{x(2x+5)}\,\mathrm dx=a\ln b') + p(f'where {m("a")} and {m("b")} are rational numbers to be determined.') + mk(6)], kind='a')
Q[6] = (eq(r'\mathrm f(x)=\frac{x+2}{x^2+9}')
        + parts([p('Show that') + eq(r'\int\mathrm f(x)\,\mathrm dx=A\ln(x^2+9)+B\arctan\left(\frac{x}{3}\right)+c')
                 + p(f'where {m("c")} is an arbitrary constant and {m("A")} and {m("B")} are constants to be found.') + mk(4),
                 p(f'Hence show that the mean value of {m(r"\mathrm f(x)")} over the interval {m("[0,3]")} is') + eq(r'\frac16\ln2+\frac{1}{18}\pi') + mk(3),
                 p(f'Use the answer to part (b) to find the mean value, over the interval {m("[0,3]")}, of') + eq(r'\mathrm f(x)+\ln k')
                 + p(f'where {m("k")} is a positive constant, giving your answer in the form {m(r"p+\dfrac16\ln q")}, {m("p")} and {m("q")} are constants and {m("q")} is in terms of {m("k")}.') + mk(2)], kind='a'))
Q[7] = parts([p('Express as partial fractions') + eq(r'\frac{2x^2+3x+6}{(x+1)(x^2+4)}') + mk(3),
              p('Hence, show that') + eq(r'\int_0^2\frac{2x^2+3x+6}{(x+1)(x^2+4)}\,\mathrm dx=\ln\left(a\sqrt2\right)+b\pi')
              + p(f'where {m("a")} and {m("b")} are constants to be determined.') + mk(4)], kind='a')
