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
		# print("mar", self.mar.buffer)
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

class Memory():

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
			'10000000': self.m.controlCircuits.halt,
			'00000000': self.m.controlCircuits.noOp
		}
		return instruction_set[opcode]

	def store(self, data, address):
		try:
			if type(address).__name__ == 'str':
				address = int(str,2)
			if type(data).__name__ != "str":
				data = decToBin(data)
			self.memory[address] = Instruction.padWord(data)
		except(TypeError):
			raise UnloadNoneError("Attempted to unload data from empty MBR buffer")

class MAR():

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


class MBR():

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

class IBR():

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

class IR():

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

class ControlCircuits():

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
		self.m.mbr.buffer = self.m.mar.buffer
		self.m.mar.buffer = None
		self.m.pc.counter = int(self.m.mbr.buffer,2)
		self.m.pc.startWord = 0

	def jumpMxR(self):
		self.m.mbr.buffer = self.m.mar.buffer
		self.m.mar.buffer = None
		self.m.pc.counter = int(self.m.mbr.buffer,2)
		self.m.pc.startWord = 20

	def jumpPlusMxL(self):
		self.m.mbr.buffer = self.m.mar.buffer
		self.m.mar.buffer = None
		if type(self.m.accumulator.buffer).__name__ == "str":
			self.m.accumulator.buffer = int(self.m.accumulator.buffer, 2)
		# print("buffmaster",self.m.mbr.buffer, self.m.pc.counter)
		if self.m.accumulator.buffer >= 0 :
			self.m.pc.counter = int(self.m.mbr.buffer,2)
			self.m.pc.startWord = 0

	def jumpPlusMxR(self):
		self.m.mbr.buffer = self.m.mar.buffer
		self.m.mar.buffer = None
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

	def halt(self):
		self.m.pc.counter = 1001

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


class ALC():

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


class Accumulator():

	def __init__(self, machine):
		self.buffer = None
		self.m = machine

	def load(self, data):
		self.buffer = data

class MQ():
	def __init__(self, machine):
		self.buffer = None
		self.isNegative = False
		self.m = machine

	def load(self, data, isNegative = False):
		self.buffer = data
		self.isNegative = isNegative

	def moveToAcc(self):
		self.m.accumulator.load(self.buffer)
		self.buffer = None

class PC():
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

	'''
	Following program implements a factorial calculator, memory[0] is the input for the program
	'''
	machine = Machine(1000,'00100000')
	machine.memory.memory[0] = "0000000000000000000000000000000000000100" # input

	machine.memory.memory[1] = "0000000000000000000000000000000000000001" # output
	machine.memory.memory[2] = "0000000000000000000000000000000000000001"
	machine.memory.memory[3] = "0000000000000000000000000000000000000000"

	machine.memory.memory[33] = '00001001''000000000000' + '00001011''000000000001' # multiply mem[0] with mem[1]
	machine.memory.memory[34] = '00100001''000000000001' + '00000000''000000000000' # store result to mem[1]
	machine.memory.memory[35] = '00001001''000000000000' + '00001010''000000000000' # take mem[0], load to accumulator
	machine.memory.memory[36] = '00000110''000000000010' + '00100001''000000000011' # subtract 1, stor that to mem[3]
	machine.memory.memory[37] = '00000001''000000000011' + '00100001''000000000000' # store that same value to mem[0]
	machine.memory.memory[38] = '00001001''000000000011' + '00001010''000000000000' # load mem[3] to accumulator for conditional jump
	machine.memory.memory[39] = '00000110''000000000010' + '00001111''000000100000' # subtract 1, ready for conditional jump, jump to mem[32] if accumulator positive
	machine.memory.memory[40] = '10000000''000000000000' + '00000000''000000000000' # halt

	print("value on input stream:", machine.memory.memory[0])
	machine.start()
	print("value on output stream:", machine.memory.memory[1])

	pass
run()