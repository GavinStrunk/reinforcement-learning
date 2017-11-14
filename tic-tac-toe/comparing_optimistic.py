
from __future__ import division
import numpy as np
import matplotlib.pyplot as plt

class Bandits:
	def __init__(self,m, mean_max=10):
		self.m = m
		self.mean = mean_max
		self.N = 1

	def pull(self):
		return np.random.randn() + self.m

	def update(self, x):
		self.N += 1
		self.mean = (1.0 - (1.0 / self.N)) * self.mean + (1.0 / self.N) * x

def run_experiment(m1,m2,m3,eps,N):
	
	bandits = [Bandits(m1), Bandits(m2), Bandits(m3)]

	data = np.empty(N)

	for i in range(N):
		#greedy
		j = np.argmax([b.mean for b in bandits])

		x = bandits[j].pull()
		bandits[j].update(x)

		data[i] = x
	cummulative_avg = np.cumsum(data) / (np.arange(N) + 1)

	#plot move average ctr
	plt.plot(cummulative_avg)
	plt.plot(np.ones(N)*m1)
	plt.plot(np.ones(N)*m2)
	plt.plot(np.ones(N)*m3)
	plt.xscale('log')
	plt.show()

	for b in bandits:
		print b.mean

	return cummulative_avg

if __name__ == '__main__':

	c_1 = run_experiment(1.0, 2.0, 3.0, 0.1, 100000)
	c_05 = run_experiment(1.0, 2.0, 3.0, 0.05, 100000)
	c_01 = run_experiment(1.0, 2.0, 3.0, 0.01, 100000)

	plt.plot(c_1, label='eps = 0.1')
	plt.plot(c_05, label='eps = 0.05')
	plt.plot(c_01, label='eps = 0.01')
	plt.legend()
	plt.xscale('log')
	plt.show()

	plt.plot(c_1, label='eps = 0.1')
	plt.plot(c_05, label='eps = 0.05')
	plt.plot(c_01, label='eps = 0.01')
	plt.legend()
	plt.show()	