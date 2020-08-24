from os import sys
sys.path.insert(0, "..")
from machine import *


class Accumulator(Machine):

	def __init__(self, machine):
		self.buffer = None
		self.m = machine

	def load(self, data):
		self.buffer = data
