# PMT Core Pure 2, Ch.6 Hyperbolic Functions: transcribed from the rendered page images. Wording, part labels and
# marks exactly as printed; figures are source crops with their printed captions. Q3 and Q6 print only the total.
from lib import *
Q = {}
Q[1] = (p(f'Given that {m(r"y=\operatorname{arsinh}(\tanh x)")}, show that') + eq(r'\frac{\mathrm dy}{\mathrm dx}=\frac{\operatorname{sech}^2x}{\sqrt{1+\tanh^2x}}') + p(mk(5)))
Q[2] = (eq(r'\mathrm f(x)=\frac{1}{\sqrt{4x^2+9}}')
        + parts([p('Using a substitution, that should be stated clearly, show that') + eq(r'\int\mathrm f(x)\,\mathrm dx=A\sinh^{-1}(Bx)+c')
                 + p(f'where {m("c")} is an arbitrary constant and {m("A")} and {m("B")} are constants to be found.') + mk(4),
                 f'Hence find, in exact form in terms of natural logarithms, the mean value of {m(r"\mathrm f(x)")} over the interval {m("[0,3]")}. {mk(2)}'], kind='a'))
Q[3] = (p(f'The curve {m("C")} has equation') + eq(r'y=31\sinh x-2\sinh2x\qquad x\in\mathbb R')
        + p(f'Determine, in terms of natural logarithms, the exact {m("x")} coordinates of the stationary points of {m("C")}.'))
Q[4] = parts([p(f'Using the definition for {m(r"\cosh x")} in terms of exponentials, show that') + eq(r'\cosh2x\equiv2\cosh^2x-1') + mk(3),
              p(f'Find the exact values of {m("x")} for which') + eq(r'29\cosh x-3\cosh2x=38') + p('giving your answers in terms of natural logarithms.') + mk(6)], kind='a')
Q[5] = parts([p('Prove that') + eq(r'\tanh^{-1}(x)=\frac12\ln\left(\frac{1+x}{1-x}\right)\qquad-k<x<k') + p(f'stating the value of the constant {m("k")}.') + mk(5),
              p('Hence, or otherwise, solve the equation') + eq(r'2x=\tanh\left(\ln\sqrt{2-3x}\right)') + mk(5)], kind='a')
Q[6] = (bold('In this question you must show all stages of your working.') + bold('Solutions relying entirely on calculator technology are not acceptable.')
        + p(f'Determine the values of {m("x")} for which') + eq(r'64\cosh^4x-64\cosh^2x-9=0')
        + p(f'Give your answers in the form {m(r"q\ln2")} where {m("q")} is rational and in simplest form.'))
Q[7] = (bold('Solutions based entirely on graphical or numerical methods are not acceptable.')
        + fig(7, 80, 'Figure 1: axes x and y with origin O; the curve y = arsinh x rising from O and levelling off; a dashed horizontal line y = β; the region R between the y-axis, the curve and the line y = β is shaded')
        + p('Figure 1 shows a sketch of part of the curve with equation') + eq(r'y=\operatorname{arsinh}x\qquad x\geqslant0')
        + p(f'and the straight line with equation {m(r"y=\beta")}')
        + p(f'The line and the curve intersect at the point with coordinates {m(r"(\alpha,\beta)")}')
        + p(f'Given that {m(r"\beta=\dfrac12\ln3")}')
        + parts([f'show that {m(r"\alpha=\dfrac{1}{\sqrt3}")} {mk(3)}'], kind='a')
        + p(f'The finite region {m("R")}, shown shaded in Figure 1, is bounded by the curve with equation {m(r"y=\operatorname{arsinh}x")}, the {m("y")}-axis and the line with equation {m(r"y=\beta")}')
        + p(f'The region {m("R")} is rotated through {m(r"2\pi")} radians about the {m("y")}-axis.')
        + parts([f'Use calculus to find the exact value of the volume of the solid generated. {mk(6)}'], start=2, kind='a'))
Q[8] = (parts([p('Use a hyperbolic substitution and calculus to show that') + eq(r'\int\frac{x^2}{\sqrt{x^2-1}}\,\mathrm dx=\frac12\left[x\sqrt{x^2-1}+\operatorname{arcosh}x\right]+k')
               + p(f'where {m("k")} is an arbitrary constant.') + mk(6)], kind='a')
        + fig(8, 70, 'Figure 1: axes x and y with origin O; the curve C rising from the x-axis to the right of O; the region R under C between the curve, the x-axis and the vertical line x = 3 is shaded')
        + p(f'Figure 1 shows a sketch of part of the curve {m("C")} with equation') + eq(r'y=\frac{4}{15}x\operatorname{arcosh}x\qquad x\geqslant1')
        + p(f'The finite region {m("R")}, shown shaded in Figure 1, is bounded by the curve {m("C")}, the {m("x")}-axis and the line with equation {m("x=3")}')
        + parts([p(f'Using algebraic integration and the result from part (a), show that the area of {m("R")} is given by') + eq(r'\frac{1}{15}\left[17\ln\left(3+2\sqrt2\right)-6\sqrt2\right]') + mk(5)], start=2, kind='a'))
Q[9] = parts([parts([f'Explain why {m(r"\displaystyle\int_0^{\infty}\cosh x\,\mathrm dx")} is an improper integral. {mk(1)}',
                     f'Show that {m(r"\displaystyle\int_0^{\infty}\cosh x\,\mathrm dx")} is divergent. {mk(3)}'], kind='a'),
              eq(r'4\sinh x=p\cosh x\qquad\text{where }p\text{ is a real constant}')
              + p(f'Given that this equation has real solutions, determine the range of possible values for {m("p")}') + mk(2)], kind='i')
