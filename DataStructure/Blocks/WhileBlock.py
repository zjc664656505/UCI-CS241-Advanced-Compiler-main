from DataStructure.PhiInstruction import PhiInstruction
from DataStructure.Manager.PhiManager import PhiManager
from DataStructure.Manager.VariableManager import VariableManager
from IR.IrGenerator import IrGenerator
from DataStructure.DataResult.RegisterResult import RegisterResult
from util.Constants import Constants
from DataStructure.Blocks import Block
from DataStructure.Manager.VariableManager import VariableManager
from DataStructure.Blocks.IBlock import IBlock
from DataStructure.Blocks.JoinBlock import JoinBlock
from multipledispatch import dispatch
from DataStructure.Instruction import Instruction, InstructionResult
from DataStructure.Operator import Operator, OperatorCode
from DataStructure.DataResult.ConstantResult import ConstantResult
from DataStructure.DataResult.RegisterResult import RegisterResult


# TODO: Need to finish Control flow graph first
