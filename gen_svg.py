import sys
import math
import random
import numpy as np
from parallel import parallel_process
from svgpathtools import Path, Line, wsvg

m1, m2, n1 = 2, 10, 1.5
rand_range = [1, 1, 1]


def rand(rng):
    return random.random() * (rng * 2) - rng


def pol2cart(theta, rho):
    x = rho * np.cos(theta)
    y = rho * np.sin(theta)
    return x, y


def superformula(m1, m2, n1, a=1, b=1, n2=1, n3=1):
    """https://en.wikipedia.org/wiki/Superformula"""
    def fn(ang):
        cs = math.pow(abs(math.cos((m1 * ang)/4)/a), n2)
        sn = math.pow(abs(math.sin((m2 * ang)/4)/b), n3)
        return math.pow(cs + sn, -(1/n1))
    return fn

def generate_svg(i, m1, m2, n1):
    sf = superformula(m1, m2, n1)
    polar_pts = [(ang, sf(ang)) for ang in np.arange(0, 2*math.pi, 0.1)]
    carte_pts = [pol2cart(ang, rho) for ang, rho in polar_pts]

    # so the figure closes
    carte_pts.append(carte_pts[0])

    path = []
    for (x1, y1), (x2, y2) in zip(carte_pts, carte_pts[1:]):
        seg = Line(x1+y1*1j, x2+y2*1j)
        path.append(seg)
    paths = [Path(*path)]

    fname = 'generated/{}.svg'.format(i)
    wsvg(paths, filename=fname)
    return fname

if __name__ == '__main__':
    n_samples = sys.argv[1]
    generated = parallel_process([{
        'i': i,
        'm1': m1 + rand(rand_range[0]),
        'm2': m2 + rand(rand_range[1]),
        'n1': n1 + rand(rand_range[2]),
    } for i in range(n_samples)], generate_svg, use_kwargs=True)

    html_template = '''
    <!doctype html>
    <html lang="en">
    <head>
        <meta charset="utf-8"/>
        <meta name="viewport" content="width=device-width,initial-scale=1">
        <title>generated svgs</title>
    </head>
    <body>
        {images}
    </body>
    </html>
    '''

    with open('generated/index.html', 'w') as f:
        images = ['<img src="../{}">'.format(fname) for fname in generated]
        html = html_template.format(images='\n'.join(images))
        f.write(html)
