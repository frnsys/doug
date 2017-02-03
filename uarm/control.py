import sys
import json
import pyuarm
from time import sleep
from pyuarm import protocol

# according to <https://media.readthedocs.org/pdf/uarmdocs/latest/uarmdocs.pdf>,
# the uarm movement range is
ARM_RANGE = {
    'x': [-36.5*2, 36.5*2],
    'y': [ 11.5*2, 36.5*2],
    'z': [  -12,   19]
}
UP, DOWN = 0, 1

uarm = pyuarm.uarm.UArm(debug=False)
uarm.set_position(0,0,150)
sleep(2)

def move(x,y,z=0):
    uarm.set_position(x,y,z, relative=True)
    while uarm.is_moving():
        pass

# TODO
# - lift and move
# - draw and move

if __name__ == '__main__':
    fname = sys.argv[1]
    data = json.load(open(fname, 'r'))

    # trace the image to figure out the required size
    pos = {'x': 0, 'y': 0}
    visited_x, visited_y = [0], [0]
    for x_step, y_step, _ in data:
        pos['x'] += x_step
        pos['y'] += y_step
        visited_x.append(pos['x'])
        visited_y.append(pos['y'])

    w = max(visited_x) - min(visited_x)
    h = max(visited_y) - min(visited_y)

    # how much to scale steps down by
    scale = {
        'w': (ARM_RANGE['x'][1] - ARM_RANGE['x'][0])/w,
        'h': (ARM_RANGE['y'][1] - ARM_RANGE['y'][0])/h
    }
    scale = min(scale['w'], scale['h'])

    # TODO offset might not be necessary?
    # so the left/upper most positions are within arm range
    offset = {
        # 'x': ARM_RANGE['x'][0] - (min(visited_x) * scale),
        # 'y': ARM_RANGE['y'][0] - (min(visited_y) * scale)
        'x': 0,
        'y': 0
    }

    state = DOWN
    pos = {'x': 0, 'y': 0}
    for x_step, y_step, stroke_end in data:
        xs = x_step * scale
        ys = y_step * scale
        if stroke_end == 1 and state == DOWN:
            state = UP
            ang = uarm.get_servo_angle(protocol.SERVO_LEFT) + 10
            uarm.set_servo_angle(protocol.SERVO_LEFT, ang)
            sleep(0.5)
        elif stroke_end == 0 and state == UP:
            state = DOWN
            ang = uarm.get_servo_angle(protocol.SERVO_LEFT) - 10
            uarm.set_servo_angle(protocol.SERVO_LEFT, ang)
            sleep(0.5)
        print('step:', xs, '|', ys)
        pos['x'] += xs
        pos['y'] += ys
        move(xs, ys)
        sleep(0.02)

    ang = uarm.get_servo_angle(protocol.SERVO_LEFT) + 10
    uarm.set_servo_angle(protocol.SERVO_LEFT, ang)
    sleep(0.5)
    uarm.set_position(-pos['x'], -pos['y'], 0, relative=True)
    uarm.close()
