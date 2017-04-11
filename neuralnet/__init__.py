import os
import time
import pickle
import argparse
import tensorflow as tf
from .model import Model
from .utils import DataLoader


def sample(model_dir, seq_length=40, n=1):
    with open(os.path.join(model_dir, 'config.pkl'), 'rb') as f:
        saved_args = pickle.load(f)
    model = Model(saved_args, True)
    sess = tf.InteractiveSession()
    saver = tf.train.Saver()
    ckpt = tf.train.get_checkpoint_state(model_dir)
    print("loading model: ", ckpt.model_checkpoint_path)
    saver.restore(sess, ckpt.model_checkpoint_path)

    for _ in range(n):
        strokes, params = model.sample(sess, seq_length)
        yield strokes


def train(save_dir, data_file, config):
    continuing = False
    try:
        with open(os.path.join(save_dir, 'config.pkl'), 'rb') as f:
            saved_args = pickle.load(f)
        model = Model(saved_args)
        continuing = True

    except FileNotFoundError:
        parser = argparse.ArgumentParser()
        parser.add_argument('--rnn_size', type=int, default=256,
                            help='size of RNN hidden state')
        parser.add_argument('--num_layers', type=int, default=2,
                            help='number of layers in the RNN')
        parser.add_argument('--model', type=str, default='gru',
                            help='rnn, gru, or lstm')
        parser.add_argument('--batch_size', type=int, default=16,
                            help='minibatch size')
        parser.add_argument('--seq_length', type=int, default=300,
                            help='RNN sequence length')
        parser.add_argument('--num_epochs', type=int, default=1000,
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
        parser.add_argument('--data_scale', type=float, default=20,
                            help='factor to scale raw data down by') # if you get nan you might need to increase this
        parser.add_argument('--keep_prob', type=float, default=0.8,
                            help='dropout keep probability')
        # kinda hacky
        args = parser.parse_args([
            '--{}={}'.format(k, v) for k, v in config.items()
        ])

        with open(os.path.join(save_dir, 'config.pkl'), 'wb') as f:
            pickle.dump(args, f)

        model = Model(args)

    print('loading data')
    data_loader = DataLoader(data_file, args.batch_size, args.seq_length, args.data_scale)
    print('done loading data')

    print('starting session')
    with tf.Session() as sess:
        print('session started')
        tf.global_variables_initializer().run()
        saver = tf.train.Saver(tf.global_variables())

        if continuing:
            ckpt = tf.train.get_checkpoint_state(save_dir)
            saver.restore(sess, ckpt.model_checkpoint_path)

        print('here we go')
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
                    checkpoint_path = os.path.join(save_dir, 'model.ckpt')
                    saver.save(sess, checkpoint_path, global_step = e * data_loader.num_batches + b)
                    print("model saved to {}".format(checkpoint_path))
