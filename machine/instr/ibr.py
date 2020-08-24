from os import sys
sys.path.insert(0, "..")
from machine import *


class IBR(Machine):

	def __init__(self, machine):
		self.buffer = None
		self.m = machine

	def load(self, instruction):
		self.buffer = instruction

	def unload(self):
		instruction = self.buffer

		if instruction:
			self.m.ir.load(instruction[0:8])
			self.m.mar.load(instruction[8:20])
		else:
			raise UnloadNoneError("Attempted to unload data from empty buffer")

		self.buffer = None

	def hasNextInstruction():
		return self.buffer != None
