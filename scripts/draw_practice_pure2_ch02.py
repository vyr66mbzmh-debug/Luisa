"""Draw deterministic solution graphs from the printed functions.

The original answer sketches label the y-intercept as 1; the question's
f(x)=2|x+3|-4 instead gives 2. Original source assets remain untouched.
"""
from pathlib import Path
from html import escape
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'resources/practice-solutions/assets'
def draw(name,title,points,labels,xlim,ylim):
 w,h=600,390;left,top,right,bottom=55,40,35,45
 def pt(x,y):return (left+(x-xlim[0])/(xlim[1]-xlim[0])*(w-left-right),top+(ylim[1]-y)/(ylim[1]-ylim[0])*(h-top-bottom))
 def line(a,b,extra=''):
  x1,y1=pt(*a);x2,y2=pt(*b)
  return f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" {extra}/>'
 svg=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img"><title>{escape(title)}</title><rect width="100%" height="100%" fill="white"/>', '<g stroke="#52606d" stroke-width="1.5">',line((xlim[0],0),(xlim[1],0)),line((0,ylim[0]),(0,ylim[1])),'</g>',f'<polyline points="'+ ' '.join(f'{a:.2f},{b:.2f}' for a,b in [pt(*p) for p in points])+'" fill="none" stroke="#142f46" stroke-width="3"/>','<g font-family="Arial, sans-serif" font-size="17" fill="#142f46">',f'<text x="55" y="24">{escape(title)}</text>']
 for (x,y),label,dx,dy in labels:
  a,b=pt(x,y);svg.append(f'<circle cx="{a:.2f}" cy="{b:.2f}" r="3"/><text x="{a+dx:.2f}" y="{b+dy:.2f}">{escape(label)}</text>')
 a,b=pt(xlim[1],0);svg.append(f'<text x="{a+10:.2f}" y="{b+5:.2f}">x</text>');a,b=pt(0,ylim[1]);svg.append(f'<text x="{a+10:.2f}" y="{b:.2f}">y</text>');svg.extend(['</g>','</svg>']);(OUT/name).write_text('\n'.join(svg)+'\n')
draw('pure2-ch02-silver-modulus.svg','y = |2|x + 3| − 4|',[(-8,6),(-5,0),(-3,4),(-1,0),(2,6)],[((-5,0),'(−5, 0)',-38,25),((-3,4),'(−3, 4)',-30,-13),((-1,0),'(−1, 0)',-36,25),((0,2),'(0, 2)',12,5)],(-8,2),(-1,7))
draw('pure2-ch02-silver-input.svg','y = 2|x| + 2',[(-4,10),(0,2),(4,10)],[((0,2),'(0, 2)',12,12)],(-4.5,4.5),(-1,11))
print('2 exact line graphs drawn')
# Keep x=0 as an explicit vertex so the reflected exponentials meet at a corner.
import math
exponential_points=[(i/100,-math.exp(abs(i/100))) for i in range(-160,161)]
draw('pure2-ch02-negative-exponential.svg','y = −e^|x|',exponential_points,[((0,-1),'(0, −1)',12,-12)],(-1.8,1.8),(-5.2,0.5))
print('1 reflected exponential graph drawn with an exact central corner')
