from DataStructure.Instruction import Instruction
from multipledispatch import dispatch
from DataStructure.Dom.DominantTree import DominantTreeNode

class IBlock:
    def getid(self):
        pass

    @dispatch()
    def getinstruction(self):
        pass

    @dispatch(Instruction)
    def addinstruction(self, instruction):
        pass

    @dispatch(Instruction, int)
    def addinstruction(self, instruction, idx):
        pass

    @dispatch(list)
    def addinstruction(self, instruction):
        pass

    def getinstruction(self, pc):
        pass

    def setparent(self, block):
        pass

    def getblock(self):
        pass

    def setchild(self, block):
        pass

    def getchild(self):
        pass

    def tostring(self):
        pass

    def freezessa(self, global_ssa, local_ssa):
        pass

    def getglobalssa(self):
        pass

    def getlocalssa(self):
        pass

    def searchcommonsubexpression(self, instruction):
        pass

    def searchcse(self, instruction):
        pass

    def addsubexpression(self, instruction):
        pass

    def getdominatetreenode(self):
        pass

    def getdominantnodecse(self):
        pass

    def setdominatetreenode(self, node):
        pass
