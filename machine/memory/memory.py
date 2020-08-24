from os import sys
sys.path.insert(0, "..")
from machine import *

class Memory(Machine):

	def __init__(self, machine, size):
		self.m = machine
		self.memory = ['0' * 40] * size # 8 bit opcode + 12 bit address * 2
		self.size = size

	def printMemory(self):
		for i in self.memory:
			print(i)

	def prettyPrint(self):
		zcount = 0
		flag = 0
		for i in range(len(self.memory)+1):
			try:
				if self.memory[i] == "0"*40 and i <= self.size - 1:
					if not zcount:
						print(f"{i} >> ".rjust(8) + "0"*40, end=" ")
					zcount+=1
					flag = 1
				else:
					if flag:
						print(f"x {zcount}")
						flag = 0
					zcount = 0
					if i <= self.size - 1:
						print(f"{i} >> ".rjust(8) + f"{self.memory[i]}")
			except IndexError:
				print(f"x {zcount}")
				zcount = 0
				if i <= self.size - 1:
					print(f"{i} >> {self.memory[i]}")

	def instrMap(self, opcode):
		instruction_set = {
			# data transfer
			'00001010': self.m.controlCircuits.loadMq,
			'00001001': self.m.controlCircuits.loadMqMx,
			'00100001': self.m.controlCircuits.storMx,
			'00000001': self.m.controlCircuits.loadMx,
			'00000010': self.m.controlCircuits.loadMinusMx,
			'00000011': self.m.controlCircuits.loadAbsMx,
			'00000100': self.m.controlCircuits.loadMinusAbsMx,
			# unconditional
			'00001101': self.m.controlCircuits.jumpMxL,
			'00001110': self.m.controlCircuits.jumpMxR,
			# conditional
			'00001111': self.m.controlCircuits.jumpPlusMxL,
			'00010000': self.m.controlCircuits.jumpPlusMxR,
			# arithmetic
			'00000101': self.m.controlCircuits.addMx,
			'00000111': self.m.controlCircuits.addAbsMx,
			'00000110': self.m.controlCircuits.subMx,
			'00001000': self.m.controlCircuits.subAbsMx,
			'00001011': self.m.controlCircuits.mulMx,
			'00001100': self.m.controlCircuits.divMx,
			'00010100': self.m.controlCircuits.lsh,
			'00010101': self.m.controlCircuits.rsh,
			# address modify
			'00010010': self.m.controlCircuits.storMxL,
			'00010011': self.m.controlCircuits.storMxR,
			# no op
			'10000000': self.m.controlCircuits.noOp,
			'00000000': self.m.controlCircuits.noOp
		}
		return instruction_set[opcode]

	def store(self, data, address):
		if type(address) == 'str':
			address = int(str,2)
		if type(data) != "str":
			data = decToBin(data)
		self.memory[address] = Instruction.padWord(data)