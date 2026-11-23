# PMT Core Pure 2, Ch.7 Methods in Differential Equations: transcribed from the rendered page images. Wording, part
# labels and marks exactly as printed.
from lib import *
Q = {}
Q[1] = (parts([p(f'Find, in the form {m(r"y=\mathrm f(x)")}, the general solution of the equation')
               + eq(r'\cos x\frac{\mathrm dy}{\mathrm dx}+y\sin x=2\cos^3x\sin x+1,\quad0<x<\frac{\pi}{2}') + mk(8)], kind='a')
        + p(f'Given that {m(r"y=5\sqrt2")} when {m(r"x=\dfrac{\pi}{4}")}')
        + parts([f'find the value of {m("y")} when {m(r"x=\dfrac{\pi}{6}")}, giving your answer in the form {m(r"a+b\sqrt3")}, where {m("a")} and {m("b")} are rational numbers to be found. {mk(3)}'], start=2, kind='a'))
Q[2] = (parts([p('Determine the general solution of the differential equation') + eq(r'\cos x\frac{\mathrm dy}{\mathrm dx}+y\sin x=\mathrm e^{2x}\cos^2x')
               + p(f'giving your answer in the form {m(r"y=\mathrm f(x)")}') + mk(3)], kind='a')
        + p(f'Given that {m("y=3")} when {m("x=0")}')
        + parts([f'determine the smallest positive value of {m("x")} for which {m("y=0")} {mk(3)}'], start=2, kind='a'))
Q[3] = parts([p('Find the general solution of the differential equation') + eq(r'\frac{\mathrm d^2y}{\mathrm dx^2}-2\frac{\mathrm dy}{\mathrm dx}=26\sin3x') + mk(8),
              f'Find the particular solution of this differential equation for which {m("y=0")} and {m(r"\dfrac{\mathrm dy}{\mathrm dx}=0")} when {m("x=0")} {mk(5)}'], kind='a')
