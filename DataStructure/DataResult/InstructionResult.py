from DataStructure.DataResult.IResult import IResult

class InstructionResult(IResult):
    def __init__(self, iid=-1, constant=None):
        # iid -> instruction id
        # constant -> instruction value
        self.iid = iid
        self.constant = constant

    def set(self, value):
        self.iid = value

    def setiid(self, iid):
        self.iid = iid

    def getiid(self,iid):
        return self.iid

    def clone(self):
        return InstructionResult(self.iid, self.constant)

    def equals(self, result):
        if isinstance(result, InstructionResult):
            return self.iid == result.iid
        return False

    def toInstruction(self):
        return InstructionResult(self.iid)

    def toString(self):
        return f"({self.iid})"
