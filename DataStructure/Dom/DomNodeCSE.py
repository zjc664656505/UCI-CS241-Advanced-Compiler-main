# Define Dominant Tree Node Common Sub-expression Elimination
from DataStructure.Instruction import Instruction
from DataStructure.Operator import OperatorCode


class DomNodeCSE:
    def __int__(self, id=-1):
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
            for idx in range(len(self.instructions[instruction.opcode])-1, -1, -1):
                if self.instructions[instruction.opcode][idx].equals(instruction):
                    return self.instructions[instruction.opcode][idx]
        return Instruction(-1)