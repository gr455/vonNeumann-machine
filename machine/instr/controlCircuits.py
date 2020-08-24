from os import sys
sys.path.insert(0, "..")
from machine import *


class ControlCircuits(Machine):

	def __init__(self, machine):
		self.buffer = None
		self.m = machine

	def load(self, opcode):
		self.buffer = opcode

	def decodeInstruction(self):
		return self.m.memory.instrMap(self.buffer)

	# operation functions definition

	def loadMq(self):
		self.m.mq.moveToAcc()

	# Mx should be data
	def loadMqMx(self):
		self.m.mar.fetch() # since loadMqMx first is loaded to MBR as an instruction, MBR now expects data

		self.m.alc.moveToMQ()

	def storMx(self):
		self.m.alc.moveToMbr()
		self.m.mbr.storeToMemory(int(self.m.mar.buffer,2))

	def loadMx(self):
		self.m.mar.fetch()

		self.m.alc.moveToAcc()

	def loadMinusMx(self):
		self.m.mar.fetch()
		self.m.mbr.buffer = -self.m.mbr.buffer

		self.m.alc.moveToAcc()

	def loadAbsMx(self):
		self.m.mar.fetch()
		self.m.mbr.buffer = abs(self.m.mbr.buffer)

		self.m.alc.moveToAcc()

	def loadMinusAbsMx(self):
		self.mar.fetch()
		self.mbr.buffer = -abs(self.m.mbr.buffer)

		self.alc.moveToAcc()

	def jumpMxL(self):
		self.m.mar.fetch()
		self.m.pc.counter = int(self.m.mbr.buffer,2)
		self.m.pc.startWord = 0

	def jumpMxR(self):
		self.m.mar.fetch()
		self.m.pc.counter = int(self.m.mbr.buffer,2)
		self.m.pc.startWord = 20

	def jumpPlusMxL(self):
		self.m.mar.fetch()
		if self.m.accumulator.buffer >= 0 :
			self.m.pc.counter = int(self.m.mbr.buffer,2)
			self.m.pc.startWord = 0

	def jumpPlusMxR(self):
		self.m.mar.fetch()
		if self.m.accumulator.buffer >= 0 :
			self.m.pc.counter = int(self.m.mbr.buffer,2)
			self.m.pc.startWord = 20

	def addMx(self):
		self.m.mar.fetch()
		self.m.alc.add(int(self.m.mbr.buffer,2), int(self.m.accumulator.buffer,2))
		self.m.mbr.buffer = None

	def addAbsMx(self):
		self.m.mar.fetch()
		self.m.alc.add(abs(int(self.m.mbr.buffer,2)), int(self.m.accumulator.buffer,2))
		self.m.mbr.buffer = None

	def subMx(self):
		self.m.mar.fetch()
		self.m.alc.subtract(int(self.m.accumulator.buffer,2), int(self.m.mbr.buffer,2))
		self.m.mbr.buffer = None

	def subAbsMx(self):
		self.m.mar.fetch()
		self.m.alc.subtract(int(self.m.accumulator.buffer,2), abs(int(self.m.mbr.buffer,2)))
		self.m.mbr.buffer = None

	def mulMx(self):
		self.m.mar.fetch()
		self.m.alc.multiply(self.m.mq.buffer, self.m.mbr.buffer)
		self.m.mbr.buffer = None

	def divMx(self):
		self.m.mar.fetch()
		self.m.alc.divide(self.m.accumulator.buffer, self.m.mbr.buffer)
		self.m.mbr.buffer = None

	def lsh(self):
		self.m.mar.fetch()
		self.m.alc.leftShift(self.m.mbr.buffer)
		self.m.mbr.buffer = None

	def rsh(self):
		self.m.mar.fetch()
		self.m.alc.rightShift(self.m.mbr.buffer)
		self.m.mbr.buffer = None

	def noOp(self):
		return True

	def storMxL(self):
		acBits = self.m.accumulator.buffer & 2**12 - 1
		acBits = Instruction.padAddress(str(acBits))
		self.m.mbr.load(acBits)
		self.changeAddress(acBits, 'left')

	def storMxR(self):
		acBits = self.m.accumulator.buffer & 2**12 - 1
		acBits = Instruction.padAddress(str(acBits))
		self.m.mbr.load(acBits)
		self.changeAddress(acBits, 'right')

