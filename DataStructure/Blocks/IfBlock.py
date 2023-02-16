from DataStructure.Instruction import Instruction
from DataStructure.DataResult.IResult import IResult
from DataStructure.Blocks.Block import Block
from DataStructure.Blocks.IBlock import IBlock
from DataStructure.DataResult.BranchResult import BranchResult
from DataStructure.Blocks.JoinBlock import JoinBlock

class IfBlock(Block):
    thenBlock = None
    elseBlock = None
    joinBlock = None

    def __init__(self, id:int):
        super().__init__(id)
        self.thenBlock = None
        self.elseBlock = None
        self.joinBlock = None

    def setThenBlock(self, block:IBlock):
        self.thenBlock = block

    def getThenBlock(self):
        return self.thenBlock

    def setElseBlock(self, block:IBlock):
        self.elseBlock = block

    def getElseBlock(self):
        return self.elseBlock

    def setJoinBlock(self, block:IBlock):
        self.joinBlock = block

    def getJoinBlock(self):
        return self.joinBlock

    def fixupBranch(self, iid:int, targetblock:IBlock):
        instruction = self.getinstruction(iid)
        if isinstance(instruction.operandy, BranchResult):
            instruction.operandy.set(targetblock)



