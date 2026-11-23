# PMT Core Pure 1, Ch.1 Complex Numbers: transcribed from the rendered page images (inline maths in the
# PDF is embedded as images). Wording, part labels and marks exactly as printed.
from lib import *
Q = {}
Q[1] = parts([
    p(f'The complex number {m("w")} is given by') + eq(r'w=\frac{p-4\mathrm i}{2-3\mathrm i}')
    + p(f'where {m("p")} is a real constant.')
    + parts([f'Express {m("w")} in the form {m(r"a+b\mathrm i")}, where {m("a")} and {m("b")} are real constants.<br>Give your answer in its simplest form in terms of {m("p")}. {mk(3)}',
             f'Given that arg {m(r"w=\dfrac{\pi}{4}")}<br>find the value of {m("p")}. {mk(2)}'], kind='a'),
    p(f'The complex number {m("z")} is given by') + eq(r'z=(1-\lambda\mathrm i)(4+3\mathrm i)')
    + p(f'where {m(r"\lambda")} is a real constant.<br>Given that') + eq(r'|z|=45')
    + p(f'find the possible values of {m(r"\lambda")}<br>Give your answers as exact values in their simplest form. {mk(3)}'),
], kind='i')
Q[2] = (p(f'Given that 4 and {m(r"2\mathrm i-3")} are roots of the equation') + eq(r'x^3+ax^2+bx-52=0')
        + p(f'where {m("a")} and {m("b")} are real constants,')
        + parts([f'write down the third root of the equation, {mk(1)}',
                 f'find the value of {m("a")} and the value of {m("b")}. {mk(5)}'], kind='a'))
Q[3] = (eq(r'\mathrm f(z)=z^4-6z^3+pz^2+qz+r') + p(f'where {m("p")}, {m("q")} and {m("r")} are real constants.')
        + p(f'The roots of the equation {m(r"\mathrm f(z)=0")} are {m(r"\alpha")}, {m(r"\beta")}, {m(r"\gamma")} and {m(r"\delta")} where {m(r"\alpha=3")} and {m(r"\beta=2+\mathrm i")}')
        + p(f'Given that {m(r"\gamma")} is a complex root of {m(r"\mathrm f(z)=0")}')
        + parts([parts([f'write down the root {m(r"\gamma")},', f'explain why {m(r"\delta")} must be real.'], kind='i') + mk(2),
                 f'Determine the value of {m(r"\delta")}. {mk(2)}',
                 f'Hence determine the values of {m("p")}, {m("q")} and {m("r")}. {mk(3)}',
                 f'Write down the roots of the equation {m(r"\mathrm f(-2z)=0")} {mk(2)}'], kind='a'))
Q[4] = (p(f'Given that {m(r"z=a+b\mathrm i")} is a complex number where {m("a")} and {m("b")} are real constants,')
        + parts([f'show that {m("zz^*")} is a real number. {mk(2)}'], kind='a')
        + p('Given that') + ul([m('zz^*=18'), m(r'\dfrac{z}{z^*}=\dfrac{7}{9}+\dfrac{4\sqrt2}{9}\mathrm i')])
        + parts([f'determine the possible complex numbers {m("z")} {mk(5)}'], start=2, kind='a'))
Q[5] = (p('Let') + eq(r'\mathrm f(z)=z^3-8z^2+pz-24') + p(f'where {m("p")} is a real constant.<br>Given that the equation {m(r"\mathrm f(z)=0")} has distinct roots')
        + eq(r'\alpha,\ \beta\ \text{ and }\left(\alpha+\frac{12}{\alpha}-\beta\right)')
        + parts([f'solve completely the equation {m(r"\mathrm f(z)=0")} {mk(6)}', f'Hence find the value of {m("p")}. {mk(2)}'], kind='a'))
Q[6] = (p('Let') + eq(r'\mathrm f(z)=z^3+pz^2+qz-15') + p(f'where {m("p")} and {m("q")} are real constants.<br>Given that the equation {m(r"\mathrm f(z)=0")} has roots')
        + eq(r'\alpha,\frac{5}{\alpha}\ \text{ and }\left(\alpha+\frac{5}{\alpha}-1\right)')
        + parts([f'solve completely the equation {m(r"\mathrm f(z)=0")} {mk(5)}', f'Hence find the value of {m("p")}. {mk(2)}'], kind='a'))
Q[7] = (p('Let') + eq(r'z=\frac{4}{1+\mathrm i}') + p(f'Find, in the form {m(r"a+\mathrm ib")} where {m(r"a,b\in\mathbb R")}')
        + parts([f'{m("z")} {mk(2)}', f'{m("z^2")} {mk(2)}'], kind='a')
        + p(f'Given that {m("z")} is a complex root of the quadratic equation {m("x^2+px+q=0")}, where {m("p")} and {m("q")} are real integers,')
        + parts([f'find the value of {m("p")} and the value of {m("q")}. {mk(3)}'], start=3, kind='a'))
