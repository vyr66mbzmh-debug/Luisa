# PMT Core Pure 2, Ch.8 Modelling with Differential Equations: transcribed from the rendered page images. Wording,
# part labels and marks exactly as printed; the figure is a source crop with its printed caption.
from lib import *
Q = {}
D = r'\frac{\mathrm d^2\theta}{\mathrm dt^2}+9\theta=\frac12\cos3t'
Q[1] = (fig(1, 35, 'Figure 3: a pendulum hanging from a fixed point, displaced by an angle θ from the dashed downward vertical, with a dashed arc showing its swing')
        + p('The motion of a pendulum, shown in Figure 3, is modelled by the differential equation') + eq(D)
        + p(f'where {m(r"\theta")} is the angle, in radians, that the pendulum makes with the downward vertical, {m("t")} seconds after it begins to move.')
        + parts([parts([p('Show that a particular solution of the differential equation is') + eq(r'\theta=\frac{1}{12}t\sin3t') + mk(4),
                        f'Hence, find the general solution of the differential equation. {mk(4)}'], kind='i')], kind='a')
        + p('Initially, the pendulum') + ul([f'makes an angle of {m(r"\dfrac{\pi}{3}")} radians with the downward vertical', 'is at rest'])
        + p(f'Given that, 10 seconds after it begins to move, the pendulum makes an angle of {m(r"\alpha")} radians with the downward vertical,')
        + parts([f'determine, according to the model, the value of {m(r"\alpha")} to 3 significant figures. {mk(4)}'], start=2, kind='a')
        + p(f'Given that the true value of {m(r"\alpha")} is 0.62')
        + parts([f'evaluate the model. {mk(1)}'], start=3, kind='a')
        + p('The differential equation') + eq(D) + p('models the motion of the pendulum as moving with forced harmonic motion.')
        + parts([f'Refine the differential equation so that the motion of the pendulum is simple harmonic motion. {mk(1)}'], start=4, kind='a'))
Q[2] = (p(f'An engineer is investigating the motion of a sprung diving board at a swimming pool.<br>Let {m("E")} be the position of the end of the diving board when it is at rest in its equilibrium position and when there is no diver standing on the diving board.<br>'
          f'A diver jumps from the diving board.<br>The vertical displacement, {m("h")} cm, of the end of the diving board above {m("E")} is modelled by the differential equation')
        + eq(r'4\frac{\mathrm d^2h}{\mathrm dt^2}+4\frac{\mathrm dh}{\mathrm dt}+37h=0') + p(f'where {m("t")} seconds is the time after the diver jumps.')
        + parts([f'Find a general solution of the differential equation. {mk(2)}'], kind='a')
        + p(f'When {m("t=0")}, the end of the diving board is 20 cm below {m("E")} and is moving upwards with a speed of 55 {m(r"\mathrm{cm\,s^{-1}}")}.')
        + parts([f'Find, according to the model, the maximum vertical displacement of the end of the diving board above {m("E")}. {mk(8)}',
                 f'Comment on the suitability of the model for large values of {m("t")}. {mk(2)}'], start=2, kind='a'))
Q[3] = (p(f'A scientist is studying the effect of introducing a population of white-clawed crayfish into a population of signal crayfish.<br>At time {m("t")} years, the number of white-clawed crayfish, {m("w")}, and the number of signal crayfish, {m("s")}, are modelled by the differential equations')
        + eq(r'\begin{aligned}\frac{\mathrm dw}{\mathrm dt}&=\frac52(w-s)\\\frac{\mathrm ds}{\mathrm dt}&=\frac25w-90\mathrm e^{-t}\end{aligned}')
        + parts([p('Show that') + eq(r'2\frac{\mathrm d^2w}{\mathrm dt^2}-5\frac{\mathrm dw}{\mathrm dt}+2w=450\mathrm e^{-t}') + mk(3),
                 f'Find a general solution for the number of white-clawed crayfish at time {m("t")} years. {mk(6)}',
                 f'Find a general solution for the number of signal crayfish at time {m("t")} years. {mk(2)}'], kind='a')
        + p(f'The model predicts that, at time {m("T")} years, the population of white-clawed crayfish will have died out.')
        + p(f'Given that {m("w=65")} and {m("s=85")} when {m("t=0")}')
        + parts([f'find the value of {m("T")}, giving your answer to 3 decimal places. {mk(6)}', f'Suggest a limitation of the model. {mk(1)}'], start=4, kind='a'))
