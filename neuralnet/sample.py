import os
import json
import pickle
import argparse
import tensorflow as tf
from model import Model

# main code (not in a main function since I want to run this script in IPython as well).

parser = argparse.ArgumentParser()
parser.add_argument('--sample_length', type=int, default=800,
                   help='number of strokes to sample')
sample_args = parser.parse_args()

with open(os.path.join('save', 'config.pkl'), 'rb') as f:
    saved_args = pickle.load(f)

model = Model(saved_args, True)
sess = tf.InteractiveSession()
saver = tf.train.Saver()

ckpt = tf.train.get_checkpoint_state('save')
print("loading model: ", ckpt.model_checkpoint_path)
saver.restore(sess, ckpt.model_checkpoint_path)

def sample_stroke():
  [strokes, params] = model.sample(sess, sample_args.sample_length)
  return [strokes, params]

[strokes, params] = sample_stroke()
with open('sample.json', 'w') as f:
    json.dump(strokes.tolist(), f)
