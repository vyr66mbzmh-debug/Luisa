# PMT Core Pure 1, Ch.6 Matrices: transcribed from the rendered page images. Wording, part labels and marks exactly as
# printed. Source slips are kept verbatim and recorded in questions.json (Q2 has no lead-in before its bullet list;
# Q6 prints "4x x + 3y + 8z = 3").
from lib import *
Q = {}
B = lambda s: f'<strong>{s}</strong>'
Q[1] = (eq(r'\mathbf M=\begin{pmatrix}2&1&-3\\4&-2&1\\3&5&-2\end{pmatrix}')
        + parts([f'Find {m(r"\mathbf M^{-1}")} giving each element in exact form. {mk(2)}',
                 'Solve the simultaneous equations' + eq(r'\begin{gathered}2x+y-3z=-4\\4x-2y+z=9\\3x+5y-2z=5\end{gathered}') + mk(2),
                 f'Interpret the answer to part (b) geometrically. {mk(1)}'], kind='a'))
Q[2] = (p(B('(In this question you must show all stages of your working.)'))
        + p('A college offers only three courses: Construction, Design and Hospitality.')
        + p('Each student enrols on just one of these courses.')
        + p('In 2019, there was a total of 1110 students at this college.')
        + p('There were 370 more students enrolled on Construction than Hospitality.')
        + ul([f'Construction {B("increased")} by 1.25%', f'Design {B("increased")} by 2.5%', f'Hospitality {B("decreased")} by 2%'])
        + p('In 2020, the total number of students at the college increased by 0.27% to 2 significant figures.')
        + parts([parts(['Define, for each course, a variable for the number of students enrolled on that course in 2019.',
                        f'Using your variables from part (a)(i), write down {B("three")} equations that model this situation.'], kind='i') + mk(4),
                 f'By forming and solving a matrix equation, determine how many students were enrolled on each of the three courses in 2019. {mk(4)}'], kind='a'))
Q[3] = (p('The population of chimpanzees in a particular country consists of juveniles and adults.<br>Juvenile chimpanzees do not reproduce.')
        + p('In a study, the numbers of juvenile and adult chimpanzees were estimated at the start of each year. A model for the population satisfies the matrix system')
        + eq(r'\begin{pmatrix}J_{n+1}\\A_{n+1}\end{pmatrix}=\begin{pmatrix}a&0.15\\0.08&0.82\end{pmatrix}\begin{pmatrix}J_n\\A_n\end{pmatrix}\qquad n=0,1,2,\ldots')
        + p(f'where {m("a")} is a constant, and {m("J_n")} and {m("A_n")} are the respective numbers of juvenile and adult chimpanzees {m("n")} years after the start of the study.')
        + parts([f'Interpret the meaning of the constant {m("a")} in the context of the model. {mk(1)}'], kind='a')
        + p(f'At the start of the study, the total number of chimpanzees in the country was estimated to be {m(r"64\,000")}')
        + p(f'According to the model, after one year the number of juvenile chimpanzees is {m(r"15\,360")} and the number of adult chimpanzees is {m(r"43\,008")}')
        + parts([parts([f'Find, in terms of {m("a")}' + eq(r'\begin{pmatrix}a&0.15\\0.08&0.82\end{pmatrix}^{-1}') + mk(3),
                        f'Hence, or otherwise, find the value of {m("a")}. {mk(3)}',
                        f'Calculate the change in the number of juvenile chimpanzees in the first year of the study, according to this model. {mk(2)}'], kind='i')], start=2, kind='a')
        + p('Given that the number of juvenile chimpanzees is known to be in decline in the country,')
        + parts([f'comment on the short-term suitability of this model. {mk(1)}'], start=3, kind='a')
        + p('A study of the population revealed that adult chimpanzees stop reproducing at the age of 40 years.')
        + parts(['Refine the matrix system for the model to reflect this information, giving a reason for your answer.'
                 + p('(<em>There is no need to estimate any unknown values for the refined model, but any known values should be made clear.</em>)') + mk(2)], start=4, kind='a'))
Q[4] = (p(f'{m(r"\mathbf M=\begin{pmatrix}a&2&-3\\2&3&0\\4&a&2\end{pmatrix}")}&emsp;&emsp;where {m("a")} is a constant')
        + parts([f'Show that {m(r"\mathbf M")} is non-singular for all values of {m("a")}. {mk(2)}',
                 f'Determine, in terms of {m("a")}, {m(r"\mathbf M^{-1}")} {mk(4)}'], kind='a'))
