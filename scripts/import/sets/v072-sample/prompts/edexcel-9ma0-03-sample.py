# Sample Assessment Material 9MA0/03 Statistics and Mechanics (one combined paper, original numbering), transcribed from the QP page images.
from lib import *
_GB = ('Section B: Mechanics. Unless otherwise indicated, whenever a numerical value of ' + m('g') + ' is required, take ' + m(r'g=9.8\,\mathrm{m\,s^{-2}}')
       + ' and give your answer to either 2 significant figures or 3 significant figures.')
CONTEXT = {n: context(SHOW, SIG3) if n <= 5 else context(SHOW, SIG3, _GB) for n in range(1, 11)}
Q = {}
U = lambda s: m(rf'\mathrm{{{s}}}')
MS1, MS2 = m(r'\mathrm{m\,s^{-1}}'), m(r'\mathrm{m\,s^{-2}}')
Q[1] = (p(f'The number of hours of sunshine each day, {m("y")}, for the month of July at Heathrow are summarised in the table below.')
        + table([['<strong>Hours</strong>', m(r'0\leqslant y<5'), m(r'5\leqslant y<8'), m(r'8\leqslant y<11'), m(r'11\leqslant y<12'), m(r'12\leqslant y<14')],
                 ['<strong>Frequency</strong>', '12', '6', '8', '3', '2']])
        + p(f'A histogram was drawn to represent these data. The {m(r"8\leqslant y<11")} group was represented by a bar of width 1.5 cm and height 8 cm.')
        + parts([f'Find the width and the height of the {m(r"0\leqslant y<5")} group. {mk(3)}',
                 f'Use your calculator to estimate the mean and the standard deviation of the number of hours of sunshine each day, for the month of July at Heathrow.<br>Give your answers to 3 significant figures. {mk(3)}'])
        + p('The mean and standard deviation for the number of hours of daily sunshine for the same month in Hurn are 5.98 hours and 4.12 hours respectably.<br>'
            'Thomas believes that the further south you are the more consistent should be the number of hours of daily sunshine.')
        + parts([f'State, giving a reason, whether or not the calculations in part (b) support Thomas’ belief. {mk(2)}',
                 f'Estimate the number of days in July at Heathrow where the number of hours of sunshine is more than 1 standard deviation above the mean. {mk(2)}'], start=3)
        + p(f'Helen models the number of hours of sunshine each day, for the month of July at Heathrow by {m(r"\mathrm N(6.6,\,3.7^2)")}.')
        + parts([f'Use Helen’s model to predict the number of days in July at Heathrow when the number of hours of sunshine is more than 1 standard deviation above the mean. {mk(2)}',
                 f'Use your answers to part (d) and part (e) to comment on the suitability of Helen’s model. {mk(1)}'], start=5))
Q[2] = (p(f'A meteorologist believes that there is a relationship between the daily mean windspeed, {m("w")} kn, and the daily mean temperature, {m("t")} °C. '
          'A random sample of 9 consecutive days is taken from past records from a town in the UK in July and the relevant data is given in the table below.')
        + table([[f'<strong>{m("t")}</strong>', '13.3', '16.2', '15.7', '16.6', '16.3', '16.4', '19.3', '17.1', '13.2'],
                 [f'<strong>{m("w")}</strong>', '7', '11', '8', '11', '13', '8', '15', '10', '11']])
        + p(f'The meteorologist calculated the product moment correlation coefficient for the 9 days and obtained {m("r=0.609")}')
        + parts([f'Explain why a linear regression model based on these data is unreliable on a day when the mean temperature is 24 °C {mk(1)}',
                 f'State what is measured by the product moment correlation coefficient. {mk(1)}',
                 f'Stating your hypotheses clearly test, at the 5% significance level, whether or not the product moment correlation coefficient for the population is greater than zero. {mk(3)}'])
        + p(f'Using the same 9 days a location from the large data set gave {m(r"\bar t=27.2")} and {m(r"\bar w=3.5")}')
        + parts([f'Using your knowledge of the large data set, suggest, giving your reason, the location that gave rise to these statistics. {mk(1)}'], start=4))
