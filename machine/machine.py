from alu.mq import *
from alu.accumulator import *
from alu.alc import * 
from memory.memory import *
from memory.mbr import *
from memory.mar import *
from instr.controlCircuits import *
from instr.ibr import *
from instr.ir import *


def decToBin(n):  
    return bin(n).replace("0b", "")

class Machine:

	def __init__(self, memsize, instrStart):

		self.memory = Memory(self, memsize)
		self.mar = MAR(self)
		self.mbr = MBR(self)
		self.ibr = IBR(self)
		self.ir =  IR(self)
		self.controlCircuits = ControlCircuits(self)
		self.alc = ALC(self)
		self.accumulator = Accumulator(self)
		self.mq = MQ(self)
		self.pc = PC(self, instrStart)

	# start the machine
	def start(self):
		input(f"Machine start at instruction pointer pc = {self.pc.counter} in memory\nEnter to start")
		while self.pc.counter < self.memory.size:
			try:
			# start instruction cycle
				self.mar.load(Instruction.padAddress(decToBin(self.pc.counter)))
				self.mar.fetch(self.pc.startWord)
				self.pc.startWord = 0
				self.mbr.unload()
				while self.ir.buffer:
					self.ir.unload()
					func = self.controlCircuits.decodeInstruction()
					# end of instruction cycle

					# start data cycle
					func()
					self.mbr.buffer = None
					# end data cycle

					if self.ibr.buffer:
						self.ibr.unload()

				self.pc.counter += 1
			except Exception as err:
				print(f"Exception at pc = {self.pc.counter}")
				raise err
		print(f"Program counter encountered memory boundary or end of input at pc = {self.pc.counter}")
		print("Memory state at the end of execution:")
		self.memory.prettyPrint()
		return 0


class Instruction:

	# for a single instruction
	@staticmethod
	def opcode(instruction):
		return instruction[0:8]

	@staticmethod
	def data(instruction):
		return instruction[8:20]

	# for a word
	@staticmethod
	def seperate(instructions):
		return (instructions[0:20], instructions[20:40])

	@staticmethod
	def leftRequired(instructions):
		return Instruction.seperate(instructions)[0] != '0' * 20 and Instruction.seperate(instructions)[1] != ''

	@staticmethod
	def padAddress(address):
		while len(address) < 12:
			address = '0' + address

		return address

	@staticmethod
	def padInstr(instruction):
		while(len(instruction) < 8):
			instruction = '0' + instruction

		return instruction

	@staticmethod
	def padWord(word):
		while(len(word) < 40):
			word = '0' + word

		return word

class PC(Machine):
	def __init__(self, machine, start):
		self.m = machine
		self.counter = int(start,2)
		self.startWord = 0


#Errors
class UnloadNoneError(ValueError):
	''' to be raised if component with empty buffer is called unload on '''

class MemoryAccessError(IndexError):
	''' to be raised when requested memory location does not exist '''

class IllegalOperationError(Exception):
	''' to be raised when a function is passed invalid argument '''

def run():
	'''
	Add instructions and data to the memory and initialize program counter start position
	'''
	machine = Machine(1000,'0000100000')
	machine.memory.memory[0] = "0000000000000000000000000000000000000101"
	machine.memory.memory[1] = "0000000000000000000000000000000000000011"
	machine.memory.memory[32] = '0000100100000000000000001011000000000001'
									 # "100000000000000000101000000000001"
	machine.memory.memory[33] = '0000000000000000000000100001000000000010'
	machine.start()



if __name__ == "__main__":
	run()