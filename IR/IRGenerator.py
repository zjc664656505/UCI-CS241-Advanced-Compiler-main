from DataStructure.DataResult.ConstantResult import ConstantResult
from DataStructure.DataResult.IResult import IResult
from DataStructure.DataResult.VariableResult import VariableResult
from DataStructure.Instruction import Instruction
from DataStructure.Token import Token, TokenType
from DataStructure.Instruction import DeleteMode
from util.Constants import Constants
from DataStructure.Blocks.IBlock import IBlock
from DataStructure.DataResult.BranchResult import BranchResult
from multipledispatch import dispatch
from DataStructure.DataResult.InstructionResult import InstructionResult
from DataStructure.Array import Array
import sys
from DataStructure.Operator import Operator, OperatorCode


class IrGenerator:
    pc = -1
    optimizer = None
    operator = Operator()

    def __init__(self):
        self.pc = Constants.INSTRUCTION_START_COUNTER

    def reset(self):
        self.pc = Constants.INSTRUCTION_START_COUNTER

    def getPC(self):
        return self.pc

    def incrementPC(self):
        self.pc = self.pc + 1

    @dispatch(IBlock, Token, BranchResult)
    def compute(self, block, opToken, y):
        opCode = Operator.branchingOperator[Token.tokenValueMap[opToken.value]]
        instruction = None
        if opCode == OperatorCode.bra:
            self.pc = self.pc
            instruction = Instruction(self.pc, opCode, None, y)
        else:
            self.pc = self.pc
            instruction = Instruction(self.pc, opCode, y.toInstruction(), y)
        instruction.deletemode = DeleteMode._NOT_DEL
        block.addinstruction(instruction)

    # TODO: compute for constantResult
    @dispatch(IBlock, Token, IResult, type(None), int)
    def compute(self, block, opCode, x, y, iid):
        if opCode is None:
            return
        opCode = Operator.constOperator[Token.tokenValueMap[opCode.type]]
        instruction = Instruction(iid, opCode, x, y)
        block.addinstruction(instruction)

    @dispatch(IBlock, OperatorCode, IResult, IResult)
    def compute(self, block, opCode, x, y):
        if opCode is None:
            return
        instruction = None
        if opCode == OperatorCode.move or opCode == OperatorCode.store:
            self.pc = self.pc
            instruction = Instruction(self.pc, opCode, y, x)
        elif opCode == OperatorCode.load:
            self.pc = self.pc
            instruction = Instruction(self.pc, opCode, None, y)
        else:
            self.pc = self.pc
            instruction = Instruction(self.pc, opCode, x, y)

        block.addinstruction(instruction)

    @dispatch(IBlock, OperatorCode, type(None), IResult)
    def compute(self, block, opCode, x, y):
        if opCode != OperatorCode.load:
            return
        self.pc = self.pc
        instruction = Instruction(self.pc, opCode, None, y)
        block.addinstruction(instruction)

    @dispatch(IBlock, Token, type(None), type(None))
    def compute(self, block, opToken, x, y):
        opCode = self.operator.getToken(opToken)
        self.pc = self.pc
        instruction = Instruction(self.pc, opCode, x, y)
        block.addinstruction(instruction)

    @dispatch(IBlock, Token, IResult, type(None))
    def compute(self, block, opToken, x, y):
        opCode = self.operator.getToken(opToken)
        self.pc = self.pc
        instruction = Instruction(self.pc, opCode, x, y)
        block.addinstruction(instruction)

    @dispatch(IBlock, Token, IResult, IResult)
    def compute(self, block, opToken, x, y):
        opCode = self.operator.getToken(opToken)
        self.compute(block, opCode, x, y)


    def createConstantToken(self, val, id):
        return Token(str(val), "number", id)

    def loadAarray(self, block, varManager, varResult, constants):
        print("\n ***********load array")
        array = varResult.variable
        x = array.dimensionList
        y = array.indexList
        z = [0] * len(x)
        constant_block = block.findroot(block)


        for i in range(len(y)):
            for j in range(i + 1, len(x)):
                self.pc+=1
                if z[i] == 0:
                    if self.createConstantToken(x[j], self.pc+1).value not in constants:
                        constants[self.createConstantToken(x[j], self.pc+1).value] = self.pc+1
                        x_j = ConstantResult(x[j], self.pc + 1)
                        self.compute(constant_block, self.createConstantToken(x[j], self.pc + 1), x_j, None,
                                     self.pc + 1)
                        x_j = ConstantResult(x[j])
                        self.compute(block, OperatorCode.mul, y[i], x_j)
                        z[i] = InstructionResult(self.pc)
                        self.pc = self.pc + 2
                    else:
                        constant_pc = constants[self.createConstantToken(x[j], self.pc + 1).value]
                        x_j = ConstantResult(x[j], constant_pc)
                        self.compute(block, OperatorCode.mul, y[i], x_j)
                        z[i] = InstructionResult(self.pc)
                        self.pc = self.pc + 2
                else:
                    if self.createConstantToken(x[j], self.pc + 1).value not in constants:
                        constants[self.createConstantToken(x[j], self.pc + 1).value] = self.pc+1
                        x_j = ConstantResult(x[j], self.pc+1)
                        self.compute(constant_block, self.createConstantToken(x[j], self.pc + 1), x_j, None, self.pc + 1)
                        x_j = ConstantResult(x[j])
                        self.compute(block, OperatorCode.mul, z[i], x_j)
                        z[i] = InstructionResult(self.pc)
                        self.pc = self.pc + 2
                    else:
                        constant_pc = constants[self.createConstantToken(x[j], self.pc + 1).value]
                        x_j = ConstantResult(x[j], constant_pc)
                        self.compute(block, OperatorCode.mul, y[i], x_j)
                        z[i] = InstructionResult(self.pc)
                        self.pc = self.pc + 2
            if i + 1 == len(x):
                z[i] = y[i]

        if len(z) == 1:
            self.compute(block, OperatorCode.add, ConstantResult("Frame Pointer", 0), z[0])
            z[0] = InstructionResult(self.pc)
            self.pc += 2
        else:
            for i in range(1, len(z)):
                self.compute(block, OperatorCode.add, z[i - 1], z[i])
                z[i] = InstructionResult(self.pc)
                self.pc += 2

        #self.compute(block, OperatorCode.mul, z[len(x) - 1], ConstantResult(4))
        if not self.createConstantToken(4, self.pc + 1).value in constants:
            constants[self.createConstantToken(4, self.pc + 1).value] = self.pc + 1
            self.compute(constant_block, self.createConstantToken(4, self.pc + 1), ConstantResult(4, self.pc+1), None, self.pc + 1)
            self.compute(block, OperatorCode.mul, z[len(x) - 1], ConstantResult(4, self.pc+1))
            self.pc = self.pc + 2
        else:
            constant_pc1 = constants[self.createConstantToken(4, self.pc + 1).value]
            self.compute(block, OperatorCode.mul, z[len(x) - 1], ConstantResult(4, constant_pc1))
            self.pc = self.pc + 2

        if not self.createConstantToken(array.array_addr, self.pc + 1).value in constants:
            constants[self.createConstantToken(array.array_addr, self.pc + 1).value] = self.pc + 1
            self.compute(constant_block, self.createConstantToken(array.array_addr, self.pc + 1), ConstantResult(array.array_addr, self.pc+1), None, self.pc + 1)
            self.compute(block, OperatorCode.adda, InstructionResult(self.pc - 2), ConstantResult(array.array_addr, self.pc+1))
            self.pc = self.pc + 2
        else:
            constants_pc2 = constants[self.createConstantToken(array.array_addr, self.pc + 1).value]
            self.compute(block, OperatorCode.adda, InstructionResult(self.pc - 2),
                         ConstantResult(array.array_addr, constants_pc2))
            self.pc += 2


        #self.pc = self.pc + 1
        #self.compute(block, OperatorCode.adda, InstructionResult(self.pc - 1), ConstantResult(array.array_addr))
        #self.pc = self.pc + 1
        print(f"load Aarray constants {constants}")
        print(f"array address {array.array_addr}")
        self.compute(block, OperatorCode.load, None, InstructionResult(self.pc - 2))
        self.pc = self.pc + 1

    def storeArray(self, block, varManager, lrhResult, rrResult, constants):
        print("*****************\nstore array\n")
        array = lrhResult.variable
        x = array.dimensionList
        y = array.indexList
        z = [0] * len(x)
        print(f"array start pc num: {self.pc}")
        self.pc+= len(x) + 1
        constant_block = block.findroot(block)


        for i in range(len(y)):
            for j in range(i + 1, len(x)):
                if z[i] == 0:
                    if self.createConstantToken(x[j], self.pc+1).value not in constants:
                        constants[self.createConstantToken(x[j], self.pc+1).value] = self.pc+1
                        x_j = ConstantResult(x[j], self.pc + 1)
                        self.compute(constant_block, self.createConstantToken(x[j], self.pc + 1), x_j, None,
                                     self.pc + 1)
                        self.compute(block, OperatorCode.mul, y[i], x_j)
                        z[i] = InstructionResult(self.pc)
                        self.pc = self.pc + 2
                    else:
                        constant_pc = constants[self.createConstantToken(x[j], self.pc+1).value]
                        x_j = ConstantResult(x[j], constant_pc)
                        self.compute(block, OperatorCode.mul, y[i], x_j)
                        z[i] = InstructionResult(self.pc)
                        self.pc = self.pc + 2

                else:
                    if self.createConstantToken(x[j], self.pc + 1).value not in constants:
                        constants[self.createConstantToken(x[j], self.pc + 1).value] = self.pc+1
                        x_j = ConstantResult(x[j], self.pc+1)
                        self.compute(constant_block, self.createConstantToken(x[j], self.pc + 1), x_j, None, self.pc + 1)
                        self.compute(block, OperatorCode.mul, z[i], x_j)
                        z[i] = InstructionResult(self.pc)
                        self.pc = self.pc + 2
                    else:
                        constant_pc = constants[self.createConstantToken(x[j], self.pc + 1).value]
                        x_j = ConstantResult(x[j], constant_pc)
                        self.compute(block, OperatorCode.mul, y[i], x_j)
                        z[i] = InstructionResult(self.pc)
                        self.pc = self.pc + 2

            if i + 1 == len(x):
                z[i] = y[i]

        # print(f"DEBUG: show the array length {len(z)}")


        for i in range(1, len(z)):
            print("DEBUG: Have the array element been ever stored?")
            self.compute(block, OperatorCode.add, z[i - 1], z[i])
            z[i] = InstructionResult(self.pc)
            self.pc = self.pc + 2


        print(f"array end pc num: {self.pc}")
        if not self.createConstantToken(4, self.pc + 1).value in constants:
            constants[self.createConstantToken(4, self.pc + 1).value] = self.pc + 1
            self.compute(constant_block, self.createConstantToken(4, self.pc + 1), ConstantResult(4, self.pc+1), None, self.pc + 1)
            self.compute(block, OperatorCode.mul, z[len(x) - 1], ConstantResult(4, self.pc+1))
            self.pc = self.pc + 2
        else:
            constant_pc1 = constants[self.createConstantToken(4, self.pc + 1).value]
            self.compute(block, OperatorCode.mul, z[len(x) - 1], ConstantResult(4, constant_pc1))
            self.pc = self.pc + 2

        if len(z) == 1:
            self.compute(block, OperatorCode.add, ConstantResult("Frame Pointer", 0), z[0])
            z[0] = InstructionResult(self.pc)
            self.pc += 2

        if not self.createConstantToken(array.array_addr, self.pc + 1).value in constants:
            constants[self.createConstantToken(array.array_addr, self.pc + 1).value] = self.pc+1
            self.compute(constant_block, self.createConstantToken(array.array_addr, self.pc + 1), ConstantResult(array.array_addr, self.pc+1), None, self.pc + 1)
            self.compute(block, OperatorCode.adda, InstructionResult(self.pc - 2), ConstantResult(array.array_addr, self.pc+1))
            self.pc = self.pc + 2
        else:
            constants_pc2 = constants[self.createConstantToken(array.array_addr, self.pc + 1).value]
            self.compute(block, OperatorCode.adda, InstructionResult(self.pc - 2),
                         ConstantResult(array.array_addr, constants_pc2))
            self.pc+=2


        self.compute(block, OperatorCode.store, InstructionResult(self.pc - 2), rrResult)
        self.pc = self.pc + 1

    def declareVariable(self, block, varManager, varResult, put):
        if varManager.isVariable(varResult.variable):
            print("variable already declared")
            sys.exit(-1)
            return
        else:
            #print("declare variable!")
            #print(block.id)
            varManager.updatessamap(varResult.variable.address, varResult.variable.version)
            block.global_ssa[varResult.variable.address] = varResult.variable.version
            if isinstance(varResult.variable, Array):  # add subarray to the array as an object
                arrayvar = varResult.variable
                varManager.addArray(arrayvar.address, arrayvar)
            else:  # add variable to the array
                varManager.addVariable(varResult.variable.address)
                if varResult.variable.version == Constants.FORMAL_PARAMETER_VERSION:
                    newResult = varResult.clone()
                    newResult.variable.version = self.pc
                    varManager.updatessamap(varResult.variable.address, self.pc)
                    block.global_ssa[varResult.variable.address] = self.pc
                    self.compute(block, OperatorCode.move, newResult, varResult)
                    #self.pc = Constants.INSTRUCTION_START_COUNTER
                    #self.pc = self.pc + 1
                    self.pc = 0

                elif put:
                    self.compute(block, OperatorCode.move, varResult, ConstantResult("Frame Pointer", 0))
                    #self.pc = Constants.INSTRUCTION_START_COUNTER
                    #self.pc += 1
                    self.pc = 0

