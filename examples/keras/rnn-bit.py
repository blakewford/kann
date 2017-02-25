#!/usr/bin/env python

import sys, getopt
import numpy as np
from keras.layers import Dense, Activation, GRU
from keras.models import Sequential
from keras.optimizers import RMSprop

def rb_read_data(fn):
	d, n_col = [], 0
	with open(fn, 'r') as fp:
		for line in fp:
			t = line[:-1].split()
			if n_col == 0: n_col = len(t)
			elif n_col != len(t):
				sys.exit("ERROR: different number of fields")
			d.append(t)
	max_bit = 0
	for k in range(len(d)):
		for i in range(n_col):
			t = d[k][i] = int(d[k][i])
			for j in range(64):
				if (t&1) == 1: max_bit = j;
				t >>= 1
	max_bit += 1
	x = np.zeros((len(d), max_bit, n_col - 1), dtype=np.bool)
	y = np.zeros((len(d), max_bit * 2), dtype=np.bool)
	for k in range(len(d)):
		for i in range(n_col):
			t = d[k][i]
			for j in range(max_bit):
				if i < n_col - 1:
					x[k][j][i] = t & 1
				else:
					y[k][j * 2 + (t&1)] = 1
				t >>= 1
	return x, y, n_col - 1, max_bit

def rb_model_gen(n_in, n_hidden, ulen, dropout):
	model = Sequential()
	model.add(GRU(n_hidden, input_shape=(ulen, n_in), dropout_W=dropout, dropout_U=dropout))
	model.add(Dense(ulen * 2))
	model.add(Activation('sigmoid'))
	return model

def rb_usage():
	print("Usage: rnn-bit.py [options] <data.txt>")
	sys.exit(1)

def main(argv):
	lr, to_apply, mbs, n_hidden, max_epoch, seed, dropout = 0.01, False, 64, 128, 50, 11, 0.0

	try:
		opts, args = getopt.getopt(argv[1:], "Ar:n:B:m:d:")
	except getopt.GetoptError:
		rb_usage()
	if len(args) < 1:
		rb_usage()

	for opt, arg in opts:
		if opt == '-r': lr = float(arg)
		elif opt == '-A': to_apply = True
		elif opt == '-n': n_hidden = int(arg)
		elif opt == '-B': mbs = int(arg)
		elif opt == '-m': max_epoch = int(arg)
		elif opt == '-d': dropout = float(arg)

	np.random.seed(seed)
	x, y, n_in, max_bit = rb_read_data(args[0])

	if not to_apply:
		model = rb_model_gen(n_in, n_hidden, max_bit, dropout)
		optimizer = RMSprop(lr=0.01)
		model.compile(loss='binary_crossentropy', optimizer=optimizer)
		model.fit(x, y, batch_size=mbs, nb_epoch=max_epoch)

if __name__ == "__main__":
	main(sys.argv)