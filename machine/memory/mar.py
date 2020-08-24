from os import sys
sys.path.insert(0, "..")
from machine import *


class MAR(Machine):

	def __init__(self, machine):
		self.buffer = None
		self.m = machine

	def load(self, address):
		self.buffer = address

	def fetch(self, startWord = 0):
		# print(f"fetch called on mar, buffer = {self.buffer} ")
		if self.buffer:
			try:
				# print(int(self.buffer,2))
				self.m.mbr.load(self.m.memory.memory[int(self.buffer,2)][startWord:])
			except IndexError as e:
				raise MemoryAccessError("Attempted to access invalid memory location")
		else:
			raise UnloadNoneError("Attempted to unload data from empty buffer")

		self.buffer = None
