from DataStructure.Instruction import Instruction
from DataStructure.PhiInstruction import PhiInstruction
from DataStructure.Instruction import DeleteMode
from DataStructure.Blocks.IBlock import IBlock
from DataStructure.Dom.DominantTree import DominantTreeNode, DomNodeCSE
from multipledispatch import dispatch
from DataStructure.Token import Token, TokenType
from DataStructure.Operator import OperatorCode

class Block(IBlock):
    def __init__(self, id):
        super().__init__()
        self.id = id
        self.instructions = []
        self.parent = None
        self.child = None
        self.domTreeNode = DominantTreeNode(id)
        self.domNodeCSE = DomNodeCSE(id)
        self.global_ssa = {}
        self.local_ssa = {}

    def getid(self):
        return self.id

    def def_constant_instruction(self, val):
        for instr in self.instructions:
            if val == instr.operandx.constant:
                self.instructions.remove(instr)

    @dispatch(Instruction)
    def addinstruction(self, instruction):
        self.instructions.append(instruction)

    @dispatch(list)
    def addinstruction(self, instruction):
        self.instructions = self.instructions + instruction


    @dispatch(Instruction, int)
    def addinstruction(self, instruction, idx):
        if idx < len(self.instructions):
            self.instructions.insert(idx, instruction)

    def setparent(self, block):
        self.parent = block
        self.domTreeNode.setParent(block.getdomtreenode())
        self.domNodeCSE.setParent(block.getdomnodecse())

    def findroot(self, block):
        if block.parent:
            block = self.findroot(block.parent)
        return block

    def getparent(self):
        return self.parent

    def setchild(self, block):
        self.child = block

    def getchild(self):
        return self.child

    def getdomtreenode(self):
        return self.domTreeNode

    def getdomnodecse(self):
        return self.domNodeCSE

    def tostring(self):
        return "Block " + str(self.id)

    def tostringUtil(self, instr):
        sb = ""
        instr_str = ""
        for i in instr:
            instr_str = i.toString()

            if instr_str is not None and instr_str != "":
                sb = sb+ instr_str + "||"
                instr_str = ""
        return sb

    def getinstruction(self, pc):
        mark = 0
        index = 0
        for i in self.instructions:
            if i.id == pc:
                mark = 1
                break
            else:
                index += 1
        if mark == 1:
            return self.instructions[index]
        return None

    def freezessa(self, global_ssa, local_ssa):
        self.global_ssa.update(global_ssa)
        if local_ssa:
            self.local_ssa.update(local_ssa)

    def getglobalssa(self):
        return self.global_ssa

    def getlocalssa(self):
        return self.local_ssa

    def addKill(self, kill):
        self.domTreeNode.addKill(kill)

    def searchcommonsubexpression(self, instruction):
        commonsubexpression = self.domTreeNode.find(instruction)
        if commonsubexpression.id != -2:
            if commonsubexpression.id == -1:
                if self.parent:
                    return self.parent.searchcommonsubexpression(instruction)
                else:
                    return commonsubexpression
        return None

    def addcommonsubexpression(self, instruction):
        self.domNodeCSE.add(instruction)

    def getsubexpression(self, instruction):
        return self.domTreeNode.add(instruction)

