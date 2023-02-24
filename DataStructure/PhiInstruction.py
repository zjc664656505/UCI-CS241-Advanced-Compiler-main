from DataStructure.Variable import Variable
from DataStructure.Operator import OperatorCode
from DataStructure.DataResult.IResult import IResult
from DataStructure.Instruction import Instruction
from DataStructure.Instruction import DeleteMode
from DataStructure.DataResult.VariableResult import VariableResult
from DataStructure.DataResult.InstructionResult import InstructionResult
from util.Constants import Constants
from DataStructure.DataResult.IResult import IResult


class PhiInstruction(Instruction):
    variable: Variable = None

    def __init__(self, PC: int, variable: Variable = None, x: IResult = None, y: IResult = None) -> None:
        if (variable is not None) and (x is not None) and (y is not None):
            super().__init__(PC, OperatorCode.phi, x, y)
            self.variable = variable
        else:
            super().__init__(PC)
            self.opcode = OperatorCode.phi
            self.deleteMode = DeleteMode._NOT_DEL
            self.inst_conversion = Instruction(PC)
            self.inst_conversion.opcode = self.opcode

    def clone(self) -> None:
        instr = PhiInstruction(self.id)
        instr.opcode = self.opcode
        if self.operandx is not None:
            instr.operandx = self.operandx.clone()
        if self.operandy is not None:
            instr.operandy = self.operandy.clone()
        instr.deletemode = self.deletemode
        return instr

    def toString(self, flag: bool = False) -> str:
        # print(self.opcode)
        if flag:
            temp_xResult = self.operandx
            temp_yResult = self.operandy
            if isinstance(self.operandx, VariableResult):
                if self.operandx.variable.version != Constants.FORMAL_PARAMETER_VERSION:
                    temp_xResult = InstructionResult(self.operandx.variable.version)
            if isinstance(self.operandy, VariableResult):
                if self.operandy.variable.version != Constants.FORMAL_PARAMETER_VERSION:
                    temp_yResult = InstructionResult(self.operandy.variable.version)
            # print(f"xres type {type(temp_xResult)}, yres type {type(temp_yResult)}")
            # print(f"Debug check phi {self.operandx.iid} {self.operandy.iid}")

            return "{} : phi {} := {} {}".format(self.id, self.variable.toString(), temp_xResult.toString(),
                                                 temp_yResult.toString())
        else:
            return "{} : phi {} := {} {}".format(self.id, self.variable.toString(), self.operandx.toString(),
                                                 self.operandy.toString())

    def equals(self, instruction) -> bool:
        if instruction.opcode == OperatorCode.phi:
            if (self.variable == instruction.variable.address) and (
                    self.variable.version == instruction.variable.version):
                return super().equals(instruction)

        return False

