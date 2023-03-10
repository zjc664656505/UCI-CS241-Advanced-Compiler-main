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
from DataStructure.Blocks.ConstantBlock import ConstantBlock
from DataStructure.Instruction import DeleteMode
from DataStructure.DataResult.RegisterResult import RegisterResult
from pathlib import Path
from DataStructure.Blocks.WhileBlock import WhileBlock
import os


class Graphviz:
    def __init__(self, parser, test_path, vis_path):
        self.parser = parser
        self.test_path = test_path
        self.vis_path = vis_path
        self.cfg = parser.cfg
        self.blockStack = deq()
        self.graph_filename = None
        self.printedBlock = [False] * len(self.cfg.getAllBlocks())
        self.function_calls = {}
        self.dom_edges = set()
        self.branch_edges = set()
        self.fall_through_edges = set()
        self.connect_edges = set()

        # TODO: need to implement while loop
        self.while_loopback_branch = set()

        self.phi_dict = dict()

    def getGraphFileName(self):
        return self.graph_filename

    def showGraph(self):
        code_filename = Path(self.test_path).stem
        self.graph_filename = self.vis_path + code_filename + ".gv"

        with open(self.graph_filename, 'w') as gf:
            gf.write('digraph G {\n')
            gf.write('node [shape=record];\n')

            # Start the main block
            gf.write('subgraph cluster_main{\n')
            gf.write('label = "Main";\n')
            for idx, main_block in enumerate(self.cfg.blocks):
                self.writeBlock(main_block, gf, -1)
            for idx, main_block in enumerate(self.cfg.blocks):
                if idx == 0:
                    self.connect_edges.add((0, 1))
                else:
                    self.findEdge(main_block, self.cfg)
            gf.write('}\n')
            # print(self.connect_edges)
            self.writeConnectEdge(gf)
            self.writeDomEdge(gf)
            self.writeBranchEdge(gf)
            self.writeWhileBranch(gf)
            self.writeFallThroughEdge(gf)

            gf.write('}\n')
            print(self.phi_dict)


    def writeBlock(self, block, out, FLAG):
        out.write('BB' + str(block.id) + ' [shape=record, label=')
        out_str = self.writeInstruction(block, out, FLAG)
        print("\n************\n"+out_str)
        out.write(out_str)

    def writeInstruction(self, block, out, FLAG):
        if isinstance(block, IfBlock):
            out_str = '\"<b>BB' + str(block.id) + '|{'
        elif isinstance(block, JoinBlock):
            out_str = '\"<b>BB' + str(block.id) + '|{'
        else:
            out_str = '\"<b>BB' + str(block.id) + '|{'
        for instr in block.instructions:
            #print(f"Instruction {type(instr)}")
            instr_temp = instr
            # if instr_temp.deletemode == DeleteMode._NOT_DEL:
            # TODO: debug phi
            #print(f"operation code {instr.opcode}")
            if instr_temp.deletemode == DeleteMode._NOT_DEL:
                #print(f"instruction type {type(instr_temp)}, instruction opcode {instr_temp.opcode}")
                if instr.opcode == OperatorCode.phi:
                    self.phi_dict[instr.variable.version] = [instr.operandx.iid, instr.operandy.iid]
                out_str += (instr_temp.toString(True) + '|')


        out_str = out_str[:-1] + '}\"];\n'
        return out_str

    def findEdge(self, block, cfg):
        if isinstance(block, IfBlock):
            self.dom_edges.add((block.parent.id, block.id))
            self.dom_edges.add((block.id, block.thenBlock.id))
            self.dom_edges.add((block.id, block.elseBlock.id))
            self.dom_edges.add((block.id, block.joinBlock.id))

            self.branch_edges.add((block.id, block.elseBlock.id))
            self.fall_through_edges.add((block.id, block.thenBlock.id))
        elif isinstance(block, WhileBlock):
            self.dom_edges.add((block.parent.id, block.id))
            self.dom_edges.add((block.id, block.loopblock.id))
            self.dom_edges.add((block.id, block.followBlock.id))

            self.branch_edges.add((block.id, block.followBlock.id))
            self.fall_through_edges.add((block.id, block.loopblock.id))

            self.while_loopback_branch.add((cfg.block_in_while[block.id][-1], block.id))
        elif isinstance(block, JoinBlock):
            self.fall_through_edges.add((cfg.join_parent[block.id][1], block.id))
            self.branch_edges.add((cfg.join_parent[block.id][0], block.id))
        else:
            if block.parent.id != 0 and block.id != 1:
                self.dom_edges.add((block.parent.id, block.id))

    def writeDomEdge(self, out):
        for edge in self.dom_edges:
            out.write(f"BB{edge[0]}:b -> BB{edge[1]}:b [color=blue, style=dotted, label=\"dom\"];\n")

    def writeBranchEdge(self, out):
        for edge in self.branch_edges:
            out.write(f"BB{edge[0]}:s -> BB{edge[1]}:n [label=\"branch\"];\n")

    def writeWhileBranch(self, out):
        for edge in self.while_loopback_branch:
            out.write(f"BB{edge[0]}:s -> BB{edge[1]}:e [label=\"branch\"];\n")

    def writeFallThroughEdge(self, out):
        for edge in self.fall_through_edges:
            out.write(f"BB{edge[0]}:s -> BB{edge[1]}:n [label=\"fall-through\"];\n")

    def writeConnectEdge(self, out):
        for edge in self.connect_edges:
            out.write(f"BB{edge[0]}:s -> BB{edge[1]}:n ;\n")

    def writeWhileEdge(self, out):
        # TODO: need to implement while loop
        pass



