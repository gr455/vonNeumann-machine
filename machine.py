
class Machine:

	def __init__(self, memsize):

		self.memory = Memory(memsize, memwordsize)
		self.mar = MAR()
		self.mbr = MBR()
		self.ibr = IBR()
		self.ir =  IR()
		self.controlCircuits = ControlCircuits()
		self.alc = ALC()
		self.accumulator = Accumulator()
		self.mq = MQ()
		self.pc = PC()

	# start the machine
	def start():
		while self.pc.counter < self.memory.size:
			try:
			# start instruction cycle
				self.mar.load(self.memory.memory[self.counter], startWord)
				self.pc.startWord = 0
				self.mar.fetch()
				self.mbr.unload()
				while self.ir.buffer:
					self.ir.unload()
					func = self.controlCircuits.decodeInstruction()
					# end of instruction cycle

					# start data cycle
					func(self.mbr.buffer)
					self.mbr.buffer = None
					# end data cycle

					if self.ibr.buffer:
						self.ibr.unload()

				self.pc.counter += 1
			except Exception as err:
				print("Exception at pc = {self.pc.counter}")
				raise err

		return 0


class Instruction:

	# for a single instruction
	@staticmethod
	def opcode(instruction):
		return instruction[0:7]

	@staticmethod
	def data(instruction):
		return instruction[8:19]

	# for a word
	@staticmethod
	def seperate(instructions):
		return (instructions[0:19], instructions[20:39])

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

class Memory(Machine):

	def __init__(self, size):
		self.memory = ['0' * 40] * size # 8 bit opcode + 12 bit address * 2
		self.size = size

		self.instruction_set = {
			# data transfer
			'00001010': self.controlCircuits.loadMq,
			'00001001': self.controlCircuits.loadMqMx,
			'00100001': self.controlCircuits.storMx,
			'00000001': self.controlCircuits.loadMx,
			'00000010': self.controlCircuits.loadMinusMx,
			'00000011': self.controlCircuits.loadAbsMx,
			'00000100': self.controlCircuits.loadMinusAbsMx,
			# unconditional
			'00001101': self.controlCircuits.jumpMxL,
			'00001110': self.controlCircuits.jumpMxR,
			# conditional
			'00001111': self.controlCircuits.jumpPlusMxL,
			'00010000': self.controlCircuits.jumpPlusMxR,
			# arithmetic
			'00000101': self.controlCircuits.addMx,
			'00000111': self.controlCircuits.addAbsMx,
			'00000110': self.controlCircuits.subMx,
			'00001000': self.controlCircuits.subAbsMx,
			'00001011': self.controlCircuits.mulMx,
			'00001100': self.controlCircuits.divMx,
			'00010100': self.controlCircuits.lsh,
			'00010101': self.controlCircuits.rsh,
			# address modify
			'00010010': self.controlCircuits.storMxL,
			'00010011': self.controlCircuits.storMxR,
			# no op
			'10000000': self.controlCircuits.noOp
		}

	def store(self, data, address):
		self.memory[address] = data

class MAR(Machine):

	def __init__(self):
		self.buffer = None

	def load(self, address):
		self.buffer = address

	def fetch(self, startWord = 0):
		if self.buffer:
			try:
				self.mbr.load(self.memory.memory[self.buffer][startWord:])
			except IndexError:
				raise MemoryAccessError("Attempted to access invalid memory location")
		else:
			raise UnloadNoneError("Attempted to unload data from empty buffer")

		self.buffer = None


class MBR(Machine):

	def __init__(self):
		self.buffer = None

	def load(self, instructions):
		self.buffer = instructions

	# moves the instructions from mbr to ir/ibr 
	def unload(self):
		instructions = self.buffer

		if instructions:
			if Instruction.leftRequired(instructions):
				self.ir.load(instructions[0:7])
				self.ibr.load(instructions[20:39])
				self.mar.load(instructions[8:19])
			else:
				self.ir.load(instructions[20:27])
				self.mar.load(instructions[28:39])

			self.buffer = None

		else:
			raise UnloadNoneError("Attempted to unload data from empty buffer")

	def storeToMemory(self, address):
		self.memory.store(self.buffer, address)
		self.buffer = None

	def changeAddress(self, address, leftOrRight = 'left'):
		if leftOrRight == 'left':
			self.memory.memory[self.buffer] = self.memory.memory[self.buffer][0:8] + address + self.memory.memory[self.buffer][20:39]

		else if leftOrRight == 'right':
			self.memory.memory[self.buffer] = self.memory.memory[self.buffer][0:19] +  self.memory.memory[self.buffer][20:27] + address

		else:
			raise IllegalOperationError("An internal function was passed illegal paramerter(s)")

		self.buffer = None

class IBR(Machine):

	def __init__(self):
		self.buffer = None

	def load(self, instruction):
		self.buffer = instruction

	def unload(self):
		instruction = self.buffer

		if instruction:
			self.ir.load(instruction[0:7])
			self.mar.load(instruction[8:19])
		else:
			raise UnloadNoneError("Attempted to unload data from empty buffer")

		self.buffer = None

	def hasNextInstruction():
		return self.buffer != None

class IR(Machine):

	def __init__(self):
		self.buffer = None

	def load(self, opcode):
		self.buffer = opcode

	def unload(self):
		if(self.buffer):
			self.controlCircuits.load(self.buffer)
		else:
			raise UnloadNoneError("Attempted to unload data from empty buffer")

		self.buffer = None

