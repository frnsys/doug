import json
from tqdm import tqdm
from glob import glob
from PIL import Image, ImageDraw

templ = '''
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <title>preview</title>
    <style>
        img {{
            max-width: 100%;
        }}
    </style>
</head>
<body>
    {html}
</body>
</html>
'''

def bounds(steps):
    points = [[0,0]]
    for (x_step, y_step, _) in steps:
        x, y = points[-1]
        points.append([x+x_step, y+y_step])
    min_x = min(points, key=lambda p: p[0])[0]
    max_x = max(points, key=lambda p: p[0])[0]
    min_y = min(points, key=lambda p: p[1])[1]
    max_y = max(points, key=lambda p: p[1])[1]
    return max_x, min_x, max_y, min_y

def render(steps, name):
    # scale to fit
    max_x, min_x, max_y, min_y = bounds(steps)
    d_w, d_h = max_x - min_x, max_y - min_y
    scale = min(
        width/d_w if d_w > width else 1,
        height/d_h if d_h > height else 1
    )
    d_w *= scale
    d_h *= scale
    start_x = width/2 - (min_x * scale + d_w/2)
    start_y = height/2 - (min_y * scale + d_h/2)
    pos = (start_x, start_y)

    im = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(im)
    for (x_step, y_step, up) in steps:
        next = (pos[0] + x_step * scale, pos[1] + y_step * scale)
        if not up:
            draw.line([pos, next], fill=(255, 255, 255))
        pos = next
    im.save('preview/{}.png'.format(name), 'PNG')


if __name__ == '__main__':
    width, height = 2000, 2000
    for fname in tqdm(reversed(glob('drawings/*.json'))):
        name = fname.split('/')[-1].split('.')[0]
        steps = json.load(open(fname, 'r'))
        render(steps, name)

    els = ['<img src="{}">'.format(im.replace('preview/', '')) for im in glob('preview/*.png')]
    html = templ.format(html='\n'.join(els))
    with open('preview/index.html', 'w') as f:
        f.write(html)