# PMT Core Pure 1, Ch.4 Roots of Polynomials: transcribed from the rendered page images. Wording, part labels and marks
# exactly as printed. Q4 and Q5 print no part mark (only the question total), so none is added.
from lib import *
Q = {}
def transform(eqn, roots, form, coeffs, marks):
    return (p('The cubic equation') + eq(eqn) + p(f'has roots {m(r"\alpha")}, {m(r"\beta")} and {m(r"\gamma")}.')
            + p(f'Without solving the equation, find the cubic equation whose roots are {roots}, giving your answer in the form {m(form)}, where {coeffs}' + (f' {mk(marks)}' if marks else '')))
Q[1] = transform(r'z^3-3z^2+z+5=0', f'{m(r"(2\alpha+1)")}, {m(r"(2\beta+1)")} and {m(r"(2\gamma+1)")}', r'w^3+pw^2+qw+r=0',
                 f'{m("p")}, {m("q")} and {m("r")} are integers to be found.', 5)
Q[2] = (p('The cubic equation') + eq(r'3x^3+x^2-4x+1=0') + p(f'has roots {m(r"\alpha,\ \beta,\text{ and }\gamma.")}')
        + p('Without solving the cubic equation,')
        + parts([f'determine the value of {m(r"\dfrac{1}{\alpha}+\dfrac{1}{\beta}+\dfrac{1}{\gamma}")} {mk(3)}',
                 f'find a cubic equation that has roots {m(r"\dfrac{1}{\alpha},\ \dfrac{1}{\beta}\text{ and }\dfrac{1}{\gamma},")} giving your answer in the form<br>'
                 f'{m("x^3+ax^2+bx+c=0")}, where {m("a")}, {m("b")} and {m("c")} are integers to be determined. {mk(3)}'], kind='a'))
Q[3] = transform(r'x^3+3x^2-8x+6=0', f'{m(r"(\alpha-1)")}, {m(r"(\beta-1)")} and {m(r"(\gamma-1)")}', r'w^3+pw^2+qw+r=0',
                 f'{m("p")}, {m("q")} and {m("r")} are integers to be found.', 5)
Q[4] = transform(r'2x^3+6x^2-3x+12=0', f'{m(r"(\alpha+3)")}, {m(r"(\beta+3)")} and {m(r"(\gamma+3)")}', r'pw^3+qw^2+rw+s=0',
                 f'{m("p")}, {m("q")}, {m("r")} and {m("s")} are integers to be found.', None)
Q[5] = transform(r'9x^3-5x^2+4x+7=0', f'{m(r"(3\alpha-2)")}, {m(r"(3\beta-2)")} and {m(r"(3\gamma-2)")}', r'aw^3+bw^2+cw+d=0',
                 f'{m("a")}, {m("b")}, {m("c")} and {m("d")} are integers to be determined.', None)
Q[6] = (p('The roots of the quartic equation') + eq(r'3x^4+5x^3-7x+6=0') + p(f'are {m(r"\alpha")}, {m(r"\beta")}, {m(r"\gamma")} and {m(r"\delta")}')
        + p('Making your method clear and without solving the equation, determine the exact value of')
        + parts([f'{m(r"\alpha^2+\beta^2+\gamma^2+\delta^2")} {mk(3)}',
                 f'{m(r"\dfrac{2}{\alpha}+\dfrac{2}{\beta}+\dfrac{2}{\gamma}+\dfrac{2}{\delta}")} {mk(3)}',
                 f'{m(r"(3-\alpha)(3-\beta)(3-\gamma)(3-\delta)")} {mk(3)}'], kind='i'))