Q[4] = (p('At the start of the year 2000, a survey began of the number of foxes and rabbits on an island.')
        + p(f'At time {m("t")} years after the survey began, the number of foxes, {m("f")}, and the number of rabbits, {m("r")}, on the island are modelled by the differential equations')
        + eq(r'\begin{aligned}\frac{\mathrm df}{\mathrm dt}&=0.2f+0.1r\\\frac{\mathrm dr}{\mathrm dt}&=-0.2f+0.4r\end{aligned}')
        + parts([f'Show that {m(r"\dfrac{\mathrm d^2f}{\mathrm dt^2}-0.6\dfrac{\mathrm df}{\mathrm dt}+0.1f=0")} {mk(3)}',
                 f'Find a general solution for the number of foxes on the island at time {m("t")} years. {mk(4)}',
                 f'Hence find a general solution for the number of rabbits on the island at time {m("t")} years. {mk(3)}'], kind='a')
        + p('At the start of the year 2000 there were 6 foxes and 20 rabbits on the island.')
        + parts([parts(['According to this model, in which year are the rabbits predicted to die out?',
                        'According to this model, how many foxes will be on the island when the rabbits die out?',
                        'Use your answers to parts (i) and (ii) to comment on the model.'], kind='i') + mk(7)], start=4, kind='a'))
Q[5] = (p('A sample of bacteria in a sealed container is being studied.')
        + p(f'The number of bacteria, {m("P")}, in thousands, is modelled by the differential equation') + eq(r'(1+t)\frac{\mathrm dP}{\mathrm dt}+P=t^{\frac12}(1+t)')
        + p(f'where {m("t")} is the time in hours after the start of the study.') + p('Initially, there are exactly 5000 bacteria in the container.')
        + parts([f'Determine, according to the model, the number of bacteria in the container 8 hours after the start of the study. {mk(6)}',
                 f'Find, according to the model, the rate of change of the number of bacteria in the container 4 hours after the start of the study. {mk(4)}',
                 f'State a limitation of the model. {mk(1)}'], kind='a'))
Q[6] = (p('A pond initially contains 1000 litres of unpolluted water.') + p('The pond is leaking at a constant rate of 20 litres per day.')
        + p('It is suspected that contaminated water flows into the pond at a constant rate of 25 litres per day and that the contaminated water contains 2 grams of pollutant in every litre of water.')
        + p('It is assumed that the pollutant instantly dissolves throughout the pond upon entry.')
        + p(f'Given that there are {m("x")} grams of the pollutant in the pond after {m("t")} days,')
        + parts([p('show that the situation can be modelled by the differential equation,') + eq(r'\frac{\mathrm dx}{\mathrm dt}=50-\frac{4x}{200+t}') + mk(4),
                 f'Hence find the number of grams of pollutant in the pond after 8 days. {mk(5)}', f'Explain how the model could be refined. {mk(1)}'], kind='a'))
Q[7] = (p('A tank at a chemical plant has a capacity of 250 litres. The tank initially contains 100 litres of pure water.')
        + p('Salt water enters the tank at a rate of 3 litres every minute. Each litre of salt water entering the tank contains 1 gram of salt.')
        + p('It is assumed that the salt water mixes instantly with the contents of the tank upon entry.')
        + p('At the instant when the salt water begins to enter the tank, a valve is opened at the bottom of the tank and the solution in the tank flows out at a rate of 2 litres per minute.')
        + p(f'Given that there are {m("S")} grams of salt in the tank after {m("t")} minutes,')
        + parts([p('show that the situation can be modelled by the differential equation') + eq(r'\frac{\mathrm dS}{\mathrm dt}=3-\frac{2S}{100+t}') + mk(4),
                 f'Hence find the number of grams of salt in the tank after 10 minutes. {mk(5)}'], kind='a')
        + p('When the concentration of salt in the tank reaches 0.9 grams per litre, the valve at the bottom of the tank must be closed.')
        + parts([f'Find, to the nearest minute, when the valve would need to be closed. {mk(3)}', f'Evaluate the model. {mk(1)}'], start=3, kind='a'))
