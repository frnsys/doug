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


@cli.command()
@click.argument('name')
@click.argument('svg_dir')
@click.option('-e', '--epochs', help='epochs to train for', default=1000)
def train(name, svg_dir, epochs):
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
        'save_every': int(epochs/5)
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
    with open('drawings/{}.json'.format(n_drawings), 'w') as f:
        json.dump(strokes.tolist(), f)


if __name__ == '__main__':
    cli()
