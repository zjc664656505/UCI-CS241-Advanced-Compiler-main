from DataStructure.Token import Token, TokenType
from DataStructure.Blocks.IBlock import IBlock
from DataStructure.DataResult.IResult import IResult
from DataStructure.DataResult.InstructionResult import InstructionResult

class BranchResult(IResult):
    condition=None
    fixuplocation=-1
    targetBlock=None
    iid=-1

    def __init__(self, condition=None, fixuplocation=-1, targetBlock=None):
        super().__init__()
        self.condition = condition
        self.fixuplocation = fixuplocation
        self.targetBlock = targetBlock

    def set(self, value):
        if isinstance(value, int):
            self.fixuplocation = value
        elif isinstance(value, IBlock):
            self.targetBlock = value

    def setiid(self, iid):
        self.iid = iid

    def getiid(self):
        return self.iid

    def clone(self):
        bResult = BranchResult()
        bResult.iid = self.iid
        if self.targetBlock is not None:
            bResult.targetBlock = self.targetBlock
        else:
            bResult.targetBlock = None
        bResult.condition = self.condition
        bResult.fixuplocation = self.fixuplocation
        return bResult

    def equals(self, result):
        if isinstance(result, BranchResult):
            return (self.condition.type == result.condition.type) and  (self.targetBlock.getid() == result.targetBlock.getid())
        return False

    def toInstruction(self):
        return InstructionResult(self.iid)

    def toString(self):
        return "[" + str(self.targetBlock.getid()) + "]"


