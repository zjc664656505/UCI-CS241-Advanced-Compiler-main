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
# TODO: while block needs to be implemented later on
# from DataStructure.Blocks.WhileBlock import WhileBlock
from multipledispatch import dispatch
from DataStructure.DataResult.InstructionResult import InstructionResult
from DataStructure.Operator import Operator, OperatorCode
from DataStructure.DataResult.ConstantResult import ConstantResult
from DataStructure.DataResult.RegisterResult import RegisterResult
from DataStructure.Manager.VariableManager import VariableManager
from DataStructure.Manager.PhiManager import PhiManager


class CFG:
    head: Block = None
    tail: Block = None
    blocks: list = None
    mVariableManager: VariableManager = None
    done: bool = False
    iGraph: dict = None
    returnIds: dict = None
    block_counter: int = 0

    def __init__(self, block_counter):
        # TODO: should the block_counter and base_block_counter increment by 1?
        self.block_counter = block_counter
        self.base_block_counter = block_counter
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

    def initializeIfBlock(self):
        self.block_counter += 1
        block = Block(self.block_counter)
        self.blocks.append(block)
        return block

    def initializeThenBlock(self):
        self.block_counter += 1
        block = Block(self.block_counter)
        self.blocks.append(block)
        return block

    def initializeJoinBlock(self):
        self.block_counter += 1
        block = Block(self.block_counter)
        self.blocks.append(block)
        return block

    def initializeWhileBlock(self):
        # TODO: Need to be implemented when While block is done
        pass

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

    def CP_replace(self, version, CP_id):
        for b in self.blocks:
            block = b
            for instr in block.instructions:
                if instr.id <= version:
                    continue
                else:
                    if isinstance(instr.operandx, VariableResult):
                        print('VarX -> Instr')
                        instr.operandx = InstructionResult(CP_id)
                    elif isinstance(instr.operandx, InstructionResult):
                        if instr.operandx.iid == version:
                            instr.operandx = InstructionResult(CP_id)
                    if isinstance(instr.operandy, VariableResult):
                        print("VarY -> Instr")
                        instr.operandy = InstructionResult(CP_id)
                    elif isinstance(instr.operandy, InstructionResult):
                        if instr.operandy.iid == version:
                            instr.operandy = InstructionResult(CP_id)

    def CP_replace_constant(self, version, constant):
        # version: Redundant instruction
        # constant: Copy Propogation ID
        for b in self.blocks:
            for instr in b.instructions:
                if instr.id < version:
                    continue
                else:
                    if isinstance(instr.operandx, VariableResult):
                        print("VarX -> Instr")
                        instr.operandx = ConstantResult(constant)
                    elif isinstance(instr.operandx, InstructionResult):
                        if instr.operandx.iid == version:
                            instr.operandx = ConstantResult(constant)
                    if isinstance(instr.operandy, VariableResult):
                        print("VarY -> Instr")
                        instr.operandy = ConstantResult(constant)
                    elif isinstance(instr.operandx, InstructionResult):
                        if instr.operandy.iid == version:
                            instr.operandy = ConstantResult(constant)

    def cse_move_constant(self, instr, block):
        if instr.opcode != OperatorCode.move:
            print("CSE RULE VIOLATED")
            return False
        else:
            for block_instr in block.instructions:
                instr_temp = block_instr
                if instr_temp.id >= instr.id:
                    continue
                if instr_temp.opcode != OperatorCode.move:
                    continue
                else:
                    if not isinstance(instr_temp.operandx, ConstantResult):
                        continue
                    else:
                        if instr.operandx.constant != instr_temp.operandx.constant:
                            continue
                        else:
                            instr.deletemode = DeleteMode.COPY_PROP
                            instr.res_CSE = InstructionResult(instr_temp.id)
        if block.id == self.base_block_counter:
            return False
        return self.cse_move_constant(instr, block.parent)

    def move_replace(self):
        for b in self.blocks:
            for i in b.instructions:
                instr = i
                if instr.opcode != OperatorCode.move:
                    continue
                else:
                    # for variables
                    if isinstance(instr.operandx, VariableResult):
                        if instr.operandx.variable.version == -2:
                            continue
                    if isinstance(instr.operandy, VariableResult):
                        if instr.operandy.variable.version == -2:
                            continue
                    if isinstance(instr.operandx, InstructionResult):
                        instr.deletemode = DeleteMode.COPY_PROP
                        self.CP_replace(instr.id, instr.operandx.iid)
                    elif isinstance(instr.operandx, VariableResult):
                        instr.deletemode = DeleteMode.COPY_PROP
                        self.CP_replace_constant(instr.id, instr.operandx.variable.version)
                    elif isinstance(instr.operandx, ConstantResult):
                        self.CP_replace(instr.id, instr.operandx.constant)
                        instr.deletemode = DeleteMode.COPY_PROP
                    else:
                        if instr.operandx is None:
                            print("WARNING: None Operand")
                        else:
                            print(f"WRONG OPERAND CANNOT BE PROCESSED: {instr.operandx}")


    def search_cse(self, id, instr):
        block = self.blocks[id-self.base_block_counter]
        mark_x = False
        mark_y = False

        if len(block.instructions) == 0:
            return self.search_cse(block.parent.id, instr)

        for idx in range(len(block.instructions)-1, -1, -1):
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
            # handle instruction in function call
            if instr.opcode == OperatorCode.move:
                if instr_temp.opcode != OperatorCode.move:
                    continue
                else:
                    if instr_temp.operandy.variable.address != instr.operandy.variable.address:
                        continue
                    else:
                        temp_id = -1
                        if isinstance(instr.operandx, InstructionResult):
                            temp_id = instr_temp.operandx.iid
                        elif isinstance(instr.operandx, VariableResult):
                            temp_id = instr_temp.operandx.variable.version
                        elif isinstance(instr.operandx, ConstantResult):
                            temp_id = instr_temp.operandx.constant
                        target_id = -1
                        if isinstance(instr.operandx, InstructionResult):
                            target_id = instr.operandx.iid
                        elif isinstance(instr.operandx, VariableResult):
                            target_id = instr.operandx.variable.version
                        elif isinstance(instr.operandx, ConstantResult):
                            target_id = instr.operandx.constant

                        if temp_id == target_id:
                            mark_x = True
                            mark_y = True
                            if instr_temp.deletemode == DeleteMode.CSE:
                                instr.res_CSE = instr_temp.res_CSE
                            else:
                                instr.res_CSE = InstructionResult(instr_temp.id)
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
                        temp_x = instr_temp.operandx.constant
                    if isinstance(instr_temp.operandy, InstructionResult):
                        temp_y = instr_temp.operandy.iid
                    elif isinstance(instr_temp.operandy, VariableResult):
                        temp_y = instr_temp.operandy.variable.address
                    elif isinstance(instr_temp.operandy, ConstantResult):
                        temp_y = instr_temp.operandy.constant

                    if isinstance(instr.operandx, InstructionResult):
                        target_x = instr.operandx.iid
                    elif isinstance(instr.operandx, VariableResult):
                        target_x = instr.operandx.variable.address
                    elif isinstance(instr.operandx, ConstantResult):
                        target_x = instr.operandx.constant

                    if isinstance(instr.operandy, InstructionResult):
                        target_y = instr.operandy.iid
                    elif isinstance(instr.operandy, VariableResult):
                        target_y = instr.operandy.variable.address
                    elif isinstance(instr.operandy, ConstantResult):
                        target_y = instr.operandy.constant

                    if instr.opcode != OperatorCode.mul and instr.opcode != OperatorCode.add:
                        if temp_x == target_x and temp_y == target_y:
                            if instr_temp.deletemode == DeleteMode.CSE:
                                instr.res_CSE = instr_temp.res_CSE
                            else:
                                instr.res_CSE = InstructionResult(instr_temp.id)
                            mark_x = True
                            mark_y = True
                            break
                    else:
                        if (temp_x == target_x and temp_y == target_y) or (temp_x == target_y and temp_y == target_x):
                            if instr_temp.deletemode == DeleteMode.CSE:
                                instr.res_CSE = instr_temp.res_CSE
                            else:
                                instr.res_CSE = InstructionResult(instr_temp.id)
                            instr.delemode = DeleteMode.CSE
                            mark_x = True
                            mark_y = True
                            break
                        elif temp_x == target_y and temp_y == target_x:
                            if instr_temp.deletemode == DeleteMode.CSE:
                                instr.res_CSE = instr_temp.res_CSE
                            else:
                                instr.res_CSE = InstructionResult(instr_temp.id)
                            instr.delemode = DeleteMode.CSE
                            mark_x = True
                            mark_y = True
                            break
                        else:
                            continue
        if mark_x and mark_y:
            return instr
        elif block.id != self.base_block_counter:
            return self.search_cse(block.parent.id, instr)




