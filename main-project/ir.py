from interpreter import *
from collections import defaultdict

# build the abstract instruction in IR
class Instruction(object):
    def __init__(self, instruction, operand1, operand2, *operands):
        # operand1 is the first operator of this instruction
        # operand2 is the second operator of this instruction
        # operands is a list of operands of this instruction, which will be used if phi instruction exists.
        self.instruction_label_counter = 0
        self.instruction = instruction
        self.operand1 = operand1
        self.operand2 = operand2
        self.operands = operands
        # result is used for store the result of instruction when register allocation start
        self.result = None
        # once we have the register allocation, the assigned registers are stored for the operands in the variable below
        self.assigned_operand1 = None
        self.assigned_operand2 = None
        self.assigned_result = None
        self.assigned_operands = []

        # update instruction label counter
        self.label = self.instruction_label_counter
        self.instruction_label_counter += 1

    def instruction_label_counter_reset(self):
        # if new IR is generated, then the label counter needs to be reset
        self.instruction_label_counter = 0

    def update(self):
        # TODO
        pass



class IR(object):

    # Predefined functions: TODO
    PRE_FUNCTION = {
        "InputNum" : "read",
        "OutputNum": "write",
        "OutputNewLine" : "writeNL",
    }

    # Dictionary for mapping operator to instructions
    INSTRUCTION_MAP = {
        '+': ['add'],
        '-': ['sub'],
        '/': ['div'],
        '*': ['mul'],
        '==': ['cmp', 'beq'],
        '!=': ['cmp', 'bne'],
        '<': ['cmp', 'blt'],
        '>': ['cmp', 'bgt'],
        '>=': ['cmp', 'bge'],
        '<=': ['cmp', 'ble'],
        'store': ['store'],
        'load': ['load'],
        'bra': ['bra'],
        'phi': ['phi'],
        'adda': ['adda']
    }

    def __init__(self, func_name, ast, local_symbol_table, global_symbol_table):
        self.func_name = func_name
        self.ast = ast
        self.local_symbol_table = local_symbol_table
        self.global_symbol_table = global_symbol_table
        self.ir = None
        self.basic_block = None
        self.control_flow_graph = None

        # define start_node and end_node dictionaries for traversing the control flow graph
        self.start_node = {}
        self.end_node = {}

        # define defaultdict that contains the control flow graph nodes as key which are pointed by instructions
        self.cfg_node_instructions = defaultdict(list)

        # track the last instruction for future value assignments.
        self.last_instruction = None