Q[5] = (eq(r'\mathbf M=\begin{pmatrix}2&1&4\\k&2&-2\\4&1&-2\end{pmatrix}\qquad\mathbf N=\begin{pmatrix}k-7&6&-10\\2&-20&24\\-3&2&-1\end{pmatrix}')
        + p(f'where {m("k")} is a constant.')
        + parts([f'Determine, in simplest form in terms of {m("k")}, the matrix {m(r"\mathbf{M\,N}")}. {mk(2)}',
                 f'Given that {m("k=5")}' + parts([f'write down {m(r"\mathbf{M\,N}")}', f'hence write down {m(r"\mathbf M^{-1}")}'], kind='i') + mk(2),
                 'Solve the simultaneous equations' + eq(r'\begin{aligned}2x+\ \ y+4z&=2\\5x+2y-2z&=3\\4x+\ \ y-2z&=-1\end{aligned}') + mk(2),
                 f'Interpret the answer to part (c) geometrically. {mk(1)}'], kind='a'))
Q[6] = (eq(r'\mathbf A=\begin{pmatrix}4&-1\\7&2\\-5&8\end{pmatrix}\quad\mathbf B=\begin{pmatrix}2&3&2\\-1&6&5\end{pmatrix}\quad\mathbf C=\begin{pmatrix}-5&2&1\\4&3&8\\-6&11&2\end{pmatrix}')
        + p(f'Given that {m(r"\mathbf I")} is the {m(r"3\times3")} identity matrix,')
        + parts([parts([f'show that there is an integer {m("k")} for which' + eq(r'\mathbf{AB}-3\mathbf C+k\mathbf I=\mathbf 0') + f'stating the value of {m("k")}',
                        f'explain why there can be no constant {m("m")} such that' + eq(r'\mathbf{BA}-3\mathbf C+m\mathbf I=\mathbf 0')], kind='i') + mk(4),
                 parts([f'Show how the matrix {m(r"\mathbf C")} can be used to solve the simultaneous equations'
                        + eq(r'\begin{gathered}-5x+2y+z=-14\\4\text{x}\ x+3y+8z=3\\-6x+11y+2z=7\end{gathered}'),
                        'Hence use your calculator to solve these equations.'], kind='i') + mk(3)], kind='a'))
Q[7] = (p(f'{m(r"\mathbf M=\begin{pmatrix}2&-1&1\\3&k&4\\3&2&-1\end{pmatrix}")}&emsp;&emsp;where {m("k")} is a constant')
        + parts([f'Find the values of {m("k")} for which the matrix {m(r"\mathbf M")} has an inverse. {mk(2)}',
                 f'Find, in terms of {m("p")}, the coordinates of the point where the following planes intersect'
                 + eq(r'\begin{gathered}2x-y+z=p\\3x-6y+4z=1\\3x+2y-z=0\end{gathered}') + mk(5),
                 parts([f'Find the value of {m("q")} for which the set of simultaneous equations' + eq(r'\begin{gathered}2x-y+z=1\\3x-5y+4z=q\\3x+2y-z=0\end{gathered}') + 'can be solved.',
                        f'For this value of {m("q")}, interpret the solution of the set of simultaneous equations geometrically.'], kind='i') + mk(4)], kind='a'))
Q[8] = parts([f'{m(r"\mathbf A")} is a 2 by 2 matrix and {m(r"\mathbf B")} is a 2 by 3 matrix.<br>Giving a reason for your answer, explain whether it is possible to evaluate'
              + parts([m(r'\mathbf{AB}'), m(r'\mathbf A+\mathbf B')], kind='a') + mk(2),
              'Given that' + eq(r'\begin{pmatrix}-5&3&1\\a&0&0\\b&a&b\end{pmatrix}\begin{pmatrix}0&5&0\\2&12&-1\\-1&-11&3\end{pmatrix}=\lambda\mathbf I')
              + p(f'where {m("a")}, {m("b")} and {m(r"\lambda")} are constants,')
              + parts(['determine' + ul([f'the value of {m(r"\lambda")}', f'the value of {m("a")}', f'the value of {m("b")}']),
                       f'Hence deduce the inverse of the matrix {m(r"\begin{pmatrix}-5&3&1\\a&0&0\\b&a&b\end{pmatrix}")}'], kind='a') + mk(3),
              'Given that' + eq(r'\mathbf M=\begin{pmatrix}1&1&1\\0&\sin\theta&\cos\theta\\0&\cos2\theta&\sin2\theta\end{pmatrix}\qquad\text{where }0\leqslant\theta<\pi')
              + p(f'determine the values of {m(r"\theta")} for which the matrix {m(r"\mathbf M")} is singular. {mk(4)}')], kind='i')