class ControlCircuits(Machine):

	def __init__(self):
		self.buffer = None

	def load(self, opcode):
		self.buffer = opcode

	def decodeInstruction(self):
		return self.memory.instruction_set[self.buffer]

	# operation functions definition

	def loadMq(self):
		self.mq.moveToAcc()

	# Mx should be data
	def loadMqMx(self):
		self.mar.fetch() # since loadMqMx first is loaded to MBR as an instruction, MBR now expects data

		self.alc.moveToMQ()

	def storMx(self):
		self.alc.moveToMbr()
		self.mbr.storeToMemory(self.mbr.buffer)

	def loadMx(self):
		self.mar.fetch()

		self.alc.moveToAcc()

	def loadMinusMx(self):
		self.mar.fetch()
		self.mbr.buffer = -self.mbr.buffer

		self.alc.moveToAcc()

	def loadAbsMx(self):
		self.mar.fetch()
		self.mbr.buffer = abs(self.mbr.buffer)

		self.alc.moveToAcc()

	def loadMinusAbsMx(self):
		self.mar.fetch()
		self.mbr.buffer = -abs(self.mbr.buffer)

		self.alc.moveToAcc()

	def jumpMxL(self):
		self.mar.fetch()
		self.pc.counter = int(self.mbr.buffer,2)
		self.pc.startWord = 0

	def jumpMxR(self):
		self.mar.fetch()
		self.pc.counter = int(self.mbr.buffer,2)
		self.pc.startWord = 20

	def jumpPlusMxL(self):
		self.mar.fetch()
		if self.accumulator.buffer >= 0 :
			self.pc.counter = int(self.mbr.buffer,2)
			self.pc.startWord = 0

	def jumpPlusMxR(self):
		self.mar.fetch()
		if self.accumulator.buffer >= 0 :
			self.pc.counter = int(self.mbr.buffer,2)
			self.pc.startWord = 20

	def addMx(self):
		self.mar.fetch()
		self.alc.add(self.mbr.buffer, self.accumulator.buffer)
		self.mbr.buffer = None

	def addAbsMx(self):
		self.mar.fetch()
		self.alc.add(abs(self.mbr.buffer), self.accumulator.buffer)
		self.mbr.buffer = None

	def subMx(self):
		self.mar.fetch()
		self.alc.subtract(self.accumulator.buffer, self.mbr.buffer)
		self.mbr.buffer = None

	def subAbsMx(self):
		self.mar.fetch()
		self.alc.subtract(self.accumulator.buffer, abs(self.mbr.buffer))
		self.mbr.buffer = None

	def mulMx(self):
		self.mar.fetch()
		self.alc.multiply(self.mq.buffer, self.mbr.buffer)
		self.mbr.buffer = None

	def divMx(self):
		self.mar.fetch()
		self.alc.divide(self.accumulator.buffer, self.mbr.buffer)
		self.mbr.buffer = None

	def lsh(self):
		self.mar.fetch()
		self.alc.leftShift(self.mbr.buffer)
		self.mbr.buffer = None

	def rsh(self):
		self.mar.fetch()
		self.alc.rightShift(self.mbr.buffer)
		self.mbr.buffer = None

	def noOp(self):
		return True

	def storMxL(self):
		acBits = self.accumulator.buffer & 2**12 - 1
		acBits = Instruction.padAddress(str(acBits))
		self.mbr.load(acBits)
		self.changeAddress(acBits, 'left')

	def storMxR(self);
		acBits = self.accumulator.buffer & 2**12 - 1
		acBits = Instruction.padAddress(str(acBits))
		self.mbr.load(acBits)
		self.changeAddress(acBits, 'right')


class ALC(Machine):
	
	# moves value from MBR to MQ
	def moveToMQ(self):
		self.mq.load(self.mbr.buffer)
		self.mbr.buffer = None

	# moves value from accumulator to MBR
	def moveToMbr(self):
		self.mbr.load(self.accumulator.buffer)
		self.accumulator.buffer = None

	# moves value from MBR to accumulator 
	def moveToAcc(self):
		self.accumulator.load(self.mbr.buffer)
		self.mbr.buffer = None


	def add(self, a, b):
		self.accumulator.load(a + b)

	def subtract(self, a , b):
		self.accumulator.load(a - b)

	def multiply(self, a, b):
		mul = a * b
		isNegative = mul < 0
		mul = abs(mul)
		toMq = 0
		toAcc = mul

		bitLength = mul.bit_length()

		if mul > 2**39 - 1 :
			toMq = mul & 2**(39 - bitLength) - 1 # least significant excess bits
			toAcc = mul >> (39 - bitLength)

		self.accumulator.load(toAcc)
		self.mq.load(toMq, isNegative)

	def divide(self, a, b):
		quotient = a // b
		remainder = a % b

		self.accumulator.load(remainder)
		self.mq.load(quotient)

	def leftShift(self, a):
		self.accumulator.load(a << 1)

	def rightShift(self, a):
		self.accumulator.load(a >> 1)


class Accumulator(Machine):

	def __init__(self):
		self.buffer = None

	def load(self, data):
		self.buffer = data

class MQ(Machine):
	def __init__(self):
		self.buffer = None
		self.isNegative = False

	def load(self, data, isNegative = False):
		self.buffer = data
		self.isNegative = isNegative

	def moveToAcc(self):
		self.accumulator.load(self.buffer)
		self.buffer = None

class PC(Machine):
	def __init__(self, start):
		self.counter = int(start,2)
		self.startWord = 0


#Errors
class UnloadNoneError(ValueError):
	''' to be raised if component with empty buffer is called unload on '''

class MemoryAccessError(IndexError):
	''' to be raised when requested memory location does not exist '''

class IllegalOperationError(Exception):
	''' to be raised when a function is passed invalid argument '''