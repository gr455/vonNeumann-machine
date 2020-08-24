from os import sys
sys.path.insert(0, "..")
from machine import *


class ALC(Machine):

	def __init__(self, machine):
		self.m = machine
	
	# moves value from MBR to MQ
	def moveToMQ(self):
		self.m.mq.load(self.m.mbr.buffer)
		self.m.mbr.buffer = None

	# moves value from accumulator to MBR
	def moveToMbr(self):
		self.m.mbr.load(self.m.accumulator.buffer)
		self.m.accumulator.buffer = None

	# moves value from MBR to accumulator 
	def moveToAcc(self):
		self.m.accumulator.load(self.m.mbr.buffer)
		self.m.mbr.buffer = None


	def add(self, a, b):
		self.m.accumulator.load(a + b)

	def subtract(self, a , b):
		self.m.accumulator.load(a - b)

	def multiply(self, a, b):
		# print(a, b)
		if type(a).__name__ == "str":
			a = int(a,2)
		if type(b).__name__ == "str":
			b = int(b,2)
		mul = a * b
		isNegative = mul < 0
		mul = abs(mul)
		toMq = 0
		toAcc = mul

		bitLength = mul.bit_length()

		if mul > 2**39 - 1 :
			toMq = mul & 2**(39 - bitLength) - 1 # least significant excess bits
			toAcc = mul >> (39 - bitLength)

		self.m.accumulator.load(toAcc)
		self.m.mq.load(toMq, isNegative)

	def divide(self, a, b):

		if type(a).__name__ == "str":
			a = int(a,2)
		if type(b).__name__ == "str":
			b = int(b,2)

		quotient = a // b
		remainder = a % b

		self.m.accumulator.load(remainder)
		self.m.mq.load(quotient)

	def leftShift(self, a):
		if type(a).__name__ == "str":
			a = int(a,2)

		self.m.accumulator.load(a << 1)

	def rightShift(self, a):
		if type(a).__name__ == "str":
			a = int(a,2)

		self.m.accumulator.load(a >> 1)

