from os import sys
sys.path.insert(0, "..")
from machine import *


class IR(Machine):

	def __init__(self, machine):
		self.buffer = None
		self.m = machine

	def load(self, opcode):
		self.buffer = opcode

	def unload(self):
		# print(f"ul called on IR, buffer = {self.buffer}")
		if(self.buffer):
			self.m.controlCircuits.load(self.buffer)
		else:
			raise UnloadNoneError("Attempted to unload data from empty buffer")

		self.buffer = None