# PMT Core Pure 1, Ch.3 Series: transcribed from the rendered page images. Wording, part labels and marks exactly as printed.
from lib import *
Q = {}
Q[1] = (p('In this question you may assume the results for') + eq(r'\sum_{r=1}^{n}r^3,\quad\sum_{r=1}^{n}r^2\quad\text{and}\quad\sum_{r=1}^{n}r')
        + parts([f'Show that the sum of the cubes of the first {m("n")} positive odd numbers is' + eq(r'n^2(2n^2-1)') + mk(5)], kind='a')
        + p(f'The sum of the cubes of 10 consecutive positive odd numbers is {m(r"99\,800")}')
        + parts([f'Use the answer to part (a) to determine the smallest of these 10 consecutive positive odd numbers. {mk(4)}'], start=2, kind='a'))
Q[2] = parts([f'Use the standard results for summations to show that for all positive integers {m("n")}'
              + eq(r'\sum_{r=1}^{n}(5r-2)^2=\frac{1}{6}n(an^2+bn+c)') + p(f'where {m("a")}, {m("b")} and {m("c")} are integers to be determined.') + mk(5),
              f'Hence determine the value of {m("k")} for which' + eq(r'\sum_{r=1}^{k}(5r-2)^2=94k^2') + mk(4)], kind='a')
Q[3] = parts([f'Prove by induction that, for all positive integers {m("n")},' + eq(r'\sum_{r=1}^{n}r(r+1)(2r+1)=\frac{1}{2}n(n+1)^2(n+2)') + mk(6),
              f'Hence, show that, for all positive integers {m("n")},' + eq(r'\sum_{r=n}^{2n}r(r+1)(2r+1)=\frac{1}{2}n(n+1)(an+b)(cn+d)')
              + p(f'where {m("a")}, {m("b")}, {m("c")} and {m("d")} are integers to be determined.') + mk(3)], kind='a')
Q[4] = (parts([f'Use the standard results for {m(r"\sum_{r=1}^{n}r")} and {m(r"\sum_{r=1}^{n}r^2")} to show that'
               + eq(r'\sum_{r=1}^{n}(3r^2+8r+3)=\frac{1}{2}n(2n+5)(n+3)') + p(f'for all positive integers {m("n")}.') + mk(5)], kind='a')
        + p('Given that') + eq(r'\sum_{r=1}^{12}\left(3r^2+8r+3+k(2^{r-1})\right)=3520')
        + parts([f'find the exact value of the constant {m("k")}. {mk(4)}'], start=2, kind='a'))
Q[5] = parts([f'Using the formula for {m(r"\sum_{r=1}^{n}r^2")} write down, in terms of {m("n")} only, an expression for' + eq(r'\sum_{r=1}^{3n}r^2') + mk(1),
              f'Show that, for all integers {m("n")}, where {m("n>0")}' + eq(r'\sum_{r=2n+1}^{3n}r^2=\frac{n}{6}(an^2+bn+c)')
              + p(f'where the values of the constants {m("a")}, {m("b")} and {m("c")} are to be found.') + mk(4)], kind='a')
Q[6] = parts([f'Prove by induction that for all positive integers {m("n")},' + eq(r'\sum_{r=1}^{n}r^2=\frac{1}{6}n(n+1)(2n+1)') + mk(6),
              f'Use the standard results for {m(r"\sum_{r=1}^{n}r^3")} and {m(r"\sum_{r=1}^{n}r")} to show that for all positive integers {m("n")},'
              + eq(r'\sum_{r=1}^{n}r(r+6)(r-6)=\frac{1}{4}n(n+1)(n-8)(n+9)') + mk(4),
              f'Hence find the value of {m("n")} that satisfies' + eq(r'\sum_{r=1}^{n}r(r+6)(r-6)=17\sum_{r=1}^{n}r^2') + mk(5)], kind='a')
