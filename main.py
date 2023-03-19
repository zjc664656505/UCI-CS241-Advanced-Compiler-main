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

def dir_reader(dir_name):
    out_dir = []
    out_dir_org = []
    def token_check(file_list):
        out = []
        for file_name in file_list:
            if ".txt" in file_name:
                out.append(file_name)
            elif ".smpl" in file_name:
                out.append(file_name)
            else:
                continue
        return out
    for i in os.walk(dir_name):
        if i[2] != []:
            for file in token_check(i[2]):
                dirs = i[0] +"/"+ file
                org_out = ""
                for org in dirs.split("class_test/")[1].split("/")[:-1]:
                    org_out = org_out + org + "/"
                out_dir_org.append(org_out)
                out_dir.append(dirs)
    return zip(out_dir, out_dir_org)

if __name__ == "__main__":
    debug_mode = False
    
    if debug_mode:
        file_dir = "./test/class_test/Yunpeng/array_kill.smpl"
        tokenize = Tokenizer(file_dir)
        sym = tokenize.getSym()
        parse = Parser(file_dir)
        cfg = parse.run_parser()
        graph = Graphviz(parse, file_dir, "./visualization/debug/")
        graph.showGraph()
    else:
        for file_dirs , file_org in dir_reader("./test/"):
            try:
                file_dir = file_dirs
                tokenize = Tokenizer(file_dir)
                sym = tokenize.getSym()
                parse = Parser(file_dir)
                cfg = parse.run_parser()

                #saving path
                save_path = "./visualization/" + file_org
                if not os.path.exists(save_path):
                    os.makedirs(save_path)

                graph = Graphviz(parse, file_dir, save_path)
                graph.showGraph()
            except:
                print(file_dir)



