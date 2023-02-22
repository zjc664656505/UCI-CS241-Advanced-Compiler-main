from DataStructure.Operator import OperatorCode, Operator
from DataStructure.Token import Token, TokenType
from DataStructure.Variable import Variable
from parser.parse_util import Tokenizer
from parser.Parser import Parser
from DataStructure.Dom.DominantTree import DomNodeCSE, DominantTreeNode
from graphviz import Source
import graphviz
from DataStructure.CFG import CFG
from collections import deque as deq
from DataStructure.Blocks.Block import Block
from DataStructure.Blocks.IfBlock import IfBlock
from DataStructure.Blocks.JoinBlock import JoinBlock
from DataStructure.Instruction import DeleteMode
from DataStructure.DataResult.RegisterResult import RegisterResult


# class Grpahviz:
#     def __init__(self, parser, test_path, vis_path):
#         self.parser = parser
#         self.test_path = test_path
#         self.vis_path = vis_path
#         self.cfg = parser.cfg
#         self.blockStack = deq()
#         self.graph_filename = None
#         self.printedBlock = [False] * len(self.cfg.getAllBlocks())
#         self.function_calls = {}
#         self.dom_edges = set()
#         self.branch_edges = set()
#         self.fall_through_edges = set()
#
#         # TODO: need to implement while loop
#         self.while_loopback_branch = set()
#
#         self.phi_dict = dict()
#
#     def getGraphFileName(self):
#         return self.graph_filename
#
#     def printGraph(self):
#         code_filename = self.test_path.stem
#         self.graph_filename = self.vis_path + code_filename + ".gv"
#
#         with open(self.graph_filename, 'w') as gf:
#             gf.write('digraph G {\n')
#             gf.write('node [shape=record];\n')
#
#             # Start the main block
#             gf.write('subgraph cluster_main{\n')
#             gf.write('label = "Main";\n')
#             for idx, main_block in enumerate(self.cfg.blocks):
#                 self.writeBlock(gf, main_block)
#
#     def writeBlock(self, block, out, FLAG):
#         out.write('BB' + str(block.id) + ' [shape=record, label=')
#         out.write()
#
#     def writeInstruction(self, block, out, FLAG):
#         if isinstance(block, IfBlock):
#             out_str = '<b>If\nBB' + str(block.id) + '|{'
#         elif isinstance(block, JoinBlock):
#             out_str = '<b>Join\nBB' + str(block.id) + '|{'
#         else:
#             out_str = '<b>BB' + str(block.id) + '|{'
#         for instr in block.instructions:
#             instr_temp = instr
#             if instr_temp.delete_mode == DeleteMode._NOT_DEL:
#                 if FLAG < 0:
#                     if instr.opcode == OperatorCode.phi:
#                         self.phi_dict[instr.variable.version] = [instr.operandx.iid, instr.operandy.iid]
#                 out_str += (instr_temp.toString(True) + '|')
#
#                 # Not sure whether need to check move
#         out_str = out_str[:-1] + '}\"];\n'
#         return out_str
#
#     def findEdge(self, block, cfg):
#         if isinstance(block, IfBlock):
#             self.dom_edges.add((block.parent.id, block.id))
#             self.dom_edges.add((block.id, block.thenBlock.id))
#             self.dom_edges.add((block.id, block.elseBlock.id))
#             self.dom_edges.add((block.id, block.joinBlock.id))
#             self.branch_edges.add((block.id, block.elseBlock.id))
#             self.fall_through_edges((block.id, block.thenBlock.id))
#
#         else:
#             self.fall_through_edges.add((block.parent.id, block.id))

#Test Cases
#file_dir = "./test/sample_test.txt"
#file_dir = "./test/1darray.txt"
#file_dir = "./test/nested_if.text"
file_dir = "./test/sample2.txt"
# file_dir = "./test/random_test.txt"

# tokenize = Tokenizer(file_dir)
# sym = tokenize.getSym()
parse = Parser(file_dir)
parse.run_parser()
