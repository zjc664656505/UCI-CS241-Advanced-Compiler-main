# while block is not done
# build parser for existing blocks
# objective: test IR generator to the right output
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
#from DataStructure.Blocks.WhileBlock import WhileBlock
from DataStructure.Instruction import DeleteMode
from copy import deepcopy
import sys


class Parser:
    def __init__(self, fileName):
        self.filename = fileName
        self.tokenizer = Tokenizer
        self.inputSym = None
        self.irGenerator = IrGenerator
        self.killcounter = 0
        self.blockcounter = 0
        # TODO: Build cfg
        # self.cfg = CFG(self.blockCounter)
        #self.varManager =

