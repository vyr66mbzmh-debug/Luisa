# PMT Core Pure 1, Ch.7 Linear Transformations: transcribed from the rendered page images. Wording, part labels and
# marks exactly as printed. Q6 opens with a boxed reference (an image in the PDF), transcribed as a block quote.
from lib import *
Q = {}
B = lambda s: f'<strong>{s}</strong>'
Q[1] = (eq(r'\mathbf A=\begin{pmatrix}-\dfrac12&-\dfrac{\sqrt3}{2}\\[4pt]\dfrac{\sqrt3}{2}&-\dfrac12\end{pmatrix}')
        + parts([f'Describe fully the single geometrical transformation {m("U")} represented by the matrix {m(r"\mathbf A")}. {mk(3)}'], kind='a')
        + p(f'The transformation {m("V")}, represented by the {m(r"2\times2")} matrix {m(r"\mathbf B")}, is a reflection in the line {m("y=-x")}')
        + parts([f'Write down the matrix {m(r"\mathbf B")}. {mk(1)}'], start=2, kind='a')
        + p(f'Given that {m("U")} followed by {m("V")} is the transformation {m("T")}, which is represented by the matrix {m(r"\mathbf C")},')
        + parts([f'find the matrix {m(r"\mathbf C")}. {mk(2)}',
                 f'Show that there is a real number {m("k")} for which the point {m("(1,k)")} is invariant under {m("T")}. {mk(4)}'], start=3, kind='a'))
Q[2] = parts([eq(r'\mathbf A=\begin{pmatrix}2&a\\a-4&b\end{pmatrix}')
              + p(f'where {m("a")} and {m("b")} are non-zero constants.<br>Given that the matrix {m(r"\mathbf A")} is self-inverse,')
              + parts([f'determine the value of {m("b")} and the possible values for {m("a")}. {mk(5)}'], kind='a')
              + p(f'The matrix {m(r"\mathbf A")} represents a linear transformation {m("M")}.<br>Using the smaller value of {m("a")} from part (a),')
              + parts([f'show that the invariant points of the linear transformation {m("M")} form a line, stating the equation of this line. {mk(3)}'], start=2, kind='a'),
              eq(r'\mathbf P=\begin{pmatrix}p&2p\\-1&3p\end{pmatrix}')
              + p(f'where {m("p")} is a positive constant.<br>The matrix {m(r"\mathbf P")} represents a linear transformation {m("U")}.<br>'
                  f'The triangle {m("T")} has vertices at the points with coordinates (1, 2), (3, 2) and (2, 5).<br>The area of the image of {m("T")} under the linear transformation {m("U")} is 15')
              + parts([f'Determine the value of {m("p")}. {mk(4)}'], kind='a')
              + p(f'The transformation {m("V")} consists of a stretch scale factor 3 parallel to the {m("x")}-axis with the {m("y")}-axis invariant followed by a stretch scale factor {m("-2")} parallel to the {m("y")}-axis with the {m("x")}-axis invariant. The transformation {m("V")} is represented by the matrix {m(r"\mathbf Q")}.')
              + parts([f'Write down the matrix {m(r"\mathbf Q")}. {mk(2)}'], start=2, kind='a')
              + p(f'Given that {m("U")} followed by {m("V")} is the transformation {m("W")}, which is represented by the matrix {m(r"\mathbf R")},')
              + parts([f'find the matrix {m(r"\mathbf R")}. {mk(2)}'], start=3, kind='a')], kind='i')
Q[3] = (p(f'The transformation {m("P")} is an enlargement, centre the origin, with scale factor {m("k")}, where {m("k>0")}')
        + p(f'The transformation {m("Q")} is a rotation through angle {m(r"\theta")} degrees anticlockwise about the origin.')
        + p(f'The transformation {m("P")} followed by the transformation {m("Q")} is represented by the matrix')
        + eq(r'\mathbf M=\begin{pmatrix}-4&-4\sqrt3\\4\sqrt3&-4\end{pmatrix}')
        + parts(['Determine' + parts([f'the value of {m("k")},', f'the smallest value of {m(r"\theta")}'], kind='i') + mk(4)], kind='a')
        + p(f'A square {m("S")} has vertices at the points with coordinates (0, 0), {m("(a,-a)")}, {m("(2a,0)")} and {m("(a,a)")} where {m("a")} is a constant.')
        + p(f"The square {m('S')} is transformed to the square {m(chr(83)+chr(39))} by the transformation represented by {m(r'\mathbf M')}.")
        + parts([f"Determine, in terms of {m('a')}, the area of {m(chr(83)+chr(39))} {mk(2)}"], start=2, kind='a'))
Q[4] = (eq(r'\mathbf M=\begin{pmatrix}4&-5\\2&-7\end{pmatrix}')
        + parts([f'Show that the matrix {m(r"\mathbf M")} is non-singular. {mk(2)}'], kind='a')
        + p(f'The transformation {m("T")} of the plane is represented by the matrix {m(r"\mathbf M")}.')
        + p(f'The triangle {m("R")} is transformed to the triangle {m("S")} by the transformation {m("T")}.')
        + p(f'Given that the area of {m("S")} is 63 square units,')
        + parts([f'find the area of {m("R")}. {mk(2)}', f'Show that the line {m("y=2x")} is invariant under the transformation {m("T")}. {mk(2)}'], start=2, kind='a'))
Q[5] = (eq(r'\mathbf A=\begin{pmatrix}4&-2\\5&3\end{pmatrix}')
        + p(f'The matrix {m(r"\mathbf A")} represents the linear transformation {m("M")}.')
        + p(f'Prove that, for the linear transformation {m("M")}, there are no invariant lines. {mk(5)}'))
