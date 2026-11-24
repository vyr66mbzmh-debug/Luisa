from lib import G, SHOW, context, eq, fig, m, mk, p, parts

CONTEXT = context(SHOW, G)
speed = m(r'\mathrm{m\,s^{-1}}')
acceleration = m(r'\mathrm{m\,s^{-2}}')
Q = {
    1: p(f'At time {m("t=0")}, a small ball is projected vertically upwards with speed {m("U")} {speed} from a point {m("A")} that is 16.8 m above horizontal ground.')
    + p(f'The speed of the ball at the instant immediately before it hits the ground for the first time is 19 {speed}')
    + p(f'The ball hits the ground for the first time at time {m("t=T")} seconds.')
    + p('The motion of the ball, from the instant it is projected until the instant just before it hits the ground for the first time, is modelled as that of a particle moving freely under gravity.')
    + p(f'The acceleration due to gravity is modelled as having magnitude 10 {acceleration}')
    + p('Using the model,')
    + parts([f'show that {m("U=5")} {mk(2)}', f'find the value of {m("T")}, {mk(2)}',
             f'find the time from the instant the ball is projected until the instant when the ball is 1.2 m below {m("A")}. {mk(4)}',
             f'Sketch a velocity-time graph for the motion of the ball for {m(r"0\leqslant t\leqslant T")}, stating the coordinates of the start point and the end point of your graph. {mk(2)}'])
    + p(f'In a refinement of the model of the motion of the ball, the effect of air resistance on the ball is included and this refined model is now used to find the value of {m("U")}.')
    + parts([f'State, with a reason, how this new value of {m("U")} would compare with the value found in part (a), using the initial unrefined model. {mk(1)}',
             f'Suggest one further refinement that could be made to the model, apart from including air resistance, that would make the model more realistic. {mk(1)}'], start=5),
    2: fig(2, 82, 'Figure 1. Balls P (4m) and Q (3m) hang on opposite sides of a pulley.')
    + p(f'One end of a string is attached to a small ball {m("P")} of mass {m("4m")}.')
    + p(f'The other end of the string is attached to another small ball {m("Q")} of mass {m("3m")}.')
    + p('The string passes over a fixed pulley.')
    + p(f'Ball {m("P")} is held at rest with the string taut and the hanging parts of the string vertical, as shown in Figure 1.')
    + p(f'Ball {m("P")} is released.')
    + p('The string is modelled as being light and inextensible, the balls are modelled as particles, the pulley is modelled as being smooth and air resistance is ignored.')
    + parts([f'Using the model, find, in terms of {m("m")} and {m("g")}, the magnitude of the force exerted on the pulley by the string while {m("P")} is falling and before {m("Q")} hits the pulley. {mk(8)}',
             f'State one limitation of the model, apart from ignoring air resistance, that will affect the accuracy of your answer to part (a). {mk(1)}']),
    3: p(f'A particle {m("P")} moves along a straight line such that at time {m("t")} seconds, {m(r"t\geqslant0")}, after leaving the point {m("O")} on the line, the velocity, {m("v")} {speed}, of {m("P")} is modelled as')
    + eq('v=(7-2t)(t+2)')
    + parts([f'Find the value of {m("t")} at the instant when {m("P")} stops accelerating. {mk(4)}',
             f'Find the distance of {m("P")} from {m("O")} at the instant when {m("P")} changes its direction of motion. {mk(5)}'])
    + p('In this question, solutions relying on calculator technology are not acceptable.')
}
