# while block is not done
# build parser for existing blocks
# objective: test IR generator to the right output
# TODO: Need to work on Control Flow Graph first.

from parser.exception import illegalTokenException, illegalVariableException, incorrectSyntaxException
from IR.IRGenerator import IrGenerator
from DataStructure.Manager.VariableManager import VariableManager
from DataStructure.Manager.PhiManager import PhiManager
from DataStructure.DataResult.VariableResult import VariableResult, Variable
from DataStructure.DataResult.BranchResult import BranchResult
from DataStructure.DataResult.ConstantResult import ConstantResult
from DataStructure.DataResult.RegisterResult import RegisterResult
from DataStructure.Instruction import Instruction
from DataStructure.PhiInstruction import PhiInstruction
from DataStructure.Operator import *
from DataStructure.Array import *
from DataStructure.Token import Token, TokenType
from DataStructure.Variable import *
from util.Constants import Constants
from parser.parse_util import Tokenizer
from DataStructure.Blocks.JoinBlock import JoinBlock
from DataStructure.Blocks.WhileBlock import WhileBlock
from DataStructure.Instruction import DeleteMode
from copy import deepcopy
import sys
from DataStructure.CFG import CFG
from DataStructure.DataResult.InstructionResult import InstructionResult
from DataStructure.Operator import OperatorCode

"""
Debug Log:
1. Check the variable declaration. Making sure all variables declared at the beginning are pointing to the same address.
   (Variable version and address issue solved).
   2. Now, the second problem is to update the instruction id after variable declaration. For example, after var a is
      declared, the instruction id should be updated to the next instruction id. (Solved.)
   3. Third problem is to add the constant results into a block and update this block has the head of cfg.

2. Debug Copy Propagation and Array.
"""


