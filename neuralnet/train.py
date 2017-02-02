import os
import time
import pickle
import argparse
from model import Model
from utils import DataLoader
import tensorflow as tf

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--rnn_size', type=int, default=256,
                     help='size of RNN hidden state')
  parser.add_argument('--num_layers', type=int, default=2,
                     help='number of layers in the RNN')
  parser.add_argument('--model', type=str, default='gru',
                     help='rnn, gru, or lstm')
  parser.add_argument('--batch_size', type=int, default=8,
                     help='minibatch size')
  parser.add_argument('--seq_length', type=int, default=20-(2+1),
                     help='RNN sequence length')
  parser.add_argument('--num_epochs', type=int, default=2000,
                     help='number of epochs')
  parser.add_argument('--save_every', type=int, default=1000,
                     help='save frequency')
  parser.add_argument('--grad_clip', type=float, default=10.,
                     help='clip gradients at this value')
  parser.add_argument('--learning_rate', type=float, default=0.005,
                     help='learning rate')
  parser.add_argument('--decay_rate', type=float, default=0.95,
                     help='decay rate for rmsprop')
  parser.add_argument('--num_mixture', type=int, default=20,
                     help='number of gaussian mixtures')
  parser.add_argument('--data_scale', type=float, default=10,
                     help='factor to scale raw data down by')
  parser.add_argument('--keep_prob', type=float, default=0.8,
                     help='dropout keep probability')
  args = parser.parse_args()
  train(args)

def train(args):
    data_loader = DataLoader(args.batch_size, args.seq_length, args.data_scale)

    with open(os.path.join('save', 'config.pkl'), 'wb') as f:
        pickle.dump(args, f)

    model = Model(args)

    with tf.Session() as sess:
        tf.global_variables_initializer().run()
        saver = tf.train.Saver(tf.global_variables())
        for e in range(args.num_epochs):
            sess.run(tf.assign(model.lr, args.learning_rate * (args.decay_rate ** e)))
            data_loader.reset_batch_pointer()
            state = model.initial_state.eval()
            for b in range(data_loader.num_batches):
                start = time.time()
                x, y = data_loader.next_batch()
                feed = {model.input_data: x, model.target_data: y, model.initial_state: state}
                train_loss, state, _ = sess.run([model.cost, model.final_state, model.train_op], feed)
                end = time.time()
                print(
                    "{}/{} (epoch {}), train_loss = {:.3f}, time/batch = {:.3f}"  \
                    .format(
                        e * data_loader.num_batches + b,
                        args.num_epochs * data_loader.num_batches,
                        e,
                        train_loss, end - start))
                if (e * data_loader.num_batches + b) % args.save_every == 0 and ((e * data_loader.num_batches + b) > 0):
                    checkpoint_path = os.path.join('save', 'model.ckpt')
                    saver.save(sess, checkpoint_path, global_step = e * data_loader.num_batches + b)
                    print("model saved to {}".format(checkpoint_path))

if __name__ == '__main__':
  main()
