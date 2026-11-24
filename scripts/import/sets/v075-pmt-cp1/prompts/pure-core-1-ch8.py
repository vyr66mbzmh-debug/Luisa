# PMT Core Pure 1, Ch.8 Proof by Induction: transcribed from the rendered page images. Wording, part labels and marks
# exactly as printed. Q3 and Q4 print no part mark (only the question total), so none is added.
from lib import *
Q = {}
Zp = r'n\in\mathbb Z^+'
Q[1] = parts(['A sequence of numbers is defined by' + eq(r'\begin{gathered}u_1=6,\qquad u_2=27\\u_{n+2}=6u_{n+1}-9u_n\qquad n\geqslant1\end{gathered}')
              + p(f'Prove by induction that, for {m(Zp)}') + eq(r'u_n=3^n(n+1)') + mk(6),
              f'Prove by induction that, for {m(Zp)}' + eq(r'\mathrm f(n)=3^{3n-2}+2^{3n+1}\text{ is divisible by }19') + mk(6)], kind='i')
Q[2] = (p(f'Prove by mathematical induction that, for {m(r"n\in\mathbb N")}') + eq(r'\sum_{r=1}^{n}\frac{1}{(2r-1)(2r+1)}=\frac{n}{2n+1}') + mk(6))
Q[3] = (p(f'Prove by induction that for all positive integers {m("n")}') + eq(r'\mathrm f(n)=3^{2n+4}-2^{2n}') + p('is divisible by 5'))
Q[4] = (p(f'Prove by induction that, for {m(Zp)}') + eq(r'\mathrm f(n)=2^{n+2}+3^{2n+1}') + p('is divisible by 7'))
Q[5] = parts([f'Prove by induction that, for all positive integers {m("n")},' + eq(r'\sum_{r=1}^{n}r(r+1)(2r+1)=\frac{1}{2}n(n+1)^2(n+2)') + mk(6),
              f'Hence, show that, for all positive integers {m("n")},' + eq(r'\sum_{r=n}^{2n}r(r+1)(2r+1)=\frac{1}{2}n(n+1)(an+b)(cn+d)')
              + p(f'where {m("a")}, {m("b")}, {m("c")} and {m("d")} are integers to be determined.') + mk(3)], kind='a')
Q[6] = parts([f'Prove by induction that for {m(Zp)}' + eq(r'\begin{pmatrix}5&-8\\2&-3\end{pmatrix}^n=\begin{pmatrix}4n+1&-8n\\2n&1-4n\end{pmatrix}') + mk(6),
              f'Prove by induction that for {m(Zp)}' + eq(r'\mathrm f(n)=4^{n+1}+5^{2n-1}') + p('is divisible by 21') + mk(6)], kind='i')
Q[7] = (p(f'Prove by induction that for all positive integers {m("n")},') + eq(r'\mathrm f(n)=2^{3n+1}+3\left(5^{2n+1}\right)') + p(f'is divisible by 17 {mk(6)}'))
Q[8] = parts([f'Prove by induction that for all positive integers {m("n")},' + eq(r'\sum_{r=1}^{n}r^2=\frac{1}{6}n(n+1)(2n+1)') + mk(6),
              f'Use the standard results for {m(r"\sum_{r=1}^{n}r^3")} and {m(r"\sum_{r=1}^{n}r")} to show that for all positive integers {m("n")},'
              + eq(r'\sum_{r=1}^{n}r(r+6)(r-6)=\frac{1}{4}n(n+1)(n-8)(n+9)') + mk(4),
              f'Hence find the value of {m("n")} that satisfies' + eq(r'\sum_{r=1}^{n}r(r+6)(r-6)=17\sum_{r=1}^{n}r^2') + mk(5)], kind='a')
Q[9] = parts([eq(r'\mathbf M=\begin{pmatrix}2&a&4\\1&-1&-1\\-1&2&-1\end{pmatrix}') + p(f'where {m("a")} is a constant.')
              + parts([f'For which values of {m("a")} does the matrix {m(r"\mathbf M")} have an inverse? {mk(2)}'], kind='a')
              + p(f'Given that {m(r"\mathbf M")} is non-singular,')
              + parts([f'find {m(r"\mathbf M^{-1}")} in terms of {m("a")} {mk(4)}'], start=2, kind='a'),
              f'Prove by induction that for all positive integers {m("n")},' + eq(r'\begin{pmatrix}3&0\\6&1\end{pmatrix}^n=\begin{pmatrix}3^n&0\\3\left(3^n-1\right)&1\end{pmatrix}') + mk(6)], kind='i')
