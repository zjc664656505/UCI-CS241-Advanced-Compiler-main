from DataStructure.Blocks.IBlock import IBlock
from DataStructure.DataResult.IResult import IResult
from IR.IrGenerator import IrGenerator
from DataStructure.Variable import Variable
from DataStructure.PhiInstruction import PhiInstruction

class PhiManager:
    def __init__(self):
        self.phis = {}
        self.iCodeGenerator = IrGenerator()

    def isExits(self, x):
        return x.address in self.phis.keys()


    def updatePhi(self, block, x, y, z):
        if self.isExits(x):
            if y is not None and z is not None:
                self.phis[x.address].operandx = y
                self.phis[x.address].operandy = z
                self.phis[x.address].variable.version = x.version
            elif y is None:
                self.phis[x.address].operandy = y
                self.phis[x.address].variable.version = x.version
            elif z is None:
                self.phis[x.address].operandy = y
                self.phis[x.address].variable.version = x.version
            else:
                self.phis[x.address].variable.version = x.version

    def addPhi(self, block, x, y, z):
        if not self.isExits(x):
            phi_instruction = PhiInstruction(self.iCodeGenerator.getPC())
            self.iCodeGenerator.incrementPC()
            x.version = phi_instruction.id
            phi_instruction.variable = x
            phi_instruction.operandx = y
            phi_instruction.operandy = z
            self.phis[x.address] = phi_instruction
        else:
            self.updatePhi(block, x, y, z)
