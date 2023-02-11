from DataStructure.DataResult.IResult import IResult
from DataStructure.DataResult.InstructionResult import InstructionResult

class ConstantResult(IResult):
    def __init__(self, constant: int = 0, iid: int = -1):
        super().__init__()
        self.constant = constant
        self.iid = iid

    def set(self, value):
        if type(value) == str:
            self.constant = int(value)
        elif type(value) == int:
            self.constant = value

    def setiid(self, iid: int):
        self.iid = iid

    def getiid(self):
        return self.iid

    def clone(self):
        cResult = ConstantResult()
        cResult.iid = self.iid
        cResult.constant = self.constant
        return cResult

    def equals(self, result):
        if isinstance(result, ConstantResult):
            return self.constant == result.constant

        return False

    def toInstruction(self):
        return InstructionResult(self.iid, self.constant)

    def toString(self) -> str:
        return f"& {self.constant}"