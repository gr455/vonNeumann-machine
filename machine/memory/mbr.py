from os import sys
sys.path.insert(0, "..")
from machine import *


class MBR(Machine):

	def __init__(self, machine):
		self.buffer = None
		self.m = machine

	def load(self, instructions):
		self.buffer = instructions

	# moves the instructions from mbr to ir/ibr 
	def unload(self):
		# print(f"ul called on mbr, buffer = {self.buffer}")
		instructions = self.buffer

		if instructions:
			if Instruction.leftRequired(instructions):
				self.m.ir.load(instructions[0:8])
				self.m.ibr.load(instructions[20:40])
				self.m.mar.load(instructions[8:20])
			else:
				self.m.ir.load(instructions[20:28])
				self.m.mar.load(instructions[28:40])
				# print("pr >>" + instructions[8:20]+ str(self.m.pc.counter))

			self.buffer = None

		else:
			raise UnloadNoneError("Attempted to unload data from empty buffer")

	def storeToMemory(self, address):
		self.m.memory.store(self.buffer, address)
		self.buffer = None

	def changeAddress(self, address, leftOrRight = 'left'):
		if leftOrRight == 'left':
			self.memory.memory[self.buffer] = self.memory.memory[self.buffer][0:8] + address + self.memory.memory[self.buffer][20:40]

		elif leftOrRight == 'right':
			self.memory.memory[self.buffer] = self.memory.memory[self.buffer][0:20] +  self.memory.memory[self.buffer][20:28] + address

		else:
			raise IllegalOperationError("An internal function was passed illegal paramerter(s)")

		self.buffer = None
