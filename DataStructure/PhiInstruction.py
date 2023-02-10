from DataStructure.Variable import Variable
from DataStructure.Operator import OperatorCode
from DataStructure.DataResult.IResult import IResult
from DataStructure.Instruction import Instruction
from DataStructure.Instruction import DeleteMode
from DataStructure.DataResult.VariableResult import VariableResult
from DataStructure.DataResult.InstructionResult import InstructionResult
from util import Constants

class PhiInstruction(Instruction):
    variable = None
    def __int__(self, COPY_PROP, variable, x, y):
        if variable and x and y:
            super().__init__(COPY_PROP, OperatorCode.phi, x, y)
            self.variable = variable
        else:
            super().__int__()
            self.opcode = OperatorCode.phi
            self.deletemode = DeleteMode._NOT_DEL
            self.inst_conversion = Instruction(COPY_PROP)
            self.inst_conversion.opcode = self.opcode

    def clone(self):
        instr = PhiInstruction(self.id)
        instr.opcode = self.opcode
        if self.operandx is not None:
            instr.operandx = self.operandx.clone()
        if self.operandy is not None:
            instr.operandy = self.operandy.clone()
        instr.deletemode = self.deletemode
        return instr

    def toString(self, flag=False):
        if flag:
            xres = self.operandx
            yres = self.operandy
            if isinstance(self.operandx, VariableResult):
                if self.operandx.variable.version != Constants.FORMAL_PARAMETER_VERSION:
                        xres = InstructionResult(self.operandx.variable.version)
            if isinstance(self.operandy, VariableResult):
                if self.operandy.variable.version != Constants.FORMAL_PARAMETER_VERSION:
                        yres = InstructionResult(self.operandy.variable.version)
            return f"{self.id} - phi {self.variable.toString()} = {xres.toString()} {yres.toString()}"
        else:
            return f"{self.id} - phi {self.variable.toString()} = {self.operandx.toString()} {self.operandy.toString()}"

    def equals(self, instr):
        if instr.opcode == OperatorCode.phi:
            if self.variable == instr.variable.address and \
                self.variable.version == instr.variable.version:
                return super().equals(instr)
        return False