import enum
from DataStructure.Operator import OperatorCode
from DataStructure.DataResult.IResult import IResult
from DataStructure.DataResult.VariableResult import VariableResult
from util.Constants import Constants
from DataStructure.Variable import Variable
from DataStructure.DataResult.InstructionResult import InstructionResult
from DataStructure.DataResult.ConstantResult import ConstantResult

class DeleteMode(enum.Enum):
    COPY_PROP = 0x0
    CSE = 0x1
    DCE = 0x2
    NUMBER = 0x3
    _NOT_DEL = 0x4

class Instruction:
    def __init__(self, COPY_PROP: int=None, opcode:OperatorCode=None, x:IResult=None,
                 y: IResult=None, create:bool=True, res_CSE=None):
        self.id = COPY_PROP
        self.opcode = opcode
        self.operandx: InstructionResult = x
        self.operandy: InstructionResult = y
        self.deletemode = DeleteMode._NOT_DEL
        self.res_CSE = res_CSE
        # if self.operandx and self.operandy:
        #    print(f"DEBUG Instruction x:{self.operandx.iid}, y:{self.operandy.iid}")

        if create:
            self.inst_conversion = Instruction(COPY_PROP, create=False)
            self.inst_conversion.opcode = opcode

    def setInstructionOprand(self, rResult, bool_operandX):
        if rResult:
            if isinstance(rResult, VariableResult) and rResult.isAarry == False:
                variable = rResult.variable
                if variable.version != Constants.FORMAL_PARAMETER_VERSION and \
                    variable.version != Constants.GLOBAL_VARIABLE_VERSION:
                    if bool_operandX:
                        self.inst_conversion.operandx = InstructionResult(variable.version)
                    else:
                        self.inst_conversion.operandy = Instruction(variable.version)
                else:
                    if bool_operandX:
                        self.inst_conversion.operandx = rResult
                    else:
                        self.inst_conversion.operandy = rResult
            else:
                if bool_operandX:
                    self.inst_conversion.operandx = rResult
                else:
                    self.inst_conversion.operandy = rResult

    def setInstruction(self, x, y):
        self.setInstructionOprand(x, True)
        self.setInstructionOprand(y, False)


    def setInstructionFromConversion(self, conversion_instr):
        self.inst_conversion = conversion_instr


    def clone(self):
        return Instruction(self.id, self.opcode, self.operandx, self.operandy)

    def setExternel(self, id, opcode, x, y):
        self.id = id #instruction id
        self.opcode = opcode # operator code
        self.operandx = x # operand on left
        self.operandy = y  # operand on right

    def toString(self, flag):
        res = ""
        if self.operandx and self.operandy:
            if flag:
                xres = self.operandx
                yres = self.operandy
                if isinstance(self.operandx, VariableResult):
                    if self.operandx.variable.version != Constants.FORMAL_PARAMETER_VERSION:
                        if self.opcode != OperatorCode.move:
                            # print(f"DEBUG xres: {self.operandx.variable.name}: {self.operandx.variable.version}")
                            xres = InstructionResult(self.operandx.variable.version)
                if isinstance(self.operandy, VariableResult):
                    if self.operandy.variable.version != Constants.FORMAL_PARAMETER_VERSION:
                        if self.opcode != OperatorCode.move:
                            #print(f"DEBUG yres: {self.operandy.variable.name}: {self.operandy.variable.version}")
                            yres = InstructionResult(self.operandy.variable.version)
                #print(f"DEBUG XRES: {self.operandx.variable.name}, YRES: {self.operandy.variable.name}")
                res = f"{self.id}: {self.opcode.name} {xres.toString()} {yres.toString()}"
                # print(f"DEBUG Instruction toString {xres.iid}")
            else:
                res = f"{self.id}: {self.opcode.name} {self.operandx.toString()} {self.operandy.toString()}"
        elif self.operandx is not None and self.operandy is None:
            #print("OPERANDX IS not NONE")
            if flag:
                xres = self.operandx
                if isinstance(self.operandx, VariableResult):
                    if self.operandx.variable.version != Constants.FORMAL_PARAMETER_VERSION:
                        xres = InstructionResult(self.operandx.variable.version)
                    res = f"{self.id}: {self.opcode.name} {xres.toString()}"
                elif isinstance(self.operandx, ConstantResult):
                    res = f"{self.id}: {self.opcode.name} #{self.operandx.constant}"
                else:
                    res = f"{self.id}: {self.opcode.name} {xres.toString()}"
                # print(f"DEBUG Instruction toString {res}")
            else:
                if isinstance(self.operandx, ConstantResult):
                    res = f"{self.id} {self.opcode.name} #{self.operandx.constant}"
                else:
                    res = f"{self.id}: {self.opcode.name} {self.operandx.toString()}"
        elif self.operandx is None and self.operandy is not None:
            if flag:
                yres = self.operandy
                if isinstance(self.operandy, VariableResult):
                    if self.operandy.variable.version != Constants.FORMAL_PARAMETER_VERSION:
                        yres = InstructionResult(self.operandy.variable.version)
                res = f"{self.id}: {self.opcode.name} {yres.toString()}"
            else:
                res = f"{self.id}: {self.opcode.name} {self.operandy.toString()}"
        else:
            res = f"{self.id}: {self.opcode.name}"

        return res

    def equals(self, instr):
        if self.opcode == instr.opcode:
            if self.operandx and self.operandy:
                res = self.operandx.equals(instr.operandx) and self.operandy.equals(instr.operandy)
                if self.opcode == OperatorCode.mul or self.opcode == OperatorCode.add and res == False:
                    res = self.operandx.equals(instr.operandy) and \
                        self.operandy.equals(instr.operandx)
            elif self.operandx is None and self.operandy is not None:
                return instr.operandx is None and self.operandy.equals(instr.operandy)
            elif self.operandx is not None and self.operandy is None:
                return self.operandx.equals(instr.operandx) and instr.operandy is None
            else:
                return instr.operandx is None and instr.operandy is None

