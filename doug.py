#!/usr/bin/env python

import os
import json
import click
import shutil
import neuralnet
from glob import glob
from process_svg import process_svgs


@click.group()
def cli(): pass


# if you get nan, try increasing the scale
@cli.command()
@click.argument('name')
@click.argument('svg_dir')
@click.option('-e', '--epochs', help='epochs to train for', default=1000)
@click.option('-s', '--scale', help='factor to scale raw data down by', default=20)
@click.option('-l', '--learning_rate', help='learning rate', default=0.005)
def train(name, svg_dir, epochs, scale, learning_rate):
    save_dir = 'models/{}'.format(name)
    dataset_dir = '/tmp/svg_dataset'
    for dir in [save_dir, dataset_dir]:
        if os.path.isdir(dir):
            shutil.rmtree(dir)
        os.makedirs(dir)

    print('preparing data...')
    dataf, steps = process_svgs(svg_dir, dataset_dir)

    print('training (this may take awhile)...')
    neuralnet.train(save_dir, dataf, {
        'seq_length': min(steps) - (2+1),
        'num_epochs': epochs,
        'save_every': int(epochs/5),
        'learning_rate': learning_rate,
        'data_scale': scale
    })

    print('done training model "{}"!'.format(name))


@cli.command()
@click.argument('name')
@click.argument('seq_length', type=click.INT)
def draw(name, seq_length):
    save_dir = 'models/{}'.format(name)
    if not os.path.isdir(save_dir):
        print('model "{}" hasn\'t been trained'.format(name))
        return
    strokes, params = neuralnet.sample(save_dir, seq_length)

    n_drawings = len(glob('drawings/*.json'))
    with open('drawings/{:02d}.json'.format(n_drawings), 'w') as f:
        json.dump(strokes.tolist(), f)


if __name__ == '__main__':
    cli()