if __name__ == "__main__":
    cbelem = "class_test/cbelem/while/"
    # file_dir = "./test/" + cbelem + "nested_while_no_expr_elim.smpl"

    ChinHung = "class_test/ChinHung/"
    # file_dir = "./test/" + ChinHung + "if_branch_exist_instruction.txt"
    # file_dir = "./test/" + ChinHung + "while_having_computation_in_compare.txt"

    Hongyu = "class_test/Hongyu/"

    ##array##
    # file_dir = "./test/" + Hongyu + "array/" + "test1.smpl"
    # file_dir = "./test/" + Hongyu + "array/" + "test2.smpl"
    # file_dir = "./test/" + Hongyu + "array/" + "test3.smpl"

    ##iftests##
    # file_dir = "./test/" + Hongyu + "iftests/" + "test1.smpl"

    ##simpletests##
    # file_dir = "./test/" + Hongyu + "simpletests/" + "test1.smpl"

    ##while##
    # file_dir = "./test/" + Hongyu + "while/" + "test1.smpl"
    # file_dir = "./test/" + Hongyu + "while/" + "test2.smpl"
    # file_dir = "./test/" + Hongyu + "while/" + "test3.smpl"
    # file_dir = "./test/" + Hongyu + "while/" + "test4.smpl"

    jmcgowa = "class_test/jmcgowa/"

    ##CSE_Tests##
    # file_dir = "./test/" + jmcgowa + "CSE_Tests/" + "CSE1.txt"
    # file_dir = "./test/" + jmcgowa + "CSE_Tests/" + "CSE2.txt"
    # file_dir = "./test/" + jmcgowa + "CSE_Tests/" + "CSE3.txt"
    # file_dir = "./test/" + jmcgowa + "CSE_Tests/" + "CSE4.txt"
    # file_dir = "./test/" + jmcgowa + "CSE_Tests/" + "CSE5.txt"
    # file_dir = "./test/" + jmcgowa + "CSE_Tests/" + "CSE6.txt"
    # file_dir = "./test/" + jmcgowa + "CSE_Tests/" + "IF_ELSE_NO_WRITE.txt"
    # file_dir = "./test/" + jmcgowa + "CSE_Tests/" + "IF_ELSE_WRITE.txt"
    # file_dir = "./test/" + jmcgowa + "CSE_Tests/" + "IF_IN_IF_ARRAY_NO_WRITE.txt"
    # file_dir = "./test/" + jmcgowa + "CSE_Tests/" + "IF_IN_IF_ARRAY_WRITE.txt"

    ##Regular Tests##
    # file_dir = "./test/" + jmcgowa + "Array1.txt"
    # file_dir = "./test/" + jmcgowa + "Array1_2.txt"
    # file_dir = "./test/" + jmcgowa + "Array2.txt"
    # file_dir = "./test/" + jmcgowa + "Array2_2.txt"
    # file_dir = "./test/" + jmcgowa + "Array3.txt"
    # file_dir = "./test/" + jmcgowa + "Array3_3.txt"
    # file_dir = "./test/" + jmcgowa + "BasicCall.txt"
    # file_dir = "./test/" + jmcgowa + "If_Else.txt"
    # file_dir = "./test/" + jmcgowa + "Nested_Ifs.txt"
    file_dir = "./test/" + jmcgowa + "While1.txt"



    tokenize = Tokenizer(file_dir)
    sym = tokenize.getSym()
    parse = Parser(file_dir)
    cfg = parse.run_parser()
    graph = Graphviz(parse, file_dir, "./visualization/")
    graph.showGraph()
    #graph_show = Source.from_file("./visualization/"+ file+ ".gv").view()