Q[3] = (p(f'A machine cuts strips of metal to length {m("L")} cm, where {m("L")} is normally distributed with standard deviation 0.5 cm.')
        + p(f'Strips with length either less than 49 cm or greater than 50.75 cm <strong>cannot</strong> be used.')
        + p('Given that 2.5% of the cut lengths exceed 50.98 cm,')
        + parts([f'find the probability that a randomly chosen strip of metal <strong>can</strong> be used. {mk(5)}'])
        + p('Ten strips of metal are selected at random.')
        + parts([f'Find the probability fewer than 4 of these strips <strong>cannot</strong> be used. {mk(2)}'], start=2)
        + p(f'A second machine cuts strips of metal of length {m("X")} cm, where {m("X")} is normally distributed with standard deviation 0.6 cm')
        + p('A random sample of 15 strips cut by this second machine was found to have a mean length of 50.4 cm')
        + parts([f'Stating your hypotheses clearly and using a 1% level of significance, test whether or not the mean length of all the strips, cut by the second machine, is greater than 50.1 cm {mk(5)}'], start=3))
Q[4] = (p('Given that') + eq(r'\mathrm P(A)=0.35\qquad\mathrm P(B)=0.45\qquad\text{and}\qquad\mathrm P(A\cap B)=0.13') + p('find')
        + parts([f'{m(r"\mathrm P(A^\prime\mid B^\prime)")} {mk(2)}', f'Explain why the events {m("A")} and {m("B")} are not independent. {mk(1)}'])
        + p(f'The event {m("C")} has {m(r"\mathrm P(C)=0.20")}')
        + p(f'The events {m("A")} and {m("C")} are mutually exclusive and the events {m("B")} and {m("C")} are statistically independent.')
        + parts([f'Draw a Venn diagram to illustrate the events {m("A")}, {m("B")} and {m("C")}, giving the probabilities for each region. {mk(5)}',
                 f'Find {m(r"\mathrm P([B\cup C]^\prime)")} {mk(2)}'], start=3))
Q[5] = (p('A company sells seeds and claims that 55% of its pea seeds germinate.')
        + parts([f'Write down a reason why the company should not justify their claim by testing all the pea seeds they produce. {mk(1)}'])
        + p('A random selection of the pea seeds is planted in 10 trays with 24 seeds in each tray.')
        + parts([f'Assuming that the company’s claim is correct, calculate the probability that in at least half of the trays 15 or more of the seeds germinate. {mk(3)}',
                 f'Write down two conditions under which the normal distribution may be used as an approximation to the binomial distribution. {mk(1)}'], start=2)
        + p('A random sample of 240 pea seeds was planted and 150 of these seeds germinated.')
        + parts([f'Assuming that the company’s claim is correct, use a normal approximation to find the probability that at least 150 pea seeds germinate. {mk(3)}',
                 f'Using your answer to part (d), comment on whether or not the proportion of the company’s pea seeds that germinate is different from the company’s claim of 55% {mk(1)}'], start=4))
Q[6] = (p(f'At time {m("t")} seconds, where {m(r"t\geqslant0")}, a particle {m("P")} moves so that its acceleration {m(r"\mathbf a")} {MS2} is given by')
        + eq(r'\mathbf a=5t\,\mathbf i-15t^{\frac12}\,\mathbf j')
        + p(f'When {m("t=0")}, the velocity of {m("P")} is {m(r"20\mathbf i")} {MS1}')
        + p(f'Find the speed of {m("P")} when {m("t=4")} {mk(6)}'))
Q[7] = (p(f'A rough plane is inclined to the horizontal at an angle {m(r"\alpha")}, where {m(r"\tan\alpha=\dfrac34")}.')
        + p(f'A particle of mass {m("m")} is placed on the plane and then projected up a line of greatest slope of the plane.')
        + p(f'The coefficient of friction between the particle and the plane is {m(r"\mu")}.')
        + p(f'The particle moves up the plane with a constant deceleration of {m(r"\dfrac45g")}.')
        + parts([f'Find the value of {m(r"\mu")}. {mk(6)}'])
        + p(f'The particle comes to rest at the point {m("A")} on the plane.')
        + parts([f'Determine whether the particle will remain at {m("A")}, carefully justifying your answer. {mk(2)}'], start=2))