Q[6] = ('<blockquote>' + p(f'<em>With respect to the {B("right-hand rule")}, a rotation through {m(r"\theta^\circ")} anticlockwise about the {m("y")}-axis is represented by the matrix</em>')
        + eq(r'\begin{pmatrix}\cos\theta&0&\sin\theta\\0&1&0\\-\sin\theta&0&\cos\theta\end{pmatrix}') + '</blockquote>'
        + p(f'The point {m("P")} has coordinates (8, 3, 2)')
        + p(f'The point {m("Q")} is the image of {m("P")} under the transformation reflection in the plane {m("y=0")}')
        + parts([f'Write down the coordinates of {m("Q")} {mk(1)}'], kind='a')
        + p(f'The point {m("R")} is the image of {m("P")} under the transformation rotation through {m(r"120^\circ")} anticlockwise about the {m("y")}-axis, with respect to the {B("right-hand rule")}.')
        + parts([f'Determine the exact coordinates of {m("R")} {mk(2)}',
                 f'Hence find {m(r"|\overrightarrow{PR}|")} giving your answer as a simplified surd. {mk(2)}',
                 f'Show that {m(r"\overrightarrow{PR}")} and {m(r"\overrightarrow{PQ}")} are perpendicular. {mk(1)}',
                 f'Hence determine the exact area of triangle {m("PQR")}, giving your answer as a surd in simplest form. {mk(2)}'], start=2, kind='a'))
Q[7] = (eq(r'\mathbf P=\begin{pmatrix}0&-1\\1&0\end{pmatrix}\qquad\mathbf Q=\begin{pmatrix}1&0\\0&3\end{pmatrix}')
        + parts([parts([f'Describe fully the single geometrical transformation {m("P")} represented by the matrix {m(r"\mathbf P")}.',
                        f'Describe fully the single geometrical transformation {m("Q")} represented by the matrix {m(r"\mathbf Q")}.'], kind='i') + mk(4)], kind='a')
        + p(f'The transformation {m("P")} followed by the transformation {m("Q")} is the transformation {m("R")}, which is represented by the matrix {m(r"\mathbf R")}.')
        + parts([f'Determine {m(r"\mathbf R")}. {mk(1)}',
                 parts([f'Evaluate the determinant of {m(r"\mathbf R")}.', f'Explain how the value obtained in (c)(i) relates to the transformation {m("R")}.'], kind='i') + mk(2)], start=2, kind='a'))
Q[8] = (eq(r'\mathbf A=\begin{pmatrix}2&-1\\4&3\end{pmatrix},\quad\mathbf P=\begin{pmatrix}3&6\\11&-8\end{pmatrix}')
        + parts([f'Find {m(r"\mathbf A^{-1}")} {mk(2)}'], kind='a')
        + p(f'The transformation represented by the matrix {m(r"\mathbf B")} followed by the transformation represented by the matrix {m(r"\mathbf A")} is equivalent to the transformation represented by the matrix {m(r"\mathbf P")}.')
        + parts([f'Find {m(r"\mathbf B")}, giving your answer in its simplest form. {mk(3)}'], start=2, kind='a'))
Q[9] = parts([eq(r'\mathbf A=\begin{pmatrix}p&2\\3&p\end{pmatrix},\quad\mathbf B=\begin{pmatrix}-5&4\\6&-5\end{pmatrix}') + p(f'where {m("p")} is a constant.')
              + parts([f'Find, in terms of {m("p")}, the matrix {m(r"\mathbf{AB}")} {mk(2)}'], kind='a')
              + p('Given that') + eq(r'\mathbf{AB}+2\mathbf A=k\mathbf I') + p(f'where {m("k")} is a constant and {m(r"\mathbf I")} is the {m(r"2\times2")} identity matrix,')
              + parts([f'find the value of {m("p")} and the value of {m("k")}. {mk(4)}'], start=2, kind='a'),
              eq(r'\mathbf M=\begin{pmatrix}a&-9\\1&2\end{pmatrix},\quad\text{where }a\text{ is a real constant}')
              + p(f"Triangle {m('T')} has an area of 15 square units.<br>Triangle {m('T')} is transformed to the triangle {m(chr(84)+chr(39))} by the transformation represented by the matrix {m(r'\mathbf M')}.<br>"
                  f"Given that the area of triangle {m(chr(84)+chr(39))} is 270 square units, find the possible values of {m('a')}. {mk(5)}")], kind='i')
Q[10] = (eq(r'\mathbf M=\begin{pmatrix}1&-\sqrt3\\\sqrt3&1\end{pmatrix}')
         + parts([f'Show that {m(r"\mathbf M")} is non-singular. {mk(2)}'], kind='a')
         + p(f'The hexagon {m("R")} is transformed to the hexagon {m("S")} by the transformation represented by the matrix {m(r"\mathbf M")}.')
         + p(f'Given that the area of hexagon {m("R")} is 5 square units,')
         + parts([f'find the area of hexagon {m("S")}. {mk(1)}'], start=2, kind='a')
         + p(f'The matrix {m(r"\mathbf M")} represents an enlargement, with centre (0, 0) and scale factor {m("k")}, where {m("k>0")}, followed by a rotation anti-clockwise through an angle {m(r"\theta")} about (0, 0).')
         + parts([f'Find the value of {m("k")}. {mk(2)}', f'Find the value of {m(r"\theta")}. {mk(2)}'], start=3, kind='a'))