Q[8] = (p('A company plans to build a new fairground ride. The ride will consist of a capsule that will hold the passengers and the capsule will be attached to a tall tower. The capsule is to be released from rest from a point half way up the tower and then made to oscillate in a vertical line.<br>'
          f'The vertical displacement, {m("x")} metres, of the top of the capsule below its initial position at time {m("t")} seconds is modelled by the differential equation,')
        + eq(r'm\frac{\mathrm d^2x}{\mathrm dt^2}+4\frac{\mathrm dx}{\mathrm dt}+x=200\cos t,\quad t\geqslant0')
        + p(f'where {m("m")} is the mass of the capsule including its passengers, in thousands of kilograms.')
        + p('The maximum permissible weight for the capsule, including its passengers, is 30 000N.')
        + p(f'Taking the value of {m("g")} to be 10 {m(r"\mathrm{ms^{-2}}")} and assuming the capsule is at its maximum permissible weight,')
        + parts([parts([f'explain why the value of {m("m")} is 3', p('show that a particular solution to the differential equation is') + eq(r'x=40\sin t-20\cos t'),
                        'hence find the general solution of the differential equation.'], kind='i') + mk(8),
                 f'Using the model, find, to the nearest metre, the vertical distance of the top of the capsule from its initial position, 9 seconds after it is released. {mk(4)}'], kind='a'))
Q[9] = (p('A scientist is investigating the concentration of antibodies in the bloodstream of a patient following a vaccination.')
        + p(f'The concentration of antibodies, {m("x")}, measured in micrograms (μg) per millilitre (ml) of blood, is modelled by the differential equation')
        + eq(r'100\frac{\mathrm d^2x}{\mathrm dt^2}+60\frac{\mathrm dx}{\mathrm dt}+13x=26') + p(f'where {m("t")} is the number of weeks since the vaccination was given.')
        + parts([f'Find a general solution of the differential equation. {mk(4)}'], kind='a')
        + p('Initially,') + ul(['there are no antibodies in the bloodstream of the patient', 'the concentration of antibodies is estimated to be increasing at 10 μg/ml per week'])
        + parts([f'Find, according to the model, the maximum concentration of antibodies in the bloodstream of the patient after the vaccination. {mk(8)}'], start=2, kind='a')
        + p('A second dose of the vaccine has to be given to try to ensure that it is fully effective.<br>It is only safe to give the second dose if the concentration of antibodies in the bloodstream of the patient is less than 5 μg/ml.')
        + parts([f'Determine whether, according to the model, it is safe to give the second dose of the vaccine to the patient exactly 10 weeks after the first dose. {mk(2)}'], start=3, kind='a'))
Q[10] = (p(f'Two compounds, {m("X")} and {m("Y")}, are involved in a chemical reaction. The amounts in grams of these compounds, {m("t")} minutes after the reaction starts, are {m("x")} and {m("y")} respectively and are modelled by the differential equations')
         + eq(r'\begin{aligned}\frac{\mathrm dx}{\mathrm dt}&=-5x+10y-30\\\frac{\mathrm dy}{\mathrm dt}&=-2x+3y-4\end{aligned}')
         + parts([p('Show that') + eq(r'\frac{\mathrm d^2x}{\mathrm dt^2}+2\frac{\mathrm dx}{\mathrm dt}+5x=50') + mk(3),
                  f'Find, according to the model, a general solution for the amount in grams of compound {m("X")} present at time {m("t")} minutes. {mk(6)}',
                  f'Find, according to the model, a general solution for the amount in grams of compound {m("Y")} present at time {m("t")} minutes. {mk(3)}'], kind='a')
         + p(f'Given that {m("x=2")} and {m("y=5")} when {m("t=0")}')
         + parts(['find' + parts([f'the particular solution for {m("x")},', f'the particular solution for {m("y")}.'], kind='i') + mk(4)], start=4, kind='a')
         + p('A scientist thinks that the chemical reaction will have stopped after 8 minutes.')
         + parts([f'Explain whether this is supported by the model. {mk(1)}'], start=5, kind='a'))
