from DataStructure.DataResult.IResult import IResult
from DataStructure.Array import Array
from DataStructure.Variable import Variable
from DataStructure.DataResult.InstructionResult import InstructionResult

class VariableResult(IResult):
    def __init__(self, variable=None, isArray=False, iid=-1):
        super().__init__()
        self.variable = variable
        self.isAarry = isArray
        self.iid = iid

    def set(self, value):
        self.variable = value
        if isinstance(value, Array):
            self.isAarry=True

    def setiid(self,iid):
        self.iid = iid

    def getiid(self):
        return self.iid

    def clone(self):
        variable_res = VariableResult()
        variable_res.set(self.variable.clone())
        variable_res.setiid(self.iid)
        return variable_res

    def equals(self, result):
        if isinstance(result, VariableResult):
            return self.variable.equals(result.variable) and \
                self.isAarry == result.isAarry
        return False

    def toInstruction(self):
        return InstructionResult(self.iid)

    def toString(self):
        if self.isAarry:
            return f"Array {self.variable.toString()}"
        else:
            return f"Variable {self.variable.toString()}"

