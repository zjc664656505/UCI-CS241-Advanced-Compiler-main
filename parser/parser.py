# while block is not done
# build parser for existing blocks
# objective: test IR generator to the right output
# TODO: Need to work on Control Flow Graph first.

from parser.exception import illegalTokenException, illegalVariableException, incorrectSyntaxException
from IR.IrGenerator import IrGenerator
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
# from DataStructure.Blocks.WhileBlock import WhileBlock
from DataStructure.Instruction import DeleteMode
from copy import deepcopy
import sys
from DataStructure.CFG import CFG


class Parser:
    def __init__(self, fileName):
        self.filename = fileName
        self.tokenizer = Tokenizer
        self.inputSym = None
        self.irGenerator = IrGenerator
        self.killcounter = 0
        self.blockcounter = 0
        # TODO: Build cfg
        self.cfg = CFG(self.blockcounter)
        self.varManager = self.cfg.mVariableManager

    def next(self):
        self.inputSym: Token = self.tokenizer.getSym()

    def error(self, e):
        self.tokenizer.error(e)

    def designator(self, block):
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
                        array_var = Array(array_in_vm.name, array_in_vm.address, array_in_vm.version,
                                          array_in_vm.dimensionList)
                        array_var.array_addr = array_in_vm.array_addr
                        index_List = []
                        while True:
                            self.next()
                            index_List.append(self.expression(block))
                            if self.inputSym.checkSameType(TokenType.closebracketToken):
                                self.next()
                            else:
                                self.error(incorrectSyntaxException("Expected close bracket"))
                                return None
                            if self.inputSym.checkSameType(TokenType.openbracketToken):
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
        return varResult

    def factor(self, block):
        result = None
        if self.inputSym.checkSameType(TokenType.ident):
            result = self.designator(block)
            if result is not None:
                var = result.variable
                if self.varManager.isVariable(var.address):
                    var.version = block.global_ssa[var.address]
                    if result.isAarry:
                        self.irGenerator.loadAarray(block, self.varManager, result)
                        result = result.toInstruction()
                        result.set(self.irGenerator.getPC() - 1)
        elif self.inputSym.checkSameType(TokenType.number):
            result = ConstantResult()
            result.set(self.inputSym.value)
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

        if result is not None:
            return result.clone()
        return result

    def term(self, block):
        factor_l = self.factor(block)
        if factor_l is not None:
            while self.inputSym.checkTerm():
                op = self.inputSym
                self.next()
                factor_r = self.factor(block)
                if factor_r is not None:
                    if isinstance(factor_l, VariableResult):
                        factor_l.setiid(factor_l.variable.version)
                    if factor_l.getiid() > 0 and (not isinstance(factor_l, RegisterResult)):
                        factor_l = factor_l.toInstruction()
                    if factor_r.getiid() > 0 and (not isinstance(factor_r, RegisterResult)):
                        factor_r = factor_r.toInstruction()
                    self.irGenerator.compute(block, factor_l, factor_r, op)
                    self.irGenerator.pc += 1
                    factor_l = factor_l.clone()
                    if isinstance(factor_l, ConstantResult) or isinstance(factor_l, VariableResult):
                        factor_l = factor_l.toInstruction()
                    factor_l.setiid(self.irGenerator.getPC() - 1)
        return factor_l

    def expression(self, block):
        term_l = self.term(block)
        if term_l is not None:
            while self.inputSym.checkExpression():
                op = self.inputSym
                self.next()
                term_r = self.term(block)
                if term_r is not None:
                    if isinstance(term_l, VariableResult):
                        term_l.setiid(term_l.variable.version)
                    if term_l.getiid() > 0 and (not isinstance(term_l, RegisterResult)):
                        term_l = term_l.toInstruction()
                    if term_r.getiid() > 0 and (not isinstance(term_r, RegisterResult)):
                        term_r = term_r.toInstruction()
                    self.irGenerator.compute(block, term_l, term_r, op)
                    self.irGenerator.pc += 1
                    term_l = term_l.clone()
                    if isinstance(term_l, ConstantResult) or isinstance(term_l, VariableResult):
                        term_l = term_l.toInstruction()
                    term_l.setiid(self.irGenerator.getPC() - 1)
        return term_l

    def relation(self, block):
        branch_res = BranchResult()
        expr_l = self.expression(block)
        if expr_l is not None:
            while self.inputSym.checkRelation():
                op = self.inputSym
                self.next()
                expr_r = self.expression(block)
                if expr_r is not None:
                    self.irGenerator.compute(block, expr_l, expr_r, op)
                    self.irGenerator.pc += 1
                    branch_res.condition = op
                    branch_res.fixuplocation = self.irGenerator.getPC() - 1
                    branch_res.targetBlock = block
        return branch_res.clone()

    def assignment(self, block, kill: list):
        varManager = self.varManager
        if self.inputSym.checkSameType(TokenType.letToken):
            self.next()
            designator_res = self.designator(block)
            if designator_res is not None:
                if self.inputSym.checkSameType(TokenType.becomesToken):
                    op = self.inputSym
                    self.next()
                    expr_res = self.expression(block)
                    if expr_res is not None:
                        if isinstance(expr_res, VariableResult):
                            flag = False
                        else:
                            flag = True
                        if expr_res.getiid() > 0 and (not isinstance(expr_res, RegisterResult)):
                            expr_res = expr_res.toInstruction()
                        var = designator_res.variable
                        if varManager.isVariable(var):
                            if designator_res.isAarry:
                                self.irGenerator.storeAarray(block, varManager, designator_res, expr_res)
                                newKill = Instruction(0)
                                # TODO: Should the killcounter be incremented at here? 2/15/2023
                                # self.killcounter += 1
                                newKill.setExternel(self.killcounter, OperatorCode.store, designator_res, None)
                                kill.append(newKill)
                                designator_res = designator_res.toInstruction()
                                designator_res.set(self.irGenerator.getPC() - 1)

                            else:
                                var.version = self.irGenerator.getPC()
                                if flag:
                                    var.version = self.irGenerator.getPC()
                                    self.irGenerator.compute(block, op, designator_res, expr_res)
                                    # TODO shoudl the pc of IRGenerator be incremented at here? 2/15/2023
                                    self.irGenerator.pc += 1
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
        dimensionList = self.typeDecl()
        while True:
            if self.inputSym.checkSameType(TokenType.ident):
                # TODO: Need to double check whether this is correct. 2/15/2023
                varResult = VariableResult()
                if len(dimensionList) == 0:
                    varResult.set(Variable(self.inputSym.value, self.tokenizer.ident2Addr[self.inputSym.value], self.irGenerator.getPC()))
                else:
                    varResult.set(Variable(self.inputSym.value, self.tokenizer.ident2Addr[self.inputSym.value], self.irGenerator.getPC(), dimensionList))
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
        if self.inputSym.checkSameType(TokenType.semiToken):
            self.next()
        else:
            self.error(incorrectSyntaxException("Expecting declaration for variable"))

    def ifStatement(self, block, kill: list):
        cfg = self.cfg
        if self.inputSym.checkSameType(TokenType.ifToken):
            self.next()
            ifBlock = cfg.initializeIfBlock()
            ifBlock.freezessa(block.global_ssa, None) # Update the SSA of the if block
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
            # TODO, need to finish the if statement in parser




    def block_gen(self, block, kill:list):
        new_block = None
        #while_flag = False
        if_flag = False

        if self.inputSym.checkSameType(TokenType.letToken):
            self.assignment(block, kill)
            new_block = block
        elif self.inputSym.checkSameType(TokenType.ifToken):
            new_block = self.ifStatement(block, kill)
            # TODO: need to be implemented

    def sequence(self, block, kill: list):
        cfg = self.cfg
        followblock = None
        cfg.seq_block = []
        while True:
            # TODO: Need to double check the followblock. 2/15/2023
            if followblock is None:
                # TODO: need to be implemented
                pass


    def computation(self):
        if self.inputSym.checkSameType(TokenType.mainToken):
            self.next()
            while self.inputSym.isSameType(TokenType.varToken) or self.inputSym.isSameType(TokenType.arrToken):
                self.varDecl(None)
            if self.inputSym.checkSameType(TokenType.beginToken):
                self.next()
                kill = list()
                self.cfg.head.id = self.blockcounter + 1
                self.cfg.base_block_counter = self.blockcounter + 1
                self.blockcounter += 1
                self.cfg.tail = # TODO: need to be implemented
                pass





