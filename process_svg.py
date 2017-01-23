import os
import json
import numpy as np
from glob import glob
from lxml import etree
from PIL import Image, ImageDraw
from svgpathtools import parse_path

ns = '{http://www.w3.org/2000/svg}'
step_size = 0.05

def to_coord(complex):
    return complex.real, complex.imag

dataset = []
for fname in glob('svg/*.svg'):
    strokes = []
    title, _ = os.path.basename(fname).rsplit('.', 1)
    svg = etree.parse(fname).getroot()

    # convert to absolute points
    for ch in svg.findall('.//{}path'.format(ns)):
        data = ch.attrib['d']
        path = parse_path(data)
        for segment in path:
            points = [to_coord(segment.point(x)) for x in np.arange(0, 1 + step_size, step_size)]
            strokes.append(points)

    # draw it out
    im = Image.new('RGB', (2000, 2000))
    draw = ImageDraw.Draw(im)
    for stroke in strokes:
        for start, end in zip(stroke, stroke[1:]):
            if start == end:
                continue
            draw.line([start, end], fill=(255, 255, 255))
    im.save('preview/{}.png'.format(title), 'PNG')

    # convert to offsets and end-of-stroke
    # where 1 -> the last point in the stroke
    data = []
    while strokes:
        stroke = strokes.pop(0)
        for start, end in zip(stroke, stroke[1:]):
            if start == end:
                continue
            sx, sy = start
            ex, ey = end
            delta_x, delta_y = ex - sx, ey - sy
            data.append((delta_x, delta_y, 0))
        if strokes:
            stroke_end = stroke[-1]
            stroke_start = strokes[0][0]
            sx, sy = stroke_end
            ex, ey = stroke_start
            delta_x, delta_y = ex - sx, ey - sy
            data.append((delta_x, delta_y, 1))

    dataset.append(data)
    with open('json/{}.json'.format(title), 'w') as f:
        json.dump(data, f)
    print('{}: {} steps'.format(title, len(data)))

with open('json/dataset.json', 'w') as f:
    json.dump(dataset, f)