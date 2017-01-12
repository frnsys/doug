import json
import random
import numpy as np


class DataLoader():
  def __init__(self, batch_size=50, seq_length=300, scale_factor = 10, limit = 500):
    self.batch_size = batch_size
    self.seq_length = seq_length
    self.scale_factor = scale_factor # divide data by this factor
    self.limit = limit # removes large noisy gaps in the data

    data_file = '../json/dataset.json'
    dataset = json.load(open(data_file, 'r'))
    self.load_preprocessed(dataset)
    self.reset_batch_pointer()

  def load_preprocessed(self, dataset):
    # goes thru the list, and only keeps the text entries that have more than seq_length points
    self.data = []
    counter = 0

    for data in dataset:
      if len(data) > (self.seq_length+2):
        # removes large gaps from the data
        data = np.minimum(data, self.limit)
        data = np.maximum(data, -self.limit)
        data = np.array(data,dtype=np.float32)
        data[:,0:2] /= self.scale_factor
        self.data.append(data)
        counter += int(len(data)/((self.seq_length+2))) # number of equiv batches this datapoint is worth

    # minus 1, since we want the ydata to be a shifted version of x data
    self.num_batches = int(counter / self.batch_size)

  def next_batch(self):
    # returns a randomised, seq_length sized portion of the training data
    x_batch = []
    y_batch = []
    for i in range(self.batch_size):
      data = self.data[self.pointer]
      n_batch = int(len(data)/((self.seq_length+2))) # number of equiv batches this datapoint is worth
      idx = random.randint(0, len(data)-self.seq_length-2)
      x_batch.append(np.copy(data[idx:idx+self.seq_length]))
      y_batch.append(np.copy(data[idx+1:idx+self.seq_length+1]))
      if random.random() < (1.0/float(n_batch)): # adjust sampling probability.
        #if this is a long datapoint, sample this data more with higher probability
        self.tick_batch_pointer()
    return x_batch, y_batch

  def tick_batch_pointer(self):
    self.pointer += 1
    if (self.pointer >= len(self.data)):
      self.pointer = 0
  def reset_batch_pointer(self):
    self.pointer = 0
