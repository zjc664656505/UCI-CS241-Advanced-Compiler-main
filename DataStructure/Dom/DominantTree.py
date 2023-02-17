# Build Dominant Tree Node
from DataStructure.Instruction import Instruction
from DataStructure.Operator import OperatorCode
from DataStructure.DataResult.VariableResult import VariableResult
from util.Constants import Constants


class DominantTreeNode:
    id = -1
    instructions = None
    parent = None

    def __init__(self, id):
        self.id = id
        self.instructions = {}
        self.parent = None

    def getParent(self):
        return self.parent

    def setParent(self, node):
        self.parent = node

    def addKill(self, kill):  # handle load operation
        if not OperatorCode.load in self.instructions.keys():
            self.instructions[OperatorCode.load] = []
        for i in kill:
            self.instructions[OperatorCode.load].insert(0, i.clone())

    def add(self, instruction):  # handle store operation
        if instruction.opcode == OperatorCode.store:
            if not OperatorCode.load in self.instructions.keys():
                self.instructions[OperatorCode.load] = []
            self.instructions[OperatorCode.load].append(instruction.clone())
        else:
            if not instruction.opcode in self.instructions.keys():
                self.instructions[instruction.opcode] = []
            self.instructions[instruction.opcode].append(instruction.clone())

    def delete(self, instruction):
        if instruction.opcode in self.instructions.keys():
            temp_instruction = self.instructions[instruction.opcode]
            temp = [ins for ins in temp_instruction if ins.id.equals(instruction.id)]
            self.instructions = temp

    def find(self, instruction):
        if instruction.opcode == OperatorCode.store:
            return Instruction(-2)
        if instruction.opcode == OperatorCode.load:
            if instruction.load in self.instructions.keys():
                for idx in range(len(self.instructions[instruction.opcode]) - 1, -1, -1):
                    if self.instructions[OperatorCode.load][idx].opcode == OperatorCode.store:
                        checker = self.instructions[OperatorCode.load][idx]
                        if isinstance(instruction.operandx, VariableResult) and \
                                isinstance(checker.operandx, VariableResult):
                            xres = instruction.operandx
                            yres = instruction.operandy
                            if xres.isAarry and yres.isArray and xres.variable.address == yres.variable.address:
                                return Instruction(-2)
                    else:
                        if self.instructions[OperatorCode.load][idx].operandy.eqauls(instruction.operandy):
                            if isinstance(instruction.operandy, VariableResult) and \
                                    instruction.operandy.variable.version == Constants.GLOBAL_VARIABLE_VERSION:
                                return self.instructions[instruction.opcode][idx].clone()
            return Instruction(-1)
        if instruction.opcode in self.instructions.keys():
            for idx in range(len(self.instructions[instruction.opcode]) - 1, -1, -1):
                if self.instructions[instruction.opcode][idx].equals(instruction):
                    return self.instructions[instruction.opcode][idx].clone()
        return Instruction(-1)


class DomNodeCSE:

    def __int__(self, id):
        self.id = id
        self.instructions = {}
        self.parent = None

    def getParent(self):
        return self.parent

    def setParent(self, node):
        self.parent = node

    def add(self, instruction):
        if instruction.opcode == OperatorCode.store:
            if not OperatorCode.load in self.instructions.keys():
                self.instructions[OperatorCode.load] = []
            self.instructions[OperatorCode.load].append(instruction)
        else:
            if not instruction.opcode in self.instructions.keys():
                self.instructions[instruction.opcode] = []
            self.instructions[instruction.opcode].append(instruction)

    def find(self, instruction):
        if instruction.opcode == OperatorCode.store:
            return Instruction(-2)
        if instruction.opcode in self.instructions.keys():
            for idx in range(len(self.instructions[instruction.opcode]) - 1, -1, -1):
                if self.instructions[instruction.opcode][idx].equals(instruction):
                    return self.instructions[instruction.opcode][idx]
        return Instruction(-1)
