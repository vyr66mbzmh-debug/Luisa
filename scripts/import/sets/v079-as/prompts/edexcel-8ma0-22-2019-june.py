from lib import G, SHOW, SIG3, context, eq, fig, m, mk, p, parts

CONTEXT = context(SHOW, SIG3, G)
speed = m(r'\mathrm{m\,s^{-1}}')
acceleration = m(r'\mathrm{m\,s^{-2}}')

Q = {
    1: p(f'At time {m("t=0")}, a parachutist falls vertically from rest from a helicopter which is hovering at a height of 550 m above horizontal ground.')
    + p('The parachutist, who is modelled as a particle, falls for 3 seconds before her parachute opens.')
    + p('While she is falling, and before her parachute opens, she is modelled as falling freely under gravity.')
    + p(f'The acceleration due to gravity is modelled as being 10 {acceleration}.')
    + parts([f'Using this model, find the speed of the parachutist at the instant her parachute opens. {mk(1)}'])
    + p('When her parachute is open, the parachutist continues to fall vertically.')
    + p(f'Immediately after her parachute opens, she decelerates at 12 {acceleration} for 2 seconds before reaching a constant speed and she reaches the ground with this speed.')
    + p(f'The total time taken by the parachutist to fall the 550 m from the helicopter to the ground is {m("T")} seconds.')
    + parts([f'Sketch a speed-time graph for the motion of the parachutist for {m(r"0\leqslant t\leqslant T")}. {mk(2)}',
             f'Find, to the nearest whole number, the value of {m("T")}. {mk(5)}'], start=2)
    + p(f'In a refinement of the model of the motion of the parachutist, the effect of air resistance is included before her parachute opens and this refined model is now used to find a new value of {m("T")}.')
    + parts([f'How would this new value of {m("T")} compare with the value found, using the initial model, in part (c)? {mk(1)}',
             f'Suggest one further refinement to the model, apart from air resistance, to make the model more realistic. {mk(1)}'], start=4),
    2: fig(2, 100, 'Figure 1. Ball P on the smooth table is connected over the pulley to the hanging ball Q.')
    + p(f'A small ball, {m("P")}, of mass 0.8 kg, is held at rest on a smooth horizontal table and is attached to one end of a thin rope.')
    + p('The rope passes over a pulley that is fixed at the edge of the table.')
    + p(f'The other end of the rope is attached to another small ball, {m("Q")}, of mass 0.6 kg, that hangs freely below the pulley.')
    + p(f'Ball {m("P")} is released from rest, with the rope taut, with {m("P")} at a distance of 1.5 m from the pulley and with {m("Q")} at a height of 0.4 m above the horizontal floor, as shown in Figure 1.')
    + p(f'Ball {m("Q")} descends, hits the floor and does not rebound.')
    + p('The balls are modelled as particles, the rope as a light and inextensible string and the pulley as small and smooth.')
    + p('Using this model,')
    + parts([f'show that the acceleration of {m("Q")}, as it falls, is 4.2 {acceleration} {mk(5)}',
             f'find the time taken by {m("P")} to hit the pulley from the instant when {m("P")} is released. {mk(6)}',
             f'State one limitation of the model that will affect the accuracy of your answer to part (a). {mk(1)}']),
    3: p(f'A particle, {m("P")}, moves along a straight line such that at time {m("t")} seconds, {m(r"t\geqslant0")}, the velocity of {m("P")}, {m("v")} {speed}, is modelled as')
    + eq('v=12+4t-t^2') + p('Find')
    + parts([f'the magnitude of the acceleration of {m("P")} when {m("P")} is at instantaneous rest, {mk(5)}',
             f'the distance travelled by {m("P")} in the interval {m(r"0\leqslant t\leqslant3")} {mk(3)}'])
}
