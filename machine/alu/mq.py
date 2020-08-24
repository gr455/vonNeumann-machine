from os import sys
sys.path.insert(0, "..")
from machine import *

class MQ(Machine):
	def __init__(self, machine):
		self.buffer = None
		self.isNegative = False
		self.m = Machine

	def load(self, data, isNegative = False):
		self.buffer = data
		self.isNegative = isNegative

	def moveToAcc(self):
		self.accumulator.load(self.buffer)
		self.buffer = None
