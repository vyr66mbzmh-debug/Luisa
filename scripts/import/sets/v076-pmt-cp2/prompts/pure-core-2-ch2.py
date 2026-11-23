# PMT Core Pure 2, Ch.2 Series (CP2): transcribed from the rendered page images. Wording, part labels and marks
# exactly as printed. Q4 prints only the question total.
from lib import *
Q = {}
Q[1] = (eq(r'y=\ln\left(\frac{1}{1-2x}\right),\qquad|x|<\frac12')
        + parts([f'Find {m(r"\dfrac{\mathrm dy}{\mathrm dx}")}, {m(r"\dfrac{\mathrm d^2y}{\mathrm dx^2}")} and {m(r"\dfrac{\mathrm d^3y}{\mathrm dx^3}")} {mk(4)}',
                 f'Hence, or otherwise, find the series expansion of {m(r"\ln\left(\dfrac{1}{1-2x}\right)")} about {m("x=0")}, in ascending powers of {m("x")}, up to and including the term in {m("x^3")}. Give each coefficient in its simplest form. {mk(3)}',
                 f'Use your expansion to find an approximate value for {m(r"\ln\left(\dfrac32\right)")}, giving your answer to 3 decimal places. {mk(3)}'], kind='a'))
Q[2] = (parts([p(f'Use the standard summation formulae to show that, for {m(r"n\in\mathbb N")},') + eq(r'\sum_{r=1}^{n}(3r^2-17r-25)=n(n^2-An-B)')
               + p(f'where {m("A")} and {m("B")} are integers to be determined.') + mk(4),
               p(f'Explain why, for {m(r"k\in\mathbb N")},') + eq(r'\sum_{r=1}^{3k}r\tan(60r)^\circ=-k\sqrt3') + mk(2)], kind='a')
        + p('Using the results from part (a) and part (b) and showing all your working,')
        + parts([p(f'determine any value of {m("n")} that satisfies') + eq(r'\sum_{r=5}^{n}(3r^2-17r-25)=15\left[\sum_{r=6}^{3n}r\tan(60r)^\circ\right]^2') + mk(6)], start=3, kind='a'))
Q[3] = (eq(r'\mathrm f(x)=\arcsin x\qquad-1\leqslant x\leqslant1')
        + parts([f'Determine the first two non-zero terms, in ascending powers of {m("x")}, of the Maclaurin series for {m(r"\mathrm f(x)")}, giving each coefficient in its simplest form. {mk(4)}',
                 f'Substitute {m(r"x=\dfrac12")} into the answer to part (a) and hence find an approximate value for {m(r"\pi")}<br>Give your answer in the form {m(r"\dfrac{p}{q}")} where {m("p")} and {m("q")} are integers to be determined. {mk(2)}'], kind='a'))
Q[4] = (p(f'Prove that, for {m(r"n\in\mathbb Z,\ n\geqslant0")}') + eq(r'\sum_{r=0}^{n}\frac{1}{(r+1)(r+2)(r+3)}=\frac{(n+a)(n+b)}{c(n+2)(n+3)}')
        + p(f'where {m("a")}, {m("b")} and {m("c")} are integers to be found.'))
Q[5] = (eq(r'y=\sin x\sinh x')
        + parts([f'Show that {m(r"\dfrac{\mathrm d^4y}{\mathrm dx^4}=-4y")} {mk(4)}',
                 f'Hence find the first three non-zero terms of the Maclaurin series for {m("y")}, giving each coefficient in its simplest form. {mk(4)}',
                 f'Find an expression for the {m("n")}th non-zero term of the Maclaurin series for {m("y")}. {mk(2)}'], kind='a'))
Q[6] = parts([p(f'Use the method of differences to prove that for {m("n>2")}') + eq(r'\sum_{r=2}^{n}\ln\left(\frac{r+1}{r-1}\right)\equiv\ln\left(\frac{n(n+1)}{2}\right)') + mk(4),
              p('Hence find the exact value of') + eq(r'\sum_{r=51}^{100}\ln\left(\frac{r+1}{r-1}\right)^{35}')
              + p(f'Give your answer in the form {m(r"a\ln\left(\dfrac{b}{c}\right)")} where {m("a")}, {m("b")} and {m("c")} are integers to be determined.') + mk(3)], kind='a')
Q[7] = (eq(r'y=\cosh^nx\qquad n\geqslant5')
        + parts([parts([p('Show that') + eq(r'\frac{\mathrm d^2y}{\mathrm dx^2}=n^2\cosh^nx-n(n-1)\cosh^{n-2}x') + mk(4),
                        f'Determine an expression for {m(r"\dfrac{\mathrm d^4y}{\mathrm dx^4}")} {mk(2)}'], kind='i'),
                 f'Hence determine the first three non-zero terms of the Maclaurin series for {m("y")}, giving each coefficient in simplest form. {mk(2)}'], kind='a'))
Q[8] = (p('Prove that') + eq(r'\sum_{r=1}^{n}\frac{1}{(r+1)(r+3)}=\frac{n(an+b)}{12(n+2)(n+3)}')
        + p(f'where {m("a")} and {m("b")} are constants to be found. {mk(5)}'))
Q[9] = parts([p(f'Show that, for {m("r>0")}') + eq(r'\frac{1}{r^2}-\frac{1}{(r+1)^2}\equiv\frac{2r+1}{r^2(r+1)^2}') + mk(1),
              p(f'Hence prove that, for {m(r"n\in\mathbb N")}') + eq(r'\sum_{r=1}^{n}\frac{2r+1}{r^2(r+1)^2}=\frac{n(n+2)}{(n+1)^2}') + mk(3),
              p(f'Show that, for {m(r"n\in\mathbb N")}, {m("n>1")}') + eq(r'\sum_{r=n}^{3n}\frac{6r+3}{r^2(r+1)^2}=\frac{an^2+bn+c}{n^2(3n+1)^2}')
              + p(f'where {m("a")}, {m("b")} and {m("c")} are constants to be found.') + mk(3)], kind='a')
Q[10] = parts([p(f'Use the standard results for {m(r"\displaystyle\sum_{r=1}^{n}r^2")} and {m(r"\displaystyle\sum_{r=1}^{n}r")} to show that')
               + eq(r'\sum_{r=1}^{n}(3r-2)^2=\frac12n\left[6n^2-3n-1\right]') + p(f'for all positive integers {m("n")}.') + mk(5),
               p(f'Hence find any values of {m("n")} for which') + eq(r'\sum_{r=5}^{n}(3r-2)^2+103\sum_{r=1}^{28}r\cos\left(\frac{r\pi}{2}\right)=3n^3') + mk(5)], kind='a')
Q[11] = parts([p(f'Show that, for {m("r>0")}') + eq(r'r-3+\frac{1}{r+1}-\frac{1}{r+2}=\frac{r^3-7r-5}{(r+1)(r+2)}') + mk(2),
               p('Hence prove, using the method of differences, that') + eq(r'\sum_{r=1}^{n}\frac{r^3-7r-5}{(r+1)(r+2)}=\frac{n(n^2+an+b)}{2(n+2)}')
               + p(f'where {m("a")} and {m("b")} are constants to be found.') + mk(5)], kind='a')