class Parser:
    def __init__(self, fileName):
        self.filename = fileName
        self.tokenizer = Tokenizer(fileName)
        self.inputSym = None
        self.irGenerator = IrGenerator()
        self.killcounter = 0
        self.blockcounter = 0
        self.constantBlock = None
        self.constants = {}
        # TODO: Build cfg
        self.cfg = CFG(self.blockcounter)
        self.varManager = self.cfg.mVariableManager
        self.continuous_iid_track = []
        self.global_continuous_flag = False
        self.dimension_track = 0
        self.dimension_list = []
        r_constant_flag = False

    def next(self):
        self.inputSym: Token = self.tokenizer.getSym()

    def error(self, e):
        self.tokenizer.error(e)

    def designator(self, block):
        # print(self.irGenerator.pc)
        varResult = VariableResult()
        if self.inputSym.checkSameType(TokenType.ident):
            # get the input symbol value -> e.g. main, var1, var2
            token_value = self.inputSym.value

            # get the variable address from the variable manager
            variable = self.tokenizer.ident2Addr[self.inputSym.value]

            # check whether the variable is a variable
            if self.varManager.isVariable(variable):
                self.next()

                # check whether the variable is an Arrayed
                if self.varManager.isArray(variable):
                    if self.inputSym.checkSameType(TokenType.openbracketToken):
                        # define array in virtual memory
                        array_in_vm = self.varManager.arrays[variable]
                        # create the array variable
                        self.dimension_list = array_in_vm.dimensionList.copy()
                        self.dimension_list_len = len(array_in_vm.dimensionList.copy())
                        array_var = Array(array_in_vm.name, array_in_vm.address, array_in_vm.version,
                                          array_in_vm.dimensionList)
                        array_var.array_addr = array_in_vm.array_addr
                        index_List = []
                        while True:
                            # print(f"DEBUG: current inputSym {self.inputSym.value}")
                            self.next()
                            index = self.expression(block)
                            # print(f"Debug: index {index}")
                            index_List.append(index)

                            if self.inputSym.checkSameType(TokenType.closebracketToken):
                                self.next()
                            else:
                                self.error(incorrectSyntaxException("Expected close bracket for array element"))
                                return None
                            if not self.inputSym.checkSameType(TokenType.openbracketToken):
                                break
                        array_var.indexList = index_List
                        varResult.set(array_var)
                        varResult.setiid(array_var.version)
                    else:
                        self.error(incorrectSyntaxException("Expected open bracket"))
                        return None
                else:
                    v = Variable(token_value, variable, block.global_ssa[variable])
                    varResult.set(v)
                    varResult.setiid(v.version)
            else:
                self.error(illegalVariableException("Variable definition is illegal"))
                return None
        else:
            self.error(incorrectSyntaxException("Expected identifier"))
            return None
        # print(f"*******\nDEBUG: Variable name {v.name}, Variable Version {v.version}********\n")
        return varResult

    def factor(self, block, array_flag=False):
        result = None
        if self.inputSym.checkSameType(TokenType.ident):
            result = self.designator(block)
            if result is not None:
                var = result.variable
                if self.varManager.isVariable(var.address):
                    var.version = block.global_ssa[var.address]
                    if result.isAarry:
                        self.irGenerator.loadAarray(block, self.varManager, result, self.constants)
                        result = result.toInstruction()
                        result.set(self.irGenerator.getPC() - 1)
        elif self.inputSym.checkSameType(TokenType.number):
            # TODO: Change made to the factor function 2/28/2023
            op = self.inputSym
            result = ConstantResult()
            if self.dimension_list:
                new_iid = self.dimension_list_len

            if array_flag == False:
                if self.inputSym.value not in self.constants:
                    result.set(self.inputSym.value)
                    result.setiid(self.irGenerator.getPC() + 1)
                    print(f"\nConstantResult Debug {result.iid}: {self.inputSym.value}")
                    self.continuous_iid_track.append(result.iid)
                    print(self.continuous_iid_track)
                    if len(self.continuous_iid_track) > 1:
                        print("Continuous iid >1")
                        if result.iid == self.continuous_iid_track[-1]:
                            if self.dimension_list != []:
                                if len(self.dimension_list) > 1:
                                    self.dimension_track += 1
                                    self.dimension_list.pop()

                                new_iid = result.iid+self.dimension_track
                                result.setiid(new_iid)
                                self.irGenerator.compute(self.constantBlock, op, result, None, new_iid)
                                self.constants[self.inputSym.value] = new_iid
                                self.global_continuous_flag = True
                            else:
                                if result.iid == self.continuous_iid_track[-2]:
                                    print("dup iid!!!!")
                                    self.irGenerator.compute(self.constantBlock, op, result, None,
                                                             self.irGenerator.getPC() + 2)
                                    self.constants[self.inputSym.value] = self.irGenerator.getPC() + 2
                                    print(f"self.constants: {self.constants}")
                                else:
                                    self.irGenerator.compute(self.constantBlock, op, result, None, self.irGenerator.getPC() + 1)
                                    self.constants[self.inputSym.value] = self.irGenerator.getPC()+1

                    else:
                        self.irGenerator.compute(self.constantBlock, op, result, None, self.irGenerator.getPC() + 1)
                        self.constants[self.inputSym.value] = self.irGenerator.getPC() + 1

                else:
                    result.set(self.inputSym.value)
                    result.setiid(self.constants[self.inputSym.value])
                self.next()
            else:
                print("CREATE CONSTANT BLOCK FOR ARRAY")
                if self.inputSym.value not in self.constants:
                    print(self.irGenerator.pc)
                    print(new_iid)
                    result.set(self.inputSym.value)
                    result.setiid(self.irGenerator.getPC() + new_iid+1)
                    self.irGenerator.compute(self.constantBlock, op, result, None, self.irGenerator.getPC() + new_iid+1)
                    self.constants[self.inputSym.value] = self.irGenerator.getPC()+ new_iid +1
                else:
                    result.set(self.inputSym.value)
                    result.setiid(self.constants[self.inputSym.value])
                self.next()
        elif self.inputSym.checkSameType(TokenType.openparenToken):
            self.next()
            result = self.expression(block)
            if result is not None:
                if self.inputSym.checkSameType(TokenType.closeparenToken):
                    result = result.toInstruction()
                    self.next()
                else:
                    self.error(incorrectSyntaxException("Expected close parenthesis"))
        elif self.inputSym.checkSameType(TokenType.callToken):
            result = self.funcCall(block)

        if result is not None:
            return result.clone()

        return result

    def term(self, block, array_flag=False):
        r_constant_flag = False
        l_constant_flag = False
        factor_l = self.factor(block, array_flag)
        if factor_l is not None:
            while self.inputSym.checkTerm():
                op = self.inputSym
                self.next()
                factor_r = self.factor(block)
                if factor_r is not None:
                    if isinstance(factor_r, ConstantResult):
                        print("FACTOR R is Constant Result!!!")
                        r_constant_flag = True

                    if isinstance(factor_l, ConstantResult):
                        l_constant_flag = True

                    if isinstance(factor_l, VariableResult):
                        l_constant_flag = False
                        factor_l.setiid(factor_l.variable.version)
                    if factor_l.getiid() > 0 and (not isinstance(factor_l, RegisterResult)):
                        factor_l = factor_l.toInstruction()
                    if factor_r.getiid() > 0 and (not isinstance(factor_r, RegisterResult)):
                        factor_r = factor_r.toInstruction()

                    if isinstance(factor_l, ConstantResult) or isinstance(factor_r, ConstantResult):
                        self.irGenerator.compute(block, op, factor_l, factor_r)
                        self.irGenerator.pc += 2
                    else:
                        if l_constant_flag and r_constant_flag:
                            factor_r.setiid(self.constants[str(factor_r.constant)])
                            self.irGenerator.compute(block, op, factor_l, factor_r)
                            self.irGenerator.pc += 3
                        elif l_constant_flag == False and r_constant_flag == True:
                            factor_r.setiid(self.constants[str(factor_r.constant)])
                            self.irGenerator.compute(block, op, factor_l, factor_r)
                            self.irGenerator.pc += 2
                        else:
                            self.irGenerator.pc += 1
                            self.irGenerator.compute(block, op, factor_l, factor_r)
                            self.irGenerator.pc += 1
                    factor_l = factor_l.clone()
                    if isinstance(factor_l, ConstantResult) or isinstance(factor_l, VariableResult):
                        print(f"*******Is Term checked?********\n")
                        factor_l = factor_l.toInstruction()
                    if l_constant_flag and r_constant_flag:
                        factor_l.setiid(self.irGenerator.getPC()-3)
                    elif r_constant_flag:
                        factor_l.setiid(self.irGenerator.getPC()-2)
                    else:
                        factor_l.setiid(self.irGenerator.getPC() -1)

        return factor_l

    def expression(self, block, array_flag=False):
        term_l = self.term(block, array_flag)
        self.r_constant_flag= False
        self.l_constant_flag = False
        if term_l is not None:
            while self.inputSym.checkExpression():
                op = self.inputSym
                self.next()
                term_r = self.term(block)

                # print(f"term_l version {term_r.variable.version}; term_l version {term_l.variable.version}")
                if term_r is not None:
                    if isinstance(term_r, ConstantResult):
                        print("TERM R is Constant Result!!!")
                        self.r_constant_flag = True
                    if isinstance(term_l, ConstantResult):
                        self.l_constant_flag = True

                    if isinstance(term_l, VariableResult):
                        self.l_constant_flag = False
                        print(f"expression current pc when term l is variable result {term_l.variable.version}")
                        term_l.setiid(term_l.variable.version)

                    if term_l.getiid() > 0 and (not isinstance(term_l, RegisterResult)):
                        term_l = term_l.toInstruction()
                    if term_r.getiid() > 0 and (not isinstance(term_r, RegisterResult)):
                        term_r = term_r.toInstruction()
                    if isinstance(term_l, ConstantResult) or isinstance(term_r, ConstantResult):
                        self.irGenerator.compute(block, op, term_l, term_r)
                        self.irGenerator.pc += 2
                    else:
                        print(f"expression op value {op.value}")
                        if self.l_constant_flag and self.r_constant_flag:
                            print(self.constants)
                            term_l.setiid(self.constants[str(term_l.constant)])
                            term_r.setiid(self.constants[str(term_r.constant)])
                            print(f"{term_l.constant}: {term_l.iid}")
                            print(f"{term_r.constant}: {term_r.iid}")
                            print(f"\nPCCCCCCCCCCCCC --- expression pc org {self.irGenerator.pc}")
                            print(f"expression current pc {self.irGenerator.pc}")
                            self.irGenerator.compute(block, op, term_l, term_r)
                            self.irGenerator.pc += 3
                            print(f"expression pc after {self.irGenerator.pc}")
                        elif self.l_constant_flag == False and self.r_constant_flag == True:
                            print(f"\nPCCCCCCCCCCCCC --- expression pc org {self.irGenerator.pc}")
                            print(f"expression current pc {self.irGenerator.pc}")
                            print(f"term r iid {term_r.getiid()}")

                            term_r.setiid(self.constants[str(term_r.constant)])
                            self.irGenerator.compute(block, op, term_l, term_r)
                            print([i.toString(True) for i in block.instructions])
                            self.irGenerator.pc += 2
                        else:
                            print("No Constants in expression\n")
                            self.irGenerator.pc += 1
                            self.irGenerator.compute(block, op, term_l, term_r)
                            self.irGenerator.pc += 1

                    term_l = term_l.clone()
                    if (isinstance(term_l, ConstantResult) or isinstance(term_l, VariableResult)) and array_flag == False:
                        print(f"*******Is Expression checked?********\n")
                        term_l = term_l.toInstruction()

                    if self.l_constant_flag and self.r_constant_flag:
                        term_l.setiid(self.irGenerator.getPC()-3)
                    elif self.r_constant_flag:
                        term_l.setiid(self.irGenerator.getPC()-2)
                    else:
                        term_l.setiid(self.irGenerator.getPC() - 1)


        return term_l

    def relation(self, block):
        branch_res = BranchResult()
        expr_l = self.expression(block)
        expr_r_flag = self.r_constant_flag
        expr_l_flag = self.l_constant_flag
        print("\n*******RELATION")
        if expr_l is not None:
            while self.inputSym.checkRelation():
                op = self.inputSym
                self.next()
                #self.irGenerator.pc += 1
                expr_r = self.expression(block)
                # print(f"\nDEBUG: expr_l version {expr_l.iid}"
                #       f" expr_r version {expr_r.iid}\n")
                # print(op.value)
                if expr_r is not None:
                    if isinstance(expr_r, ConstantResult):
                        expr_r_flag = True
                        # print("Debug: ConstantResult in relation for expr_r")

                    if isinstance(expr_l, ConstantResult):
                        expr_l_flag = True
                    print(f"relation expr_l is Constant {expr_l_flag}, expr_r is constant {expr_r_flag}")

                    if expr_l_flag and expr_r_flag:
                        expr_l.setiid(self.constants[str(expr_l.constant)])
                        expr_r.setiid(self.constants[str(expr_r.constant)])
                        self.irGenerator.compute(block, op, expr_l, expr_r)
                        self.irGenerator.pc += 3
                        branch_res.condition = op
                        branch_res.fixuplocation = self.irGenerator.getPC()
                        # print(f"branch_res.fixuplocation {branch_res.fixuplocation}")
                        branch_res.iid = self.irGenerator.getPC() - 3

                    elif expr_l_flag == False and expr_r_flag == True:
                        expr_r.setiid(self.constants[str(expr_r.constant)])
                        self.irGenerator.compute(block, op, expr_l, expr_r)
                        self.irGenerator.pc += 2
                        branch_res.condition = op
                        branch_res.fixuplocation = self.irGenerator.getPC()
                        # print(f"branch_res.fixuplocation {branch_res.fixuplocation}")
                        branch_res.iid = self.irGenerator.getPC() - 2
                        # print(f"branch_res.fixuplocation {branch_res.fixuplocation}")

                    else:
                        self.irGenerator.compute(block, op, expr_l, expr_r)
                        self.irGenerator.pc += 1
                        branch_res.condition = op
                        branch_res.fixuplocation = self.irGenerator.getPC()
                        # print(f"branch_res.fixuplocation {branch_res.fixuplocation}")
                        branch_res.iid = self.irGenerator.getPC() - 1
                        # print(f"branch_res.fixuplocation {branch_res.fixuplocation}")
                    branch_res.targetBlock = block
        return branch_res.clone()

    def assignment(self, block, kill: list):
        print("****\n Assignment\n")
        varManager = self.varManager
        constant_res_flag = False
        if self.inputSym.checkSameType(TokenType.letToken):
            self.next()
            designator_res = self.designator(block)
            if designator_res is not None:
                if self.inputSym.checkSameType(TokenType.becomesToken):
                    op = self.inputSym
                    self.next()
                    # expr_res = self.expression(block)
                    # # DEBUG CHECK TYPE OF OBJECT FOR expr_res
                    # # print(expr_res)
                    # if expr_res is not None:
                    #     if isinstance(expr_res, VariableResult):
                    #         flag = False
                    #     else:
                    #         flag = True
                    var = designator_res.variable
                    if varManager.isVariable(var):
                        if designator_res.isAarry:
                            expr_res = self.expression(block, array_flag=True)
                            if expr_res.getiid() > 0:
                                expr_res = expr_res.toInstruction()
                            print(f"\nEEEEEEE***** expr_res is ConstantResult with iid {expr_res.constant} Desnator {designator_res.iid}\n")

                            # define functinoal constant reuse
                            self.irGenerator.pc += 1
                            self.irGenerator.storeArray(block, varManager, designator_res, expr_res, self.constants)
                            self.irGenerator.pc += 1

                            newKill = Instruction(0)
                            # TODO: Should the killcounter be incremented at here? 2/15/2023
                            self.killcounter += 1
                            newKill.setExternel(self.killcounter, OperatorCode.store, designator_res, None)
                            kill.append(newKill)
                            designator_res = designator_res.toInstruction()
                            designator_res.set(self.irGenerator.getPC()-1)
                        else:
                            expr_res = self.expression(block)
                            if expr_res is not None:
                                if isinstance(expr_res, VariableResult):
                                    flag = False
                                else:
                                    flag = True

                            if isinstance(expr_res, ConstantResult):
                                print("\nexpr_res is Constant in assignment!!!")
                                print(expr_res.iid)
                                constant_res_flag = True

                            if expr_res.getiid() > 0:
                                expr_res = expr_res.toInstruction()

                            var.version = expr_res.iid
                            if flag:
                                if constant_res_flag:
                                    var.version = self.constants[str(expr_res.constant)]
                                else:
                                    var.version = self.irGenerator.getPC()
                                self.irGenerator.compute(block, op, designator_res, expr_res)
                                # TODO should the pc of IRGenerator be incremented at here? 2/15/2023

                                self.irGenerator.pc += 2
                                # print(f"UPDATE SSAMAP")
                                # print(var.name)
                                # print(var.address)
                                # print(var.version)
                                # print("-------------------\n")
                                varManager.updatessamap(var.address, var.version)
                            block.global_ssa[var.address] = var.version

    def typeDecl(self):
        dimensionList = list()
        if self.inputSym.checkSameType(TokenType.varToken):
            self.next()
        elif self.inputSym.checkSameType(TokenType.arrToken):
            self.next()
            while True:
                if self.inputSym.checkSameType(TokenType.openbracketToken):
                    self.next()
                    if self.inputSym.checkSameType(TokenType.number):
                        dimensionList.append(self.inputSym.value)
                        self.next()
                        if self.inputSym.checkSameType(TokenType.closebracketToken):
                            self.next()
                        else:
                            self.error(incorrectSyntaxException("Expected close bracket"))
                    else:
                        self.error(incorrectSyntaxException("Expected number"))
                else:
                    self.error(incorrectSyntaxException("Expected open bracket"))
                if not self.inputSym.checkSameType(TokenType.openbracketToken):
                    break
        else:
            self.error(incorrectSyntaxException("Expected var or arr"))
        return dimensionList

    def varDecl(self):
        # TODO: Need to initialize the block for variable declaration.
        dimensionList = self.typeDecl()
        while True:
            if self.inputSym.checkSameType(TokenType.ident):
                # TODO: Need to double check whether this is correct. 2/15/2023
                varResult = VariableResult()
                if len(dimensionList) == 0:
                    varResult.set(Variable(self.inputSym.value, self.tokenizer.ident2Addr[self.inputSym.value],
                                           self.irGenerator.getPC()))
                else:
                    varResult.set(Array(self.inputSym.value, self.tokenizer.ident2Addr[self.inputSym.value],
                                        self.irGenerator.getPC(), dimensionList))
            try:
                # TODO: Double check the irGenerator declareVariable method. 2/15/2023
                self.irGenerator.declareVariable(self.cfg.head, self.varManager, varResult, put=True)
            except Exception as errors:
                self.error(errors)

            self.next()
            if self.inputSym.checkSameType(TokenType.commaToken):
                self.next()
            if not self.inputSym.checkSameType(TokenType.ident):
                break
        self.irGenerator.pc += 1
        if self.inputSym.checkSameType(TokenType.semiToken):
            self.next()
        else:
            self.error(incorrectSyntaxException("Expecting declaration for variable"))

    def ifStatement(self, block, kill: list):
        cfg = self.cfg

        # TODO: Handle if block
        if self.inputSym.checkSameType(TokenType.ifToken):
            self.next()
            ifBlock = cfg.initializeIfBlock()
            # DEBUG CHECK IF BLOCK OBJECT TYPE
            # print(ifBlock)
            ifBlock.freezessa(block.global_ssa, None)  # Update the SSA of the if block
            print(f"global ssa: {block.global_ssa}")
            ifBlock.setparent(block)
            block.setchild(ifBlock)
            joinBlock = cfg.initializeJoinBlock()

            cfg.dom_list_if.append(ifBlock.id)
            cfg.block_in_if[ifBlock.id] = [joinBlock.id]
            cfg.join_parent[joinBlock.id] = []
            cfg.while_in_if[ifBlock.id] = []

            ifBlock.setJoinBlock(joinBlock)
            joinBlock.setparent(ifBlock)
            branch_res = self.relation(ifBlock)
            # print(branch_res.iid)
            # TODO, need to finish the if statement in parser
            self.irGenerator.compute(ifBlock, branch_res.condition, branch_res)

            # TODO: what the pc in irGenerator is, should it be incremented by 1?
            self.irGenerator.pc += 1
            tempkill = kill.copy()

            # TODO: Handle then block
            if self.inputSym.checkSameType(TokenType.thenToken):
                branch_res_then = BranchResult()
                branch_res_then.condition = self.inputSym
                self.next()
                thenBlock = cfg.initializeBlock()
                ifBlock.setThenBlock(thenBlock)
                thenBlock.setparent(ifBlock)
                # thenBlock needs to freeze the ssa of the ifBlock
                thenBlock.freezessa(ifBlock.global_ssa, None)
                cfg.block_in_if[ifBlock.id].append(thenBlock.id)
                thenBlock = self.sequence(thenBlock, kill)
                # DEBUG: check thenBlock
                # print(f'thenBlock {thenBlock is None}')

                # handle left join
                # TODO: should the index of joinId be this? 2/16/2023
                # DEBUG: Check block in if
                # print(cfg.block_in_if)
                # print(cfg.dom_list_if)
                joinId = cfg.block_in_if[cfg.dom_list_if[-1]][0]
                cfg.join_parent[joinId].append(thenBlock.id)

                if thenBlock is None:
                    return None
                branch_res_then.set(joinBlock)

                # DEBUG: Check the branch result condition
                # print(branch_res_then.condition)

                self.irGenerator.compute(thenBlock, branch_res_then.condition, branch_res_then)
                self.irGenerator.pc += 1
                thenBlock.setchild(joinBlock)
                joinBlock.setparent(thenBlock)

                thenkill = list()
                for k in kill:
                    if not (True in (j.id == k.id for j in tempkill)):
                        thenkill.append(k)

                # TODO: handle else block
                if self.inputSym.checkSameType(TokenType.elseToken):
                    # handle else block
                    self.next()
                    elseBlock = cfg.initializeBlock()
                    ifBlock.setElseBlock(elseBlock)
                    cfg.block_in_if[ifBlock.id].append(elseBlock.id)

                    # IMPORTANT: need to fix the branch result in if statement
                    ifBlock.fixupBranch(branch_res.fixuplocation, elseBlock)

                    # disable global ssa
                    self.varManager.setssamap(block.getglobalssa())

                    if elseBlock is None:
                        return None
                    elseBlock.setparent(ifBlock)
                    elseBlock.setchild(joinBlock)
                    joinBlock.setElseBlock(elseBlock)
                    # elseBlock.freezessa(ifBlock.global_ssa, None)

                    else_kill = []
                    for i in kill:
                        if not (True in (j.id == i.id for j in tempkill)):
                            else_kill.append(i)
                    elseBlock.freezessa(ifBlock.global_ssa, None)
                    elseBlock = self.sequence(elseBlock, else_kill)

                    joinId = cfg.block_in_if[cfg.dom_list_if[-1]][0]
                    cfg.join_parent[joinId].append(elseBlock.id)

                    if len(else_kill) > 0:
                        joinBlock.addKill(else_kill)
                else:
                    else_block = cfg.initializeBlock()
                    ifBlock.setElseBlock(else_block)
                    cfg.block_in_if[ifBlock.id].append(else_block.id)
                    if else_block is None:
                        return None
                    else_block.setparent(ifBlock)
                    else_block.setchild(joinBlock)
                    joinBlock.setElseBlock(else_block)
                    else_block.freezessa(ifBlock.global_ssa, None)

                    join_id = cfg.block_in_if[cfg.dom_list_if[-1]][0]
                    cfg.join_parent[join_id].append(else_block.id)
                    ifBlock.fixupBranch(branch_res.fixuplocation, joinBlock)

                if self.inputSym.checkSameType(TokenType.fiToken):
                    # TODO: should we use pop at here?
                    cfg.dom_list_if.pop()
                    self.next()

                    # TODO: Is this correct? 2/16/2023
                    left_block_ssa = cfg.blocks[cfg.join_parent[joinBlock.id][0] - cfg.base_block_counter].global_ssa
                    right_block_ssa = cfg.blocks[cfg.join_parent[joinBlock.id][1] - cfg.base_block_counter].global_ssa
                    # print(f"SSA left {left_block_ssa}, SSA right {right_block_ssa}")

                    # DEBUG SSA
                    # print(f"left_block_ssa {left_block_ssa}")
                    # print(f"right_block_ssa {right_block_ssa}")

                    # TODO: need to fix the phi instruction
                    joinBlock.createPhi(self.tokenizer.addr2Ident, left_block_ssa, right_block_ssa)
                    # print(f"JoinBlock Phis: {joinBlock.phiManager.phis}")
                    for x in joinBlock.phiManager.phis.keys():
                        joinBlock.phiManager.phis[x].variable.version = self.irGenerator.getPC()
                        joinBlock.phiManager.phis[x].id = self.irGenerator.getPC()
                        self.irGenerator.pc += 1

                    for x in joinBlock.phiManager.phis.values():
                        # print(f"Phi instruction {x.toString()} , version {x.variable.version}, addr {x.variable.address}")
                        joinBlock.instructions.append(x)

                    for instr in joinBlock.instructions:
                        if isinstance(instr, PhiInstruction):
                            if instr.variable.address in joinBlock.global_ssa.keys():
                                # print('#####################', instr.variable.address, instr.variable.version)

                                joinBlock.global_ssa[instr.variable.address] = instr.variable.version
                                # print(f'operandx {instr.operandx.variable.version}, operandy {instr.operandy.variable.version}')
                                # print(joinBlock.global_ssa)
                                self.varManager.setssamap(joinBlock.global_ssa)
                            # else:
                            # print(f'operandx {instr.operandx.variable.version}, operandy {instr.operandy.variable.version}')
                else:
                    self.error(incorrectSyntaxException("Expecting fi token"))
                    return None
            else:
                self.error(incorrectSyntaxException("Expecting then token"))
                return None
        else:
            self.error(incorrectSyntaxException("Expecting if token"))
            return None
        return joinBlock

    def funcCall(self, block):
        # print(f"Function call function is called")
        if self.inputSym.checkSameType(TokenType.callToken):
            op = self.inputSym
            self.next()
            func_sym = self.inputSym
            # print(f"DEBUG: func_sym {self.inputSym.value}")

            # TODO: double check the irGenerator.pc increment
            if self.inputSym.value in Operator.standardIoOperator:
                op = self.inputSym
                if self.inputSym.value == "InputNum":
                    self.next()
                    if self.inputSym.checkSameType(TokenType.openparenToken):
                        self.next()
                        if self.inputSym.checkSameType(TokenType.closeparenToken):
                            self.next()
                        else:
                            self.error(incorrectSyntaxException("Expecting )"))
                            return None
                    self.irGenerator.pc += 1
                    print(f"\n INPUTTTTTTT Debug inputNum- show current pc : {self.irGenerator.pc}")
                    self.irGenerator.compute(block, op, None, None)
                    self.irGenerator.pc += 1
                    return InstructionResult(self.irGenerator.getPC() - 1)
                elif self.inputSym.value == "OutputNum":
                    self.next()
                    print("\n OutputNum is called")
                    if self.inputSym.checkSameType(TokenType.openparenToken):
                        self.next()
                        res = self.expression(block)
                        # print(f"expression type {type(res)}")
                        if res is not None:
                            print("res is not None!")
                            print(block.id)
                            print(res.iid)
                            if isinstance(res, VariableResult):
                                print(res.variable.name)
                                print(res.variable.version)
                            print(f"instruction op is : {op.value}")
                            self.irGenerator.compute(block, op, res, None)
                            print([i.toString(True) for i in block.instructions])
                            self.irGenerator.pc += 2
                        if self.inputSym.checkSameType(TokenType.closeparenToken):
                            self.next()
                            return None
                        else:
                            self.error(incorrectSyntaxException("Expecting )"))
                            return None
                    else:
                        self.error(incorrectSyntaxException("Expecting ("))
                        return None
                elif self.inputSym.value == "OutputNewLine":
                    self.next()
                    if self.inputSym.checkSameType(TokenType.openparenToken):
                        self.next()
                        if self.inputSym.checkSameType(TokenType.closeparenToken):
                            self.next()
                        else:
                            self.error(incorrectSyntaxException("Expecting )"))
                            return None
                    else:
                        self.error(incorrectSyntaxException("Expecting ("))
                        return None
                    self.irGenerator.compute(block, op, None, None)
                    self.irGenerator.pc += 1
                    return None
        else:
            self.error(incorrectSyntaxException("Expecting call token"))
            return None

    def whilestatement(self, block, kill: list):
        # TODO: need to be implemented before while block is done.
        cfg = self.cfg
        followBlock = None

        if self.inputSym.checkSameType(TokenType.whileToken):
            self.next()
            whileBlock = cfg.initializeWhileBlock()

            if len(cfg.dom_list_if) > 0:
                if len(cfg.dom_list) > 0:
                    if cfg.dom_list_if[-1] < cfg.dom_list_if[-1]:
                        cfg.while_in_if[cfg.dom_list_if[-1]].append(whileBlock.id)
                    else:
                        cfg.while_in_if[cfg.dom_list_if[-1]].append(whileBlock.id)

            cfg.block_in_while[whileBlock.id] = [whileBlock.id]
            cfg.loopblocks_in_while[whileBlock.id] = []
            cfg.dom_list.append(whileBlock.id)
            parent_id = 0

            if len(cfg.parent_stack) == 0:
                parent_id = block.id
            else:
                parent_id = cfg.parent_stack.pop()
            print(cfg.blocks)
            # print(f"block0 ssa {cfg.blocks[0].getglobalssa()}, block1 ssa {cfg.blocks[1].getglobalssa()} ")
            # print(f"ssa0 {cfg.blocks[whileBlock.id - cfg.base_block_counter].getglobalssa()}")
            # print(f"ssa1 {cfg.blocks[parent_id-cfg.base_block_counter-1].getglobalssa()}")
            # print(f"while block id {whileBlock.id}, parent id {parent_id}")

            cfg.blocks[whileBlock.id].getglobalssa().update(cfg.blocks[parent_id].getglobalssa())
            cfg.parent_stack.append(whileBlock.id)

            whileBlock.setparent(block)
            block.setchild(whileBlock)
            # print(f"DEBUG while ssa. All ssa in cfg {[i.getglobalssa() for i in cfg.blocks]}")

            loopBlock = cfg.initializeBlock()
            whileBlock.setLoopBlock(loopBlock)
            loopBlock.setparent(whileBlock)

            # print(f"***\n block ssa {block.global_ssa}")
            whileBlock.freezessa(block.global_ssa, None)

            branch_res = self.relation(whileBlock)
            self.irGenerator.compute(whileBlock, branch_res.condition, branch_res)
            self.irGenerator.pc += 2

            tempkill = kill.copy()
            if self.inputSym.checkSameType(TokenType.doToken):
                branch_res_do = BranchResult()
                branch_res_do.condition = self.inputSym
                branch_res_do.set(whileBlock)
                self.next()

                if len(cfg.dom_list) == 0 or len(cfg.parent_stack) == 0:
                    print("Warning: dom_list or parent_stack is empty.")

                parent_id = cfg.parent_stack.pop()
                for i in cfg.dom_list:
                    cfg.block_in_while[i].append(loopBlock.id)

                cfg.loopblocks_in_while[cfg.dom_list[-1]].append(loopBlock.id)
                cfg.blocks[loopBlock.id].getglobalssa().update(cfg.blocks[parent_id].getglobalssa())
                # print(f"DEBUG while ssa do. All ssa in cfg {[i.getglobalssa() for i in cfg.blocks]}")

                cfg.parent_stack.append(loopBlock.id)
                loopBlock.freezessa(whileBlock.global_ssa, None)

                loopBlock = self.sequence(loopBlock, tempkill)

                if loopBlock is None:
                    return None
                if self.inputSym.checkSameType(TokenType.odToken):
                    self.next()
                    branch_res_do.set(whileBlock)
                    self.irGenerator.compute(loopBlock, branch_res_do.condition, branch_res_do)
                    self.irGenerator.pc += 1
                    loopBlock.setchild(whileBlock)
                    whileBlock.setchild(loopBlock)

                    loopkill = []
                    for i in kill:
                        if not (True in (j.id == i.id for j in tempkill)):
                            loopkill.append(i)
                    if len(loopkill) > 0:
                        whileBlock.addKill(loopkill)
                    print(f"DEBUG: cfg.block_in_while {cfg.block_in_while}")
                    print(f"DEBUG: input create phi block id {cfg.blocks[cfg.block_in_while[whileBlock.id][-1]].id}")

                    whileBlock.createPhis(cfg.blocks[cfg.block_in_while[whileBlock.id][-1]],
                                          self.tokenizer.addr2Ident, self.irGenerator)
                    # print(f"DEBUG while ssa do. All ssa in cfg {[i.getglobalssa() for i in cfg.blocks]}")
                    # print(f"whileBlock.phiManager.phis.values(): {cfg.blocks[cfg.block_in_while[whileBlock.id][-1]-cfg.base_block_counter]}")
                    # print(f"\n****Debug While Loop phi: {whileBlock.phiManager.phis.values()}")

                    # breakpoint()
                    cfg.dom_list.pop()

                    for i in whileBlock.phiManager.phis.values():
                        whileBlock.instructions.append(i)

                    phi_dict = {}
                    print(f"\n****Debug While Loop phi: {whileBlock.phiManager.phis.values()}")
                    for i in whileBlock.phiManager.phis.values():
                        i.variable.version = self.irGenerator.pc
                        i.id = self.irGenerator.pc
                        phi_dict[i.variable.name] = InstructionResult(i.id)
                        self.irGenerator.pc += 1
                        whileBlock.global_ssa[i.variable.address] = i.variable.version
                    print(f"\n****Debug While Loop phi: {whileBlock.phiManager.phis.values()}")

                    whileBlock.phi_optimization(cfg)

                    followBlock = cfg.initializeBlock()
                    followBlock.setparent(whileBlock)
                    followBlock.freezessa(whileBlock.global_ssa, None)
                    whileBlock.setFollowBlock(followBlock)
                    whileBlock.fixupbranch(branch_res.fixuplocation, followBlock)
                else:
                    self.error(incorrectSyntaxException("Expecting od token"))
                    return None
            else:
                self.error(incorrectSyntaxException("Expecting do token"))
                return None
        else:
            self.error(incorrectSyntaxException("Expecting while token"))
            return None
        return followBlock

    def block_gen(self, block, kill: list):
        new_block = None
        while_flag = False
        if_flag = False
        # print(f"{self.inputSym.value}")
        if new_block:
            # print(f"\n*******Block ID {new_block.id}*******\n")
            pass
        # print(self.inputSym.type)
        if self.inputSym.checkSameType(TokenType.letToken):
            # print("\n*******assignment is called*******\n")
            self.assignment(block, kill)
            new_block = block
            # print(f"\n*******Block ID {new_block.id}*******\n")
        elif self.inputSym.checkSameType(TokenType.callToken):
            # print(f"\n*******DEBUG: call token found {self.inputSym.value}*******\n")
            self.funcCall(block)  # Need to define the function call
            new_block = block
            # print(f"\n*******Block ID {new_block.id}*******\n")
        elif self.inputSym.checkSameType(TokenType.ifToken):
            new_block = self.ifStatement(block, kill)
            if_flag = True
            # print(f"\n*******Block ID {new_block.id}********\n")
        elif self.inputSym.checkSameType(TokenType.whileToken):
            new_block = self.whilestatement(block, kill)
            while_flag = True
        else:
            # print(self.inputSym.value)
            self.error(incorrectSyntaxException("No valid token found in block"))

        # print(f"\n*******Block ID {new_block.id}*******\n")
        return new_block, while_flag, if_flag

    def sequence(self, block, kill: list):
        cfg = self.cfg
        followblock = None
        cfg.seq_block = []
        while True:
            # DEBUG: Check the block
            # print(f"Block is None? {followblock is None}")
            # print(f"Is current symbol call? {self.inputSym.checkSameType(TokenType.callToken)}")
            # TODO: Need to double check the followblock. 2/15/2023
            if followblock is None:
                new_block, while_flag, if_flag = self.block_gen(block, kill)
                if while_flag:
                    if len(cfg.dom_list) > 0:
                        if new_block.id not in cfg.loopblocks_in_while[cfg.dom_list[-1]]:
                            cfg.loopblocks_in_while[cfg.dom_list[-1]].append(new_block.id)
                            cfg.block_in_while[cfg.dom_list[-1]].append(new_block.id)
                if if_flag:
                    if len(cfg.dom_list) > 0:
                        if isinstance(new_block, JoinBlock):
                            cfg.block_in_while[cfg.dom_list[-1]].append(new_block.id)
            else:
                new_block, while_flag, if_flag = self.block_gen(followblock, kill)
                if while_flag:
                    if len(cfg.dom_list) > 0:
                        if new_block.id not in cfg.loopblocks_in_while[cfg.dom_list[-1]]:
                            cfg.loopblocks_in_while[cfg.dom_list[-1]].append(new_block.id)
                            cfg.block_in_while[cfg.dom_list[-1]].append(new_block.id)
                if if_flag:
                    if len(cfg.dom_list) > 0:
                        if isinstance(new_block, JoinBlock):
                            cfg.block_in_while[cfg.dom_list[-1]].append(new_block.id)
            if new_block is None:
                return None
            if while_flag:
                followblock = new_block
            if if_flag:
                followblock = new_block

            # print(f"Current Symbol Value {self.inputSym.value}")
            if self.inputSym.checkSameType(TokenType.semiToken):
                self.next()
                if self.inputSym.checkSameType(TokenType.elseToken) or self.inputSym.checkSameType(TokenType.fiToken) \
                        or self.inputSym.checkSameType(TokenType.endToken) or self.inputSym.checkSameType(
                    TokenType.odToken):
                    break
            else:
                break

        # DEBUG: Check the new_block is None
        # print(f"New block is None? {new_block is None}")
        return new_block

    def computation(self):
        if self.inputSym.checkSameType(TokenType.mainToken):
            self.next()
            kill = list()
            while self.inputSym.checkSameType(TokenType.varToken) or self.inputSym.checkSameType(TokenType.arrToken):
                # print(f"Check current symbol {self.inputSym.value}")
                self.varDecl()
            self.irGenerator.pc += 1
            if self.inputSym.checkSameType(TokenType.beginToken):
                self.next()

                self.constantBlock = self.cfg.initializeConstantBlock()

                self.cfg.head.id = self.blockcounter + 1
                self.cfg.base_block_counter = self.blockcounter + 1
                self.blockcounter += 1
                self.cfg.head.setparent(self.constantBlock)
                self.constantBlock.setchild(self.cfg.head)

                # DEBUG sequence function

                # print("RUN TAIL SEQUENCE")
                self.cfg.tail = self.sequence(self.cfg.head, kill)  # TODO: need to be implemented

                # DEBUG: check if tail is None
                # print("Tail is None? ", self.cfg.tail is None)
                if self.cfg.tail is None:
                    return False

                if self.inputSym.checkSameType(TokenType.endToken):
                    # print("End token is found")
                    self.next()
                    if self.inputSym.checkSameType(TokenType.periodToken):
                        op = self.inputSym
                        self.next()
                        self.irGenerator.compute(self.cfg.tail, op, None, None)
                        self.irGenerator.pc += 1
                        return True
                    else:
                        self.error(incorrectSyntaxException("Expecting period token"))
                else:
                    self.error(incorrectSyntaxException("Expecting end token"))
            else:
                self.error(incorrectSyntaxException("Expecting begin token"))
        else:
            self.error(incorrectSyntaxException("Expecting main token"))

        return False

    def run_parser(self):
        self.irGenerator.reset()
        self.next()
        self.cfg.done = self.computation()
        self.cfg.cse_optimization()
        print()
        print("BEFORE CSE")
        for i in self.cfg.blocks:
            for j in i.instructions:
                print(j.toString(True))
        print()


        self.cfg.optimize()
        print()
        print("AFTER CSE")
        for i in self.cfg.blocks:
            for j in i.instructions:
                print(j.toString(True))
        print("---------------------\n")


        self.cfg.move_replace()
        # print(self.cfg.blocks)
        #
        # print("Is CFG done? ", self.cfg.done)

        return self.cfg








