# build control flow graph
from util.Constants import Constants
from DataStructure.Variable import Variable
from DataStructure.Instruction import DeleteMode, Instruction
from DataStructure.DataResult.IResult import IResult
from DataStructure.DataResult.VariableResult import VariableResult
from DataStructure.Blocks.Block import Block
from IR.IRGenerator import IrGenerator
from DataStructure.Blocks.JoinBlock import JoinBlock
from DataStructure.Blocks.IfBlock import IfBlock
from DataStructure.Blocks.ConstantBlock import ConstantBlock
# TODO: while block needs to be implemented later on
from DataStructure.Blocks.WhileBlock import WhileBlock
from multipledispatch import dispatch
from DataStructure.DataResult.InstructionResult import InstructionResult
from DataStructure.Operator import Operator, OperatorCode
from DataStructure.DataResult.ConstantResult import ConstantResult
from DataStructure.DataResult.RegisterResult import RegisterResult
from DataStructure.Manager.VariableManager import VariableManager
from DataStructure.Manager.PhiManager import PhiManager


# TODO: update cfg with while block
class CFG:
    head: Block = None
    tail: Block = None
    blocks: list = None
    mVariableManager: VariableManager = None
    done: bool = False
    iGraph: dict = None
    returnIds: dict = None
    block_counter: int = -1

    def __init__(self, block_counter):
        # TODO: should the block_counter and base_block_counter increment by 1?
        self.block_counter = block_counter + 1
        self.base_block_counter = block_counter + 1
        self.head = Block(block_counter)
        self.blocks = []
        self.mVariableManager = VariableManager()
        self.returnIds = {}
        self.done = False
        self.blocks.append(self.head)
        self.iGraph = {}

        # While block. NOT IMPLEMENTED until WhileBlock is implemented.
        self.dom_list = []
        self.parent_stack = []
        self.block_in_while = {}
        self.loopblocks_in_while = {}

        # If block.
        self.dom_list_if = []
        self.while_in_if = {}
        self.block_in_if = {}

        # join block
        self.join_parent = {}
        self.live_range = {}
        self.adjacent = {}

    def initializeBlock(self):
        self.block_counter += 1
        # initialize block based on the block_counter which is the block id.
        block = Block(self.block_counter)
        self.blocks.append(block)
        return block

    def initializeConstantBlock(self):
        block = ConstantBlock(0)
        self.blocks.insert(0, block)
        return block

    def initializeIfBlock(self):
        self.block_counter += 1
        block = IfBlock(self.block_counter)
        self.blocks.append(block)
        return block

    def initializeJoinBlock(self):
        self.block_counter += 1
        block = JoinBlock(self.block_counter)
        self.blocks.append(block)
        return block

    def initializeWhileBlock(self):
        self.block_counter += 1
        block = WhileBlock(self.block_counter)
        self.blocks.append(block)
        return block

    def getAllBlocks(self):
        return self.blocks

    def getInstruction(self, id):
        block_Instruction = None
        for b in self.blocks:
            block_Instruction = b.getInstruction(id)
            if block_Instruction:
                return block_Instruction
        return block_Instruction

    def find_instr_from_iid(self, iid):
        # iid is the parameter for extracting instruction based on instruction id
        for b in self.blocks:
            for i in b.instructions:
                if i.id == iid:
                    return i

    def CP_replace(self, version: int, CP_id: int) -> None:
        # version is the PC that redundant move
        # CP_id is the target PC
        for b in self.blocks:
            block: Block = b
            for inst in block.instructions:
                if inst.id <= version:
                    continue
                else:
                    if isinstance(inst.operandx, VariableResult):
                        if inst.operandx.variable.version == version:
                            #print("Warning the variable result is changed to instruction result")
                            inst.operandx = InstructionResult(CP_id)
                    elif isinstance(inst.operandx, InstructionResult):
                        if inst.operandx.iid == version:
                            inst.operandx = InstructionResult(CP_id)

                    if isinstance(inst.operandy, VariableResult):
                        if inst.operandy.variable.version == version:

                            #print("Warning the variable result is changed to instruction result")
                            inst.operandy = InstructionResult(CP_id)
                    elif isinstance(inst.operandy, InstructionResult):
                        if inst.operandy.iid == version:
                            inst.operandy = InstructionResult(CP_id)


    def CP_replace_constant(self, version: int, constant: int) -> None:
        # version is the PC that redundant move
        # CP_id is the target PC
        for b in self.blocks:
            block: Block = b
            for inst in block.instructions:
                if inst.id < version:
                    continue
                else:
                    if isinstance(inst.operandx, VariableResult):
                        if inst.operandx.variable.version == version:
                            #print("Warning the variable result is changed to instruction result")
                            inst.operandx = ConstantResult(constant)
                    elif isinstance(inst.operandx, InstructionResult):
                        if inst.operandx.iid == version:
                            inst.operandx = ConstantResult(constant)

                    if isinstance(inst.operandy, VariableResult):
                        if inst.operandy.variable.version == version:
                            #print("Warning the variable result is changed to instruction result")
                            inst.operandy = ConstantResult(constant)
                    elif isinstance(inst.operandy, InstructionResult):
                        if inst.operandy.iid == version:
                            inst.operandy = ConstantResult(constant)

    def cse_move_constant(self, inst: Instruction, block: Block) -> bool:
        if inst.opcode != OperatorCode.move:
            #print("********Something wrong*********")
            return False
        for x in block.instructions:
            inst_temp: Instruction = x
            if inst_temp.id >= inst.id:
                continue
            if inst_temp.opcode != OperatorCode.move:
                continue
            else:
                if not isinstance(inst_temp.operandx, ConstantResult):
                    continue
                else:
                    if inst.operandx.constant != inst_temp.operandx.constant:
                        continue
                    else:
                        inst.deletemode = DeleteMode.COPY_PROP
                        inst.res_CSE = InstructionResult(inst_temp.id)
                        return True
        if block.id == self.base_block_counter:
            return False
        return self.cse_move_constant(inst, block.parent)

    def move_replace(self) -> None:
        for b in self.blocks:
            block: Block = b
            for i in block.instructions:
                inst: Instruction = i
                if inst.opcode != OperatorCode.move:
                    print(inst.toString(True))
                    continue
                else:
                    print(inst.toString(True))
                    if isinstance(inst.operandy, VariableResult):
                        # passing value to formal variable
                        if inst.operandy.variable.version == -2:
                            continue
                    if isinstance(inst.operandx, VariableResult):
                        if inst.operandx.variable.version == -2:
                            continue

                    if isinstance(inst.operandx, InstructionResult):
                        inst.deletemode = DeleteMode.COPY_PROP
                        self.CP_replace(inst.id, inst.operandx.iid)
                    elif isinstance(inst.operandx, VariableResult):
                        inst.deletemode = DeleteMode.COPY_PROP
                        self.CP_replace(inst.id, inst.operandx.variable.version)
                    elif isinstance(inst.operandx, ConstantResult):
                        mask: bool = self.cse_move_constant(inst, block)
                        self.CP_replace_constant(inst.id, inst.operandx.iid)
                        inst.deletemode = DeleteMode.COPY_PROP
                    else:
                        if inst.operandx == None:
                            print("Edge Case Happened None")
                        else:
                            print(inst.operandx)
                            print("Weird stuff")


    def dup_variable_removal(self):
        for b in self.blocks:
            if isinstance(b, ConstantBlock):
                continue
            block = b
            for i in block.instructions:
                instruction = i
                if isinstance(instruction.operandx, VariableResult):
                    if instruction.operandx.variable.version > 0:
                        if self.find_instr_from_iid(instruction.operandx.variable.version).opcode == OperatorCode.phi:
                            instruction.operandx = InstructionResult(instruction.operandx.variable.version)
                if isinstance(instruction.operandy, VariableResult):
                    if instruction.operandy.variable.version > 0:
                        if self.find_instr_from_iid(instruction.operandy.variable.version).opcode == OperatorCode.phi:
                            instruction.operandy = InstructionResult(instruction.operandy.variable.version)

    def cse_optimization(self) -> None:
        for b in self.blocks:
            if isinstance(b, ConstantBlock):
                continue
            #print(f"optimize CSE Debug -> Current Block id is {b.id}")
            block: Block = b
            if len(block.instructions) == 0:
                continue
            for id in range(len(block.instructions)):
                inst: Instruction = block.instructions[id]
                if isinstance(inst.operandx, RegisterResult):
                    if inst.operandx.register == 31:
                        continue
                if isinstance(inst.operandy, RegisterResult):
                    if inst.operandy.register == 31:
                        continue
                # begin set all instruction as not deleted

                inst.deletemode = DeleteMode._NOT_DEL
                inst_target_X: Instruction = None
                inst_target_Y: Instruction = None
                mark_X: bool = False
                mark_Y: bool = False

                if inst.opcode == OperatorCode.move:
                    mark_Y = True
                    if isinstance(inst.operandx, InstructionResult):
                        inst_target_X = self.find_instr_from_iid(inst.operandx.iid)
                        if inst_target_X.deletemode != DeleteMode._NOT_DEL:
                            inst.operandx = inst_target_X.res_CSE
                            mark_X = True
                    elif isinstance(inst.operandx, VariableResult):
                        mark_X = False
                        if inst.operandx.variable.version == Constants.FORMAL_PARAMETER_VERSION:
                            print("skip")
                        else:
                            print("Warning: operandx is variable result.")
                elif inst.opcode == OperatorCode.phi:
                    IR_x:Instruction = None
                    IR_y:Instruction = None
                    mark_X = True
                    mark_Y = True
                    IR_x = self.find_instr_from_iid(inst.operandx.variable.version)
                    IR_y = self.find_instr_from_iid(inst.operandy.variable.version)
                    if isinstance(inst.operandx,VariableResult):
                        IR_x:Instruction = self.find_instr_from_iid(inst.operandx.variable.version)
                    if isinstance(inst.operandy, VariableResult):
                        IR_y:Instruction = self.find_instr_from_iid(inst.operandy.variable.version)
                    if IR_x != None:
                        if IR_x.deletemode != DeleteMode._NOT_DEL:
                            temp:VariableResult = VariableResult()
                            temp.variable = Variable(inst.operandx.variable.name,inst.operandx.variable.address,IR_x.res_CSE.iid)
                            inst.operandx = temp
                    if IR_y != None:
                        if IR_y.deletemode != DeleteMode._NOT_DEL:
                            temp:VariableResult = VariableResult()
                            temp.variable = Variable(inst.operandy.variable.name,inst.operandy.variable.address,IR_y.res_CSE.iid)
                            inst.operandy = temp

                elif inst.opcode == OperatorCode.bra:
                    inst.deletemode = DeleteMode._NOT_DEL
                    continue
                elif inst.opcode == OperatorCode.load:
                    inst_adda: Instruction = block.instructions[id - 1]
                    if inst_adda.deletemode == DeleteMode._NOT_DEL:
                        inst.deletemode = DeleteMode._NOT_DEL
                        continue
                    # ------------------
                elif inst.opcode == OperatorCode.store:
                    inst_adda: Instruction = block.instructions[id - 1]
                    inst_adda.deletemode = DeleteMode._NOT_DEL
                    inst.deletemode = DeleteMode._NOT_DEL
                    continue
                    # ------------------
                elif (inst.opcode == OperatorCode.read) or (inst.opcode == OperatorCode.writeNL):
                     continue
                #elif (inst.opcode == OperatorCode.read):
                #    continue
                elif inst.opcode == OperatorCode.write:
                    if isinstance(inst.operandx,InstructionResult):
                        inst_t:Instruction = self.find_instr_from_iid(inst.operandx.iid)
                        if inst_t.deletemode != DeleteMode._NOT_DEL:
                            inst.operandx = InstructionResult(inst_t.res_CSE.iid)
                    elif isinstance(inst.operandx,VariableResult):
                        inst_t:Instruction = self.find_instr_from_iid(inst.operandx.variable.version)
                        if inst_t.deletemode != DeleteMode._NOT_DEL:
                            inst.operandx = InstructionResult(inst_t.res_CSE.iid)
                    continue
                else:
                    if isinstance(inst.operandx, InstructionResult):
                        inst_target_X = self.find_instr_from_iid(inst.operandx.iid)
                        if inst_target_X.opcode != OperatorCode.move:
                            if inst_target_X.deletemode == DeleteMode._NOT_DEL:
                                # mark_X = True
                                mark_X = False
                            else:
                                inst.operandx = inst_target_X.res_CSE
                    if isinstance(inst.operandy, InstructionResult):
                        inst_target_Y = self.find_instr_from_iid(inst.operandy.iid)
                        if inst_target_Y.opcode != OperatorCode.move:
                            if inst_target_Y.deletemode == DeleteMode._NOT_DEL:
                                # mark_Y = True
                                mark_Y = False
                            else:
                                inst.operandy = inst_target_Y.res_CSE

                if (mark_X == False) and (mark_Y == False):
                    for i in reversed(range(id)):
                        inst_temp: Instruction = block.instructions[i]
                        if isinstance(inst_temp.operandx, RegisterResult):
                            if inst_temp.operandx.register == 31:
                                continue
                        if isinstance(inst_temp.operandy, RegisterResult):
                            if inst_temp.operandy.register == 31:
                                continue
                        # delete CSE
                        if (inst_temp.opcode == OperatorCode.move) or (inst_temp.opcode == OperatorCode.phi):
                            temp: int = -1
                            if inst_temp.opcode == OperatorCode.move:
                                temp = inst_temp.operandy.variable.address
                            elif inst_temp.opcode == OperatorCode.phi:
                                temp = inst_temp.variable.address

                            if isinstance(inst.operandx, InstructionResult):
                                temp: Instruction = self.find_instr_from_iid(inst.operandx.iid)
                                if (temp.opcode == OperatorCode.move) or (temp.opcode == OperatorCode.phi):
                                    if temp.operandy.variable.address == temp:
                                        mark_X = True
                                        mark_Y = True
                                        inst.deletemode = DeleteMode._NOT_DEL
                                        break
                            elif isinstance(inst.operandx, VariableResult):
                                if inst.operandx.variable.address == temp:
                                    mark_X = True
                                    mark_Y = True
                                    inst.deletemode = DeleteMode._NOT_DEL
                                    break
                            elif isinstance(inst.operandy, InstructionResult):
                                temp: Instruction = self.find_instr_from_iid(inst.operandy.iid)
                                if (temp.opcode == OperatorCode.move) or (temp.opcode == OperatorCode.phi):
                                    if temp.operandy.variable.address == temp:
                                        mark_X = True
                                        mark_Y = True
                                        inst.deletemode = DeleteMode._NOT_DEL
                                        break
                            elif isinstance(inst.operandy, VariableResult):
                                if inst.operandy.variable.address == temp:
                                    if inst.operandy.variable.address == temp:
                                        mark_X = True
                                        mark_Y = True
                                        inst.deletemode = DeleteMode._NOT_DEL
                                        break

                        if inst.opcode == OperatorCode.move:
                            if inst_temp.opcode != OperatorCode.move:
                                continue
                            else:
                                if inst_temp.operandy.variable.address != inst.operandy.variable.address:
                                    continue
                                else:
                                    temp_id: int = -1
                                    if isinstance(inst_temp.operandx, InstructionResult):
                                        temp_id = inst_temp.operandx.iid
                                    elif isinstance(inst_temp.operandx, VariableResult):
                                        temp_id = inst_temp.operandx.variable.version
                                    elif isinstance(inst_temp.operandx, ConstantResult):
                                        # temp_id = inst_temp.operandx.constant
                                        temp_id = inst_temp.operandx.iid

                                    target_id: int = -1
                                    if isinstance(inst.operandx, InstructionResult):
                                        target_id = inst.operandx.iid
                                    elif isinstance(inst.operandx, VariableResult):
                                        target_id = inst.operandx.variable.version
                                    elif isinstance(inst.operandx, ConstantResult):
                                        #target_id = inst.operandx.constant
                                        target_id = inst.operandx.iid

                                    if temp_id == target_id:
                                        mark_X = True
                                        mark_Y = True
                                        if inst_temp.deletemode == DeleteMode.CSE:
                                            inst.res_CSE = inst_temp.res_CSE
                                        else:
                                            inst.res_CSE = InstructionResult(inst_temp.id)
                                        inst.deletemode = DeleteMode.CSE
                                        break
                                    else:
                                        continue
                        elif inst.opcode == OperatorCode.load:
                            if inst_temp.opcode == OperatorCode.store:
                                adda_temp_PC: int = i - 1
                                if block.instructions[adda_temp_PC].opcode != OperatorCode.adda:
                                    print("adda instruction is missing")
                                else:
                                    if block.instructions[adda_temp_PC].operandy.constant == block.instructions[
                                        id - 1].operandy.constant:
                                        # kill current load
                                        inst.deletemode = DeleteMode._NOT_DEL
                                        block.instructions[id - 1].deletemode = DeleteMode._NOT_DEL
                                        mark_X = True
                                        mark_Y = True
                                        break
                                    else:
                                        continue
                            elif (inst_temp.opcode == OperatorCode.load) and (
                                    inst_temp.deletemode == DeleteMode._NOT_DEL):
                                adda_temp_PC:int = i - 1
                                if block.instructions[adda_temp_PC].opcode != OperatorCode.adda:
                                    print("adda instruction is missing")
                                else:
                                    if isinstance(inst.operandy, InstructionResult) and isinstance(
                                            inst_temp.operandy, InstructionResult):
                                        if block.instructions[id - 1].res_CSE.iid == inst_temp.operandy.iid:
                                            inst.deletemode = DeleteMode.CSE
                                            inst.res_CSE = InstructionResult(inst_temp.id)
                                            mark_X = True
                                            mark_Y = True
                                            break
                                        else:
                                            continue
                                    else:
                                        print("wrong instruction result")
                        else:
                            if inst_temp.opcode != inst.opcode:
                                continue
                            else:
                                temp_x: int = -1
                                temp_y: int = -1
                                target_x: int = -1
                                target_y: int = -1

                                if isinstance(inst_temp.operandx, InstructionResult):
                                    temp_x = inst_temp.operandx.iid
                                elif isinstance(inst_temp.operandx, VariableResult):
                                    temp_x = inst_temp.operandx.variable.address
                                elif isinstance(inst_temp.operandx, ConstantResult):
                                    #temp_x = inst_temp.operandx.constant
                                    temp_x = inst_temp.operandx.iid

                                if isinstance(inst_temp.operandy, InstructionResult):
                                    temp_y = inst_temp.operandy.iid
                                elif isinstance(inst_temp.operandy, VariableResult):
                                    temp_y = inst_temp.operandy.variable.address
                                elif isinstance(inst_temp.operandy, ConstantResult):
                                    #temp_y = inst_temp.operandy.constant
                                    temp_x = inst_temp.operandx.iid

                                if isinstance(inst.operandx, InstructionResult):
                                    target_x = inst.operandx.iid
                                elif isinstance(inst.operandx, VariableResult):
                                    target_x = inst.operandx.variable.address
                                elif isinstance(inst.operandx, ConstantResult):
                                    #target_x = inst.operandx.constant
                                    target_x = inst.operandx.iid

                                if isinstance(inst.operandy, InstructionResult):
                                    target_y = inst.operandy.iid
                                elif isinstance(inst.operandy, VariableResult):
                                    target_y = inst.operandy.variable.address
                                elif isinstance(inst.operandy, ConstantResult):
                                    #target_y = inst.operandy.constant
                                    target_y = inst.operandy.iid

                                if (inst.opcode != OperatorCode.mul) and (inst.opcode != OperatorCode.add):
                                    if (temp_x == target_x) and (temp_y == target_y):
                                        if inst_temp.deletemode == DeleteMode.CSE:
                                            inst.res_CSE = inst_temp.res_CSE
                                        else:
                                            inst.res_CSE = InstructionResult(inst_temp.id)
                                        inst.deletemode = DeleteMode.CSE
                                        mark_X = True
                                        mark_Y = True
                                        break
                                else:
                                    if (temp_x == target_x) and (temp_y == target_y):
                                        if inst_temp.deletemode == DeleteMode.CSE:
                                            inst.res_CSE = inst_temp.res_CSE
                                        else:
                                            inst.res_CSE = InstructionResult(inst_temp.id)
                                        inst.deletemode = DeleteMode.CSE
                                        mark_X = True
                                        mark_Y = True
                                        break
                                    elif (temp_x == target_y) and (temp_y == target_x):
                                        if inst_temp.deletemode == DeleteMode.CSE:
                                            inst.res_CSE = inst_temp.res_CSE
                                        else:
                                            inst.res_CSE = InstructionResult(inst_temp.id)
                                        inst.deletemode = DeleteMode.CSE
                                        mark_X = True
                                        mark_Y = True
                                        break
                                    else:
                                        continue
                if (mark_X == True) and (mark_Y == True) or (block.id == self.base_block_counter):
                    continue
                else:
                    # need search parent block

                    if inst.opcode != OperatorCode.load:
                        if block.parent.id != 0:
                            inst = self.search_cse(block.parent.id, inst)
                    else:
                        # For load kill we need to consider join and while
                        base: int = block.instructions[id - 1].operandy.constant
                        if isinstance(block, JoinBlock):
                            left_id: int = self.join_parent[block.id][0]
                            left_block: Block = self.blocks[left_id - self.base_block_counter]
                            right_id: int = self.join_parent[block.id][1]
                            right_block: Block = self.blocks[right_id - self.base_block_counter]
                            if (self.load_kill(left_block, base, False) == False) and (
                                    self.load_kill(right_block, base, False) == False):
                                inst = self.load_store_check(block.parent, inst)
                                continue
                            else:
                                inst.deletemode = DeleteMode._NOT_DEL
                                block.instructions[id - 1].deletemode = DeleteMode._NOT_DEL
                                continue
                        elif isinstance(block, WhileBlock):
                            # need to check the block insider while is complete or not
                            mask: bool = False
                            for b in self.block_in_while[block.id]:
                                if self.load_kill(self.blocks[b - self.base_block_counter], base, True):
                                    mask = True
                                    break
                            if mask == True:
                                inst.deletemode = DeleteMode._NOT_DEL
                                block.instructions[id - 1].deletemode = DeleteMode._NOT_DEL
                                continue
                            else:
                                inst = self.load_store_check(block.parent, inst)
                                continue
                        else:
                            inst = self.load_store_check(block.parent, inst)
                            continue


    def search_cse(self, id, instr):
        # print(f"search CSE debug - block id {id} and base_block_counter {self.base_block_counter}")
        #breakpoint()

        block = self.blocks[id]
        # print(f"block id update {block.id}")
        mark_x = False
        mark_y = False

        if len(block.instructions) == 0:
            # print("empty block")
            return self.search_cse(block.parent.id, instr)

        for idx in reversed(range(len(block.instructions))):
            instr_temp = block.instructions[idx]
            if instr_temp.opcode == OperatorCode.move or instr_temp.opcode == OperatorCode.phi:
                temp = -1
                if instr_temp.opcode == OperatorCode.move:
                    temp = instr_temp.operandy.variable.address
                elif instr_temp.opcode == OperatorCode.phi:
                    temp = instr_temp.operandy.variable.address

                if isinstance(instr.operandx, InstructionResult):
                    # instruction x
                    temp = self.find_instr_from_iid(instr.operandx.iid)
                    if temp.opcode == OperatorCode.move or temp.opcode == OperatorCode.phi:
                        if temp.operandy.variable.address == temp:
                            mark_x = True
                            mark_y = True
                            instr.deletemode = DeleteMode._NOT_DEL
                            break
                elif isinstance(instr.operandx, VariableResult):
                    if instr.operandx.variable.address == temp:
                        mark_x = True
                        mark_y = True
                        instr.deletemode = DeleteMode._NOT_DEL
                        break
                elif isinstance(instr.operandy, InstructionResult):
                    # instruction y
                    temp = self.find_instr_from_iid(instr.operandy.iid)
                    if temp.opcode == OperatorCode.move or temp.opcode == OperatorCode.phi:
                        if temp.operandy.variable.address == temp:
                            mark_x = True
                            mark_y = True
                            instr.deletemode = DeleteMode._NOT_DEL
                            break
                elif isinstance(instr.operandy, VariableResult):
                    if instr.operandy.variable.address == temp:
                        mark_x = True
                        mark_y = True
                        instr.deletemode = DeleteMode._NOT_DEL
                        break

            if instr.opcode == OperatorCode.move:
                if instr_temp.opcode != OperatorCode.move:
                    continue
                else:
                    if instr_temp.operandy.variable.address != instr.operandy.variable.address:
                        continue
                    else:
                        temp_id = -1
                        if isinstance(instr_temp.operandx, InstructionResult):
                            temp_id = instr_temp.operandx.iid
                        elif isinstance(instr_temp.operandx, VariableResult):
                            temp_id = instr_temp.operandx.variable.version
                        elif isinstance(instr_temp.operandx, ConstantResult):
                            #temp_id = instr_temp.operandx.constant
                            temp_id = instr_temp.operandx.iid

                        target_id = -1
                        if isinstance(instr.operandx, InstructionResult):
                            target_id = instr.operandx.iid
                        elif isinstance(instr.operandx, VariableResult):
                            target_id = instr.operandx.variable.version
                        elif isinstance(instr.operandx, ConstantResult):
                            #target_id = instr.operandx.constant
                            target_id = instr.operandx.iid

                        if temp_id == target_id:
                            mark_x = True
                            mark_y = True
                            if instr_temp.deletemode == DeleteMode.CSE:
                                instr.res_CSE = instr_temp.CSE
                            else:
                                instr.res_CSE = InstructionResult(instr_temp.id)
                            instr.deletemode = DeleteMode.CSE
                            break
                        else:
                            continue
            else:
                if instr_temp.opcode != instr.opcode:
                    continue
                else:
                    temp_x = -1
                    temp_y = -1
                    target_x = -1
                    target_y = -1
                    if isinstance(instr_temp.operandx, InstructionResult):
                        temp_x = instr_temp.operandx.iid
                    elif isinstance(instr_temp.operandx, VariableResult):
                        temp_x = instr_temp.operandx.variable.address
                    elif isinstance(instr_temp.operandx, ConstantResult):
                        #temp_x = instr_temp.operandx.constant
                        temp_x = instr_temp.operandx.iid

                    if isinstance(instr_temp.operandy, InstructionResult):
                        temp_y = instr_temp.operandy.iid
                    elif isinstance(instr_temp.operandy, VariableResult):
                        temp_y = instr_temp.operandy.variable.address
                    elif isinstance(instr_temp.operandy, ConstantResult):
                        #temp_y = instr_temp.operandy.constant
                        temp_y = instr_temp.operandy.iid
                    if isinstance(instr.operandx, InstructionResult):
                        target_x = instr.operandx.iid
                    elif isinstance(instr.operandx, VariableResult):
                        target_x = instr.operandx.variable.address
                    elif isinstance(instr.operandx, ConstantResult):
                        #target_x = instr.operandx.constant
                        target_x = instr.operandx.iid
                    if isinstance(instr.operandy, InstructionResult):
                        target_y = instr.operandy.iid
                    elif isinstance(instr.operandy, VariableResult):
                        target_y = instr.operandy.variable.address
                    elif isinstance(instr.operandy, ConstantResult):
                        #target_y = instr.operandy.constant
                        target_y = instr.operandy.iid
                    if instr.opcode != OperatorCode.mul and instr.opcode != OperatorCode.add:
                        if temp_x == target_x and temp_y == target_y:
                            if instr_temp.deletemode == DeleteMode.CSE:
                                instr.res_CSE = instr_temp.res_CSE
                            else:
                                instr.res_CSE = InstructionResult(instr_temp.id)
                            instr.deletemode = DeleteMode.CSE
                            mark_x = True
                            mark_y = True
                            break
                    else:
                        if temp_x == target_x and temp_y == target_y:
                            if instr_temp.deletemode == DeleteMode.CSE:
                                instr.res_CSE = instr_temp.res_CSE
                            else:
                                instr.res_CSE = InstructionResult(instr_temp.id)
                            instr.deletemode = DeleteMode.CSE
                            mark_x = True
                            mark_y = True
                            break
                        elif temp_x == target_y and temp_y == target_x:
                            if instr_temp.deletemode == DeleteMode.CSE:
                                instr.res_CSE = instr_temp.res_CSE
                            else:
                                instr.res_CSE = InstructionResult(instr_temp.id)
                            instr.deletemode = DeleteMode.CSE
                            mark_x = True
                            mark_y = True
                            break
                        else:
                            continue
        if mark_x and mark_y:
            return instr
        elif block.id != self.base_block_counter:
            return self.search_cse(block.parent.id, instr)

    def load_store_check(self, block: Block, inst: Instruction) -> None:
        # For load kill we need to consider join and while
        inst_adda: Instruction = self.find_instr_from_iid(inst.operandy.iid)
        for i in reversed(range(len(block.instructions))):
            inst_temp: Instruction = block.instructions[i]
            if inst_temp.opcode == OperatorCode.store:
                inst_adda: Instruction = self.find_instr_from_iid(inst.operandy.iid)
                if block.instructions[i - 1].operandy.constant == inst_adda.operandy.constant:
                    inst.deletemode = DeleteMode._NOT_DEL
                    inst_adda.deletemode = DeleteMode._NOT_DEL
                    return inst
                else:
                    continue
            elif (inst_temp.opcode == OperatorCode.load) and (inst_temp.deletemode == DeleteMode._NOT_DEL):
                # if inst.id == 22:
                #     print(inst.id)
                #     print(inst_temp.id)
                if inst_adda.res_CSE.iid == inst_temp.operandy.iid:
                    inst.deletemode = DeleteMode.CSE
                    inst.res_CSE = InstructionResult(inst_temp.id)
                    return inst
            else:
                continue

        # if this is first block stop searching
        if block.id == 1:
            return inst

        base: int = inst_adda.operandy.constant
        if isinstance(block, JoinBlock):
            left_id: int = self.join_parent[block.id][0]
            left_block: Block = self.blocks[left_id]
            right_id: int = self.join_parent[block.id][0]
            right_block: Block = self.blocks[right_id]
            if (self.load_kill(left_block, base, False) == False) and (
                    self.load_kill(right_block, base, False) == False):
                return self.load_store_check(block.parent, inst)
            else:
                inst.deletemode = DeleteMode._NOT_DEL
                # TODO DO: Should the self.id -1 at here?
                # What is the id here?
                block.instructions[id - 1].deletemode = DeleteMode._NOT_DEL
                return inst
        elif isinstance(block, WhileBlock):
            # need to check the block insider while is complete or not
            mask: bool = False
            for b in self.block_in_while[block.id]:
                if self.load_kill(self.blocks[b - self.base_block_counter], base, True):
                    mask = True
                    break
            if mask == True:
                inst.deletemode = DeleteMode._NOT_DEL
                if inst_adda.opcode == OperatorCode.adda:
                    inst_adda.deletemode = DeleteMode._NOT_DEL
                else:
                    print("wrong adda instruction")
                return inst
            else:
                return self.load_store_check(block.parent, inst)
        else:
            return self.load_store_check(block.parent, inst)

        return inst

    def load_kill(self, block, base, stop):
        if len(block.instructions) == 0:
            return False

        marker = False
        for i in range(len(block.instructions)):
            instr_temp = block.instructions[i]
            if instr_temp.opcode != OperatorCode.store:
                continue
            else:
                # TODO: should we check the base equal to the last instruction in the block?
                if base != block.instructions[i - 1].operandy.constant:
                    continue
                else:
                    marker = True
                    break
        if marker == True:
            return True
        else:
            if stop == True:
                return False
            else:
                if isinstance(block.parent, IfBlock):
                    return False
                else:
                    return self.load_kill(block.parent, base, False)
