from DataStructure.Instruction import Instruction
from DataStructure.DataResult.IResult import IResult
from DataStructure.Blocks.Block import Block
from DataStructure.Blocks.IBlock import IBlock
from DataStructure.DataResult.BranchResult import BranchResult
from DataStructure.Blocks.JoinBlock import JoinBlock

class ConstantBlock(Block):
    def __init__(self, id:int):
        super().__init__(id)
        self.id = id