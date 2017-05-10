import json
from svgpathtools import Path, Line, wsvg


def json2svg(fname):
    path = []
    pts = [(0,0)]
    data = json.load(open(fname, 'r'))

    for x_step, y_step, up in data:
        x, y = pts[-1]
        x_next, y_next = x + x_step, y + y_step
        if not up:
            line = Line(x+y*1j, x_next+y_next*1j)
            path.append(line)
        pts.append((x_next, y_next))
    paths = [Path(*path)]
    out = '{}.svg'.format(fname.rsplit('.', 1)[0])
    wsvg(paths, filename=out)
    return out


if __name__ == '__main__':
    import sys
    fname = sys.argv[1]
    out = json2svg(fname)
    print('wrote to', out)