Q[8] = (p(f'<em>[In this question {m(r"\mathbf i")} and {m(r"\mathbf j")} are horizontal unit vectors due east and due north respectively]</em>')
        + p('A radio controlled model boat is placed on the surface of a large pond.') + p('The boat is modelled as a particle.')
        + p(f'At time {m("t=0")}, the boat is at the fixed point {m("O")} and is moving due north with speed 0.6 {MS1}.')
        + p(f'Relative to {m("O")}, the position vector of the boat at time {m("t")} seconds is {m(r"\mathbf r")} metres.')
        + p(f'At time {m("t=15")}, the velocity of the boat is {m(r"(10.5\mathbf i-0.9\mathbf j)")} {MS1}.')
        + p('The acceleration of the boat is constant.')
        + parts([f'Show that the acceleration of the boat is {m(r"(0.7\mathbf i-0.1\mathbf j)")} {MS2}. {mk(2)}',
                 f'Find {m(r"\mathbf r")} in terms of {m("t")}. {mk(2)}',
                 f'Find the value of {m("t")} when the boat is north-east of {m("O")}. {mk(3)}',
                 f'Find the value of {m("t")} when the boat is moving in a north-east direction. {mk(3)}']))
Q[9] = (fig(9, 30, 'Figure 1: ladder AB of length 2a with A on horizontal ground and B against a vertical wall, making angle α with the ground')
        + p(f'A uniform ladder {m("AB")}, of length {m("2a")} and weight {m("W")}, has its end {m("A")} on rough horizontal ground.')
        + p(f'The coefficient of friction between the ladder and the ground is {m(r"\dfrac14")}.')
        + p(f'The end {m("B")} of the ladder is resting against a smooth vertical wall, as shown in Figure 1.')
        + p(f'A builder of weight {m("7W")} stands at the top of the ladder.<br>To stop the ladder from slipping, the builder’s assistant applies a horizontal force of magnitude {m("P")} to the ladder at {m("A")}, towards the wall.<br>'
            'The force acts in a direction which is perpendicular to the wall.')
        + p(f'The ladder rests in equilibrium in a vertical plane perpendicular to the wall and makes an angle {m(r"\alpha")} with the horizontal ground, where {m(r"\tan\alpha=\dfrac52")}.')
        + p('The builder is modelled as a particle and the ladder is modelled as a uniform rod.')
        + parts([f'Show that the reaction of the wall on the ladder at {m("B")} has magnitude {m("3W")}. {mk(5)}',
                 f'Find, in terms of {m("W")}, the range of possible values of {m("P")} for which the ladder remains in equilibrium. {mk(5)}'])
        + p('Often in practice, the builder’s assistant will simply stand on the bottom of the ladder.')
        + parts([f'Explain briefly how this helps to stop the ladder from slipping. {mk(3)}'], start=3))
Q[10] = (fig(10, 70, 'Figure 2: a stone thrown from O at the top of an 18 m vertical cliff with speed U m/s at angle α above the horizontal, landing at S on sea level 36 m from the foot of the cliff')
         + p(f'A boy throws a stone with speed {m("U")} {MS1} from a point {m("O")} at the top of a vertical cliff.<br>The point {m("O")} is 18 m above sea level.')
         + p(f'The stone is thrown at an angle {m(r"\alpha")} above the horizontal, where {m(r"\tan\alpha=\dfrac34")}.')
         + p(f'The stone hits the sea at the point {m("S")} which is at a horizontal distance of 36 m from the foot of the cliff, as shown in Figure 2.<br>'
             f'The stone is modelled as a particle moving freely under gravity with {m(r"g=10\,\mathrm{m\,s^{-2}}")}')
         + p('Find')
         + parts([f'the value of {m("U")}, {mk(6)}',
                  f'the speed of the stone when it is 10.8 m above sea level, giving your answer to 2 significant figures. {mk(5)}',
                  f'Suggest two improvements that could be made to the model. {mk(2)}']))
