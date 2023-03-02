from DataStructure.PhiInstruction import PhiInstruction
from DataStructure.Manager.PhiManager import PhiManager
from DataStructure.Manager.VariableManager import VariableManager
from IR.IRGenerator import IrGenerator
from DataStructure.DataResult.RegisterResult import RegisterResult
from util.Constants import Constants
from DataStructure.Blocks.Block import Block
from DataStructure.Blocks.IfBlock import IfBlock
from DataStructure.Manager.VariableManager import VariableManager
from DataStructure.Blocks.IBlock import IBlock
from DataStructure.Blocks.JoinBlock import JoinBlock
from multipledispatch import dispatch
from DataStructure.Instruction import Instruction, InstructionResult
from DataStructure.Operator import Operator, OperatorCode
from DataStructure.DataResult.ConstantResult import ConstantResult
from DataStructure.DataResult.RegisterResult import RegisterResult
from DataStructure.DataResult.VariableResult import VariableResult
from DataStructure.Variable import Variable


# TODO: Implementing while block 3/1/2022.
# There might be bug exists, need to check it in parser.
class WhileBlock(Block):
    def __init__(self, id):
        super().__init__(id)
        self.loopblock = None
        self.followBlock = None
        self.phiManager = PhiManager()

    def setLoopBlock(self, block):
        self.loopblock = block

    def getLoopBlock(self):
        return self.loopblock

    def setFollowBlock(self, block):
        self.followBlock = block

    def getFollowBlock(self):
        return self.followBlock

    def getInstruction(self, pc):

        instruction = super().getinstruction(pc)
        if instruction is not None:
            return instruction

        for i in self.phiManager.phis.keys():
            if i == pc:
                return self.phiManager.phis[i]
        return None

    def getPhiMap(self):
        phimap = {}
        for i in self.phiManager.phis.items():
            phimap.update(i)
        return phimap

    def getPhis(self):
        if self.phiManager is not None and self.phiManager.phis is not None and len(self.phiManager.phis.values()):
            return list(self.phiManager.phis.values())
        return []

    def toString(self):
        out = ""
        phiinstructions = list(self.phiManager.phis.values())
        out += super().tostringUtil(phiinstructions)
        out += super().tostring()

    def fixupbranch(self, iid, targetBlock):
        self.getInstruction(iid).operandy.set(targetBlock)


    def updateIncomingVarManager(self, globalVarManager, localVarManager):
        globalVarManager.setssamp(self.global_ssa)
        if localVarManager is not None and len(self.local_ssa) > 0:
            localVarManager.setssamp(self.local_ssa)

    @dispatch(dict, IrGenerator, dict, dict, dict)
    def createPhis(self, addr2ident,irGenerators,pssamap, lssamap, ssamap):
        for key in pssamap.keys():
            x = Variable(addr2ident[key], key)
            print(f"Debug create_phis, {pssamap} {lssamap}")
            if pssamap[key] != lssamap[key]:
                print("this is true")
                x1 = VariableResult()
                x1.set(Variable(addr2ident[key], key, pssamap[key]))
                x2 = VariableResult()
                x2.set(Variable(addr2ident[key], key, lssamap[key]))

                self.phiManager.addPhi(self, x, x1, x2)
                ssamap[key] = x.version

    @dispatch(IBlock, dict, IrGenerator)
    def createPhis(self, block, addr2ident, irGenerators):
        print("create phis!!!!!!")
        self.createPhis(addr2ident, irGenerators, self.parent.global_ssa, block.getglobalssa(), self.global_ssa)

    @dispatch(IBlock, list, IrGenerator)
    def updatePhiVarOccurances(self, block, instructions, irGenerators):
        for i in instructions:
            if isinstance(i.operandx, VariableResult):
                var_update = i.operandx.variable
                if var_update.address in self.phiManager.phis.keys():
                    phi = self.phiManager.phis[var_update.address]
                    if var_update.version == phi.operandx.variable.version:
                        var_update.version = phi.variable.version

            if isinstance(i.operandy, VariableResult):
                var_update = i.operandy.variable
                if var_update.address in self.phiManager.phis.keys():
                    phi = self.phiManager.phis[var_update.address]
                    if var_update.version == phi.operandx.variable.version:
                        var_update.version = phi.variable.version


    @dispatch(IBlock, IrGenerator)
    def updatePhiVarOccurances(self, block, irGenerators):
        if isinstance(block, WhileBlock) or isinstance(block, JoinBlock):
            block_phi = []
            block_phi = block.getPhi()
            for i in block_phi:
                if i.variable.address in self.phiManager.phis.keys():
                    phiInstr = self.phiManager.phis[i.variable.address]
                    if isinstance(phiInstr.operandx, VariableResult):
                        if isinstance(i.operandx, VariableResult):
                            var_update = i.operandx.variable
                            if var_update.version == phiInstr.operandx.variable.version:
                                var_update.version = phiInstr.variable.version
                        if isinstance(i.operandy, VariableResult):
                            var_update = i.operandy.variable
                            if var_update.version == phiInstr.operandx.variable.version:
                                var_update.version = phiInstr.variable.version
        self.updatePhiVarOccurances(block, block.getInstructions(), irGenerators)

    @dispatch(IrGenerator)
    def updatePhiVarOccurances(self, irGenerators):
        self.updatePhiVarOccurances(self, self.instructions, irGenerators)
        nBlocks = []
        nfBlocks = []
        nBlocks.append(self.loopblock)
        alreadyVisitedBlocks = [False]*2000
        alreadyVisitedBlocks[self.id] = True
        while len(nBlocks) != 0 and len(nfBlocks) !=0:
            if len(nBlocks) != 0:
                cBlock = nBlocks.pop()
            else:
                cBlock = nfBlocks.pop()

            alreadyVisitedBlocks[cBlock.getid()] = True
            self.updatePhiVarOccurances(cBlock, irGenerators)

            if isinstance(cBlock, WhileBlock):
                if cBlock.getLoopBlock() is not None:
                    if not alreadyVisitedBlocks[cBlock.getLoopBlock().getid()]:
                        nBlocks.append(cBlock.getLoopBlock())
                if cBlock.getFollowBlock() is not None:
                    if not alreadyVisitedBlocks[cBlock.getFollowBlock().getid()]:
                        nfBlocks.append(cBlock.getFollowBlock())

            if isinstance(cBlock, IfBlock):
                if cBlock.getThenBlock() is not None:
                    if not alreadyVisitedBlocks[cBlock.getThenBlock().getid()]:
                        nBlocks.append(cBlock.getThenBlock())

                    if cBlock.getElseBlock() is not None:
                        if not alreadyVisitedBlocks[cBlock.getElseBlock().getid()]:
                            nBlocks.append(cBlock.getElseBlock())

                    if cBlock.getJoinBlock() is not None:
                        if not alreadyVisitedBlocks[cBlock.getJoinBlock().getid()]:
                            nfBlocks.append(cBlock.getJoinBlock())
            else:
                if cBlock.getchild() is not None:
                    if isinstance(cBlock.getchild(), JoinBlock) == False and\
                        alreadyVisitedBlocks[cBlock.getchild().getid()] == False:
                        nBlocks.append(cBlock.getchild())

    def find_instr_from_iid(self, iid, cfg):
        for block in cfg.blocks:
            for i in block.instructions:
                if i.id == iid:
                    return i


    def recursion_lookup(self, operand, block, cfg, id):
        print(f"block id {block.id}, self id {self.id}")
        # breakpoint()
        if block.id < self.id:
            return None
        if operand is None:
            print("Warning: operand is None!!!!")

        mask = False
        for ids in reversed(range(len(block.instructions))):
            instr_temp = block.instructions[ids]
            if instr_temp.opcode == OperatorCode.move:
                if isinstance(instr_temp.operandy, VariableResult):
                    if isinstance(operand, VariableResult):
                        if operand.variable.address == instr_temp.operandy.variable.address:
                            mask = True
                            return InstructionResult(instr_temp.id)
                    elif isinstance(operand, InstructionResult):
                        instr_temp1 = self.find_instr_from_iid(operand.iid, cfg)
                        if instr_temp1.opcode == OperatorCode.move:
                            if instr_temp1.operandy.variable.address == instr_temp.operandy.variable.address:
                                mask = True
                                return InstructionResult(instr_temp.id)
                        else:
                            continue
                else:
                    print("Assignment instruction for right operand.")
            elif instr_temp.opcode == OperatorCode.phi:
                temp_variable = instr_temp.variable
                if isinstance(operand, VariableResult):
                    if operand.variable.address == temp_variable.address:
                        mask = True
                        return InstructionResult(instr_temp.id)
                elif isinstance(operand, InstructionResult):
                    instr_temp1 = self.find_instr_from_iid(operand.iid, cfg)
                    if instr_temp1.opcode == OperatorCode.move:
                        if instr_temp1.operandy.variable.address == temp_variable.address:
                            mask = True
                            return InstructionResult(instr_temp.id)
                    else:
                        continue
        if mask:
            print("Warning: Recursion in while might be wrong.")
        if block.id == 1:
            return None

        return self.recursion_lookup(operand, block.parent, cfg, id)


    def phi_optimization(self, cfg):
        nBlocks = []
        nfBlocks = []

        for b in cfg.blocks:
            block = b
            if block.id >= self.id:
                nBlocks.append(block.id)

        for block_id in nBlocks:
            block = cfg.blocks[block_id]
            if len(block.instructions) == 0:
                continue

            for instr_id in range(len(block.instructions)):
                instr = block.instructions[instr_id]

                if instr.opcode == OperatorCode.move:
                    continue

                if block_id == self.id and instr.opcode == OperatorCode.phi:
                    continue

                if instr.opcode == OperatorCode.phi:
                    block = block
                    if isinstance(block, JoinBlock):
                        left_id = cfg.join_parent[block.id][0]
                        right_id = cfg.join_parent[block.id][1]

                        # define operandx
                        temp_res_var = VariableResult()
                        temp_res_var.set(instr.operandx.variable)
                        temp_res_instr = self.recursion_lookup(instr.operandx, cfg.blocks[left_id], cfg, block_id)
                        temp_res_var.setiid(temp_res_instr.iid)
                        temp_res_var.variable.version = temp_res_instr.iid
                        instr.operandx = temp_res_var

                        # define operandy
                        temp_res_var = VariableResult()
                        temp_res_var.set(instr.operandy.variable)
                        temp_res_instr = self.recursion_lookup(instr.operandy, cfg.blocks[right_id], cfg, block_id)
                        temp_res_var.setiid(temp_res_instr.iid)
                        temp_res_var.variable.version = temp_res_instr.iid
                        instr.operandy = temp_res_var

                    elif isinstance(block, WhileBlock):
                        temp_res_var = VariableResult()
                        temp_res_var.set(instr.operandx.variable)
                        temp_res_instr = self.recursion_lookup(instr.operandx, block.parent, cfg, block_id)
                        temp_res_var.setiid(temp_res_instr.iid)
                        temp_res_var.variable.version = temp_res_instr.iid
                        instr.operandx = temp_res_var
                    continue

                mask_x = False
                mask_y = False

                if isinstance(instr.operandx, ConstantResult):
                    mask_x = True
                if isinstance(instr.operandy, ConstantResult):
                    mask_y = True

                for i in reversed(range(0, instr_id)):
                    if mask_x and mask_y:
                        break

                    instr_temp = block.instructions[i]

                    if instr_temp.opcode == OperatorCode.move:
                        if instr.operandx != None:
                            if isinstance(instr.operandx, VariableResult):
                                if instr.operandx.variable.address == instr_temp.operandy.variable.address:
                                    mask_x = True
                                    instr.operandx = InstructionResult(instr_temp.id)
                            elif isinstance(instr.operandx, InstructionResult):
                                instr_temp1 = self.find_instr_from_iid(instr.operandx.iid, cfg)
                                if instr_temp1.opcode == OperatorCode.move:
                                    if instr_temp1.operandy.variable.address == instr_temp.operandy.variable.address:
                                        mask_x = True
                                        instr.operandx = InstructionResult(instr_temp.id)
                            else:
                                mask_x = True
                        else:
                            mask_x = True

                    if instr_temp.opcode == OperatorCode.phi:
                        if instr.operandy != None:
                            if isinstance(instr.operandy, VariableResult):
                                if instr.operandy.variable.address == instr_temp.operandy.variable.address:
                                    mask_y = True
                                    instr.operandx = InstructionResult(instr_temp.id)
                            elif isinstance(instr.operandy, InstructionResult):
                                instr_temp1 = self.find_instr_from_iid(instr.operandx.iid, cfg)
                                if instr_temp1.opcode == OperatorCode.move:
                                    if instr_temp1.operandy.variable.address == instr_temp.operandy.variable.address:
                                        mask_y = True
                                        instr.operandy = InstructionResult(instr_temp.id)
                            else:
                                mask_y = True
                        else:
                            mask_y = True

                        if instr.operandy != None:
                            if isinstance(instr.operandy, VariableResult):
                                if instr_temp.variable.address == instr.operandy.variable.address:
                                    mask_y = True
                                    instr.operandy = InstructionResult(instr_temp.id)
                            elif isinstance(instr.operandy, InstructionResult):
                                instr_temp1 = self.find_instr_from_iid(instr.operandy.iid, cfg)
                                if instr_temp1.opcode == OperatorCode.move:
                                    if instr_temp1.operandy.variable.address == instr_temp.variable.address:
                                        mask_y = True
                                        instr.operandy = InstructionResult(instr_temp.id)
                            else:
                                mask_y = True
                        else:
                            mask_y = True
                    else:
                        continue

                if mask_x and mask_y:
                    continue
                else:
                    if block.parent.id < self.id:
                        continue
                    else:
                        final_res_x = None
                        final_res_y = None
                        if mask_x == False and mask_y == True:
                            final_res_x = self.recursion_lookup(instr.operandx, block.parent, cfg, instr_id)
                            final_res_y = instr.operandy
                        elif mask_x == True and mask_y == False:
                            final_res_x = instr.operandx
                            final_res_y = self.recursion_lookup(instr.operandy, block.parent, cfg, instr_id)
                        else:
                            final_res_x = self.recursion_lookup(instr.operandx, block.parent, cfg, instr_id)
                            final_res_y = self.recursion_lookup(instr.operandy, block.parent, cfg, instr_id)

                        if final_res_x != None:
                            instr.operandx = final_res_x
                        if final_res_y != None:
                            instr.operandy = final_res_y
                        continue














