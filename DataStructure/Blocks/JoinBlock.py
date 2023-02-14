from DataStructure.Blocks.Block import Block
from DataStructure.Blocks.IBlock import IBlock
from DataStructure.Instruction import Instruction
from DataStructure.PhiInstruction import PhiInstruction
from DataStructure.DataResult.VariableResult import VariableResult
from DataStructure.Variable import Variable
from multipledispatch import dispatch
from DataStructure.PhiInstruction import DeleteMode
from DataStructure.Manager import PhiManager
from DataStructure.Manager import VariableManager

class JoinBlock(Block):
    elseBlock = None
    thenBlock = None
    phiManager = None

    def __init__(self, id):
        super().__init__(id)
        self.thenBlock = None
        self.elseBlock = None
        self.phiManager = PhiManager()

    def setThenBlock(self, block):
        self.thenBlock = block

    def getThenBlock(self):
        return self.thenBlock

    def setElseBlock(self, block):
        self.elseBlock = block

    def getThenBlock(self):
        return self.elseBlock

    def getInstruction(self, PC):
        instruction = self.getInstruction(PC)
        if instruction:
            return instruction
        newInstruction = None
        for i in self.phiManager.phis.keys():
            if i == PC:
                newInstruction = self.phiManager.phis[i]
                break
        if newInstruction:
            return newInstruction
        return None

    def getPhiMap(self):
        phimap = {}
        for i in self.phiManager.phis.keys():
            phi = self.phiManager.phis[i]
            if phi.deleteMode == DeleteMode._NOT_DEL:
                phimap[i] = phi
        return phimap

    def getPhi(self):
        if self.phiManager and self.phiManager.phis and len(self.phiManager.phis.values()) > 0:
            return list(self.phiManager.phis.values())
        return []

    def tostring(self):
        sb = ""
        phi_instr = list(self.phiManager.phis.values())
        sb = sb + super().tostringUtil(phi_instr)
        sb = sb + super.tostring()
        return sb


    def updateManager(self, global_manager: VariableManager, local_manager: VariableManager):
        global_manager.setssamap(self.global_ssa)
        if local_manager is not None and len(self.local_ssa) >0:
            local_manager.setssamap(self.local_ssa)

    @dispatch(dict, dict, dict, dict, dict)
    def createPhi(self, addr2ident, issmap, tssmap, essamap, ssamap):
        for i in issmap.keys():
            x = Variable(addr2ident[i], i)
            if issmap[i] != tssmap[i]: # check whether is if then block
                y = VariableResult()
                y.set(Variable(addr2ident[i], i, tssmap[i]))
                z = VariableResult()
                z.set(Variable(addr2ident[i], i, issmap[i]))

                self.phiManager.addPhi(self, x, y, z)
                ssamap[i] = x.version
            if self.elseBlock is not None and (essamap is not None):
                if issmap[i] != essamap[i]: # check whether it's if else block
                    y = VariableResult()
                    y.set(Variable(addr2ident[i], i, issmap[i]))
                    z = VariableResult()
                    z.set(Variable(addr2ident[i], i, essamap[i]))
                    if self.phiManager.isExits(x):
                        self.phiManager.updatePhi(self, x, None, z)
                    else:
                        self.phiManager.addPhi(self, x, y, z)
                        ssamap[i] = x.version

    @dispatch(dict, dict, dict)
    def createPhi(self, addr2ident, lb_ssa, rb_ssa):
        self.freezessa(self.parent.gobal_ssa, self.parent.local_ssa)
        if self.thenBlock is None:
            self.createPhi(addr2ident, self.parent.global_ssa, self.parent.local_ssa,
                           self.elseBlock.global_ssa, self.global_ssa)
            self.createPhi(addr2ident, self.parent.local_ssa, self.parent.local_ssa,
                           self.elseBlock.local_ssa, self.local_ssa)
        elif self.elseBlock is None:
            self.createPhi(addr2ident, self.parent.global_ssa, self.thenBlock.global_ssa,
                           self.parent.global_ssa, self.global_ssa)
            self.createPhi(addr2ident, self.parent.local_ssa, self.thenBlock.local_ssa,
                           self.parent.local_ssa, self.local_ssa)
        else:
            self.createPhi(addr2ident, self.parent.global_ssa, lb_ssa, rb_ssa, self.global_ssa)
            self.createPhi(addr2ident, self.parent.local_ssa, self.thenBlock.local_ssa, self.elseBlock.local_ssa,
                           self.elseBlock)




