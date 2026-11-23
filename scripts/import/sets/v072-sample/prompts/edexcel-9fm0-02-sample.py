# Sample Assessment Material 9FM0/02 Core Pure Mathematics 2, transcribed from the QP page images (the PDF text layer uses an unreadable font encoding).
from lib import *
CONTEXT = context(SHOW, SIG3)
Q = {}
Q[1] = (p('The roots of the equation') + eq('x^3-8x^2+28x-32=0') + p(f'are {m(r"\alpha")}, {m(r"\beta")} and {m(r"\gamma")}')
        + p('Without solving the equation, find the value of')
        + parts([m(r'\dfrac1\alpha+\dfrac1\beta+\dfrac1\gamma'), m(r'(\alpha+2)(\beta+2)(\gamma+2)'), m(r'\alpha^2+\beta^2+\gamma^2')], kind='i') + mk(8))
Q[2] = (p(f'The plane {m(r"\Pi_1")} has vector equation') + eq(r'\mathbf r\cdot(3\mathbf i-4\mathbf j+2\mathbf k)=5')
        + parts([f'Find the perpendicular distance from the point {m("(6, 2, 12)")} to the plane {m(r"\Pi_1")} {mk(3)}'])
        + p(f'The plane {m(r"\Pi_2")} has vector equation') + eq(r'\mathbf r=\lambda(2\mathbf i+\mathbf j+5\mathbf k)+\mu(\mathbf i-\mathbf j-2\mathbf k)')
        + p(f'where {m(r"\lambda")} and {m(r"\mu")} are scalar parameters.')
        + parts([f'Show that the vector {m(r"-\mathbf i-3\mathbf j+\mathbf k")} is perpendicular to {m(r"\Pi_2")} {mk(2)}',
                 f'Show that the acute angle between {m(r"\Pi_1")} and {m(r"\Pi_2")} is {m(r"52^\circ")} to the nearest degree. {mk(3)}'], start=2))
Q[3] = parts([eq(r'\mathbf M=\begin{pmatrix}2&a&4\\1&-1&-1\\-1&2&-1\end{pmatrix}') + p(f'where {m("a")} is a constant.')
              + parts([f'For which values of {m("a")} does the matrix {m(r"\mathbf M")} have an inverse? {mk(2)}'])
              + p(f'Given that {m(r"\mathbf M")} is non-singular,')
              + parts([f'find {m(r"\mathbf M^{-1}")} in terms of {m("a")} {mk(4)}'], start=2),
              f'Prove by induction that for all positive integers {m("n")},' + eq(r'\begin{pmatrix}3&0\\6&1\end{pmatrix}^n=\begin{pmatrix}3^n&0\\3\left(3^n-1\right)&1\end{pmatrix}') + mk(6)], kind='i')
Q[4] = (p(f'A complex number {m("z")} has modulus 1 and argument {m(r"\theta")}.')
        + parts(['Show that' + eq(r'z^n+\frac1{z^n}=2\cos n\theta,\qquad n\in\mathbb Z^+') + mk(2),
                 'Hence, show that' + eq(r'\cos^4\theta=\frac18(\cos4\theta+4\cos2\theta+3)') + mk(5)]))
Q[5] = (eq(r'y=\sin x\sinh x')
        + parts([f'Show that {m(r"\dfrac{\mathrm d^4y}{\mathrm dx^4}=-4y")} {mk(4)}',
                 f'Hence find the first three non-zero terms of the Maclaurin series for {m("y")}, giving each coefficient in its simplest form. {mk(4)}',
                 f'Find an expression for the {m("n")}th non-zero term of the Maclaurin series for {m("y")}. {mk(2)}']))
Q[6] = (parts([parts([f'Show on an Argand diagram the locus of points given by the values of {m("z")} satisfying' + eq(r'\left|z-4-3\mathrm i\right|=5')], kind='i')
               + p(f'Taking the initial line as the positive real axis with the pole at the origin and given that {m(r"\theta\in[\alpha,\,\alpha+\pi]")}, where {m(r"\alpha=-\arctan\left(\dfrac43\right)")},')
               + parts(['show that this locus of points can be represented by the polar curve with equation' + eq(r'r=8\cos\theta+6\sin\theta')], kind='i', start=2) + mk(6)])
        + p(f'The set of points {m("A")} is defined by')
        + eq(r'A=\left\{z:0\leqslant\arg z\leqslant\frac{\pi}{3}\right\}\cap\left\{z:\left|z-4-3\mathrm i\right|\leqslant5\right\}')
        + parts([parts([f'Show, by shading on your Argand diagram, the set of points {m("A")}.',
                        f'Find the <strong>exact</strong> area of the region defined by {m("A")}, giving your answer in simplest form.'], kind='i') + mk(7)], start=2))
Q[7] = (p('At the start of the year 2000, a survey began of the number of foxes and rabbits on an island.')
        + p(f'At time {m("t")} years after the survey began, the number of foxes, {m("f")}, and the number of rabbits, {m("r")}, on the island are modelled by the differential equations')
        + eq(r'\frac{\mathrm df}{\mathrm dt}=0.2f+0.1r') + eq(r'\frac{\mathrm dr}{\mathrm dt}=-0.2f+0.4r')
        + parts([f'Show that {m(r"\dfrac{\mathrm d^2f}{\mathrm dt^2}-0.6\dfrac{\mathrm df}{\mathrm dt}+0.1f=0")} {mk(3)}',
                 f'Find a general solution for the number of foxes on the island at time {m("t")} years. {mk(4)}',
                 f'Hence find a general solution for the number of rabbits on the island at time {m("t")} years. {mk(3)}'])
        + p('At the start of the year 2000 there were 6 foxes and 20 rabbits on the island.')
        + parts([parts(['According to this model, in which year are the rabbits predicted to die out?',
                        'According to this model, how many foxes will be on the island when the rabbits die out?',
                        'Use your answers to parts (i) and (ii) to comment on the model.'], kind='i') + mk(7)], start=4))
