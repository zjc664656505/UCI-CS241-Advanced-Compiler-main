from interpreter import *
from collections import defaultdict


# build Memory class to represent abstract representation of operand in memory
class Memory:
    def __init__(self, name=None, size=None, scope=None):
        # name is the memory location representing the name of the variable
        self.name = name

        # size is the variable object size
        self.size = size

        # scope is representing whether or not the this variable stored in memory is global or local variable
        self.scope = scope

    def __repr__(self):
        if self.name:
            return f"(variable {self.name} with size {self.size}"


# build varible value class to represent variable value
class Value:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f'Immediate data value -> {self.value}'


# build the abstract instruction in IR. This class can be regarded as an object table to assign instruction labels
class Instruction:
    def __init__(self, instruction, operand1=None, operand2=None, *operands):
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

    def update(self, operand1, operand2):
        # define function for updating instruction operands at a later point
        if operand1:
            self.operand1 = operand1
        if operand2:
            self.operand2 = operand2

    def check_operand_is_variable(self, operand):
        if operand:
            if isinstance(operand, str) and operand[0] not in ['#', '[', '.', "!", ";"]:
                return True

    def check_operand_is_varibale_or_value(self, operand):
        if operand:
            if isinstance(operand, str) and operand[0] not in ['#', '[', '.', "!", ";"]:
                return True
            elif isinstance(operand, int):
                return True
        return False

    def check_operand_in_mem(self, operand):
        return operand is not None and isinstance(operand, Memory)

    def __contains__(self, operand):
        # define a class to check whether operand object matches with the operands in instructions
        if self.result == operand:
            return True
        elif self.operand1 == operand:
            return True
        elif self.operand2 == operand:
            return True

        for ops in self.operands:
            if ops == operand:
                return True
        return False

    def __repr__(self):
        # for printing out the current instruction in intermediate representation
        ir = f"current label - {self.label} : current instruction - {self.instruction}"

        # TODO: Unfinished. Need to address the operands.

        return ir

    def __hash__(self):
        return hash(f'{self.instruction} {self.operand1} {self.operand2} {" ".join([str(i) for i in self.operands])}')


# put the program into IR form
class IR:
    def __init__(self, func_name, ast, local_symbol_table, global_symbol_table):
        # define the in-class variables
        # Predefined functions: TODO
        self.PRE_FUNCTION = {
            "InputNum": "read",
            "OutputNum": "write",
            "OutputNewLine": "writeNL",
        }

        # Dictionary for mapping operator to instructions
        self.INSTRUCTION_MAP = {
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

        self.func_name = func_name
        self.ast = ast
        self.local_symbol_table = local_symbol_table
        self.global_symbol_table = global_symbol_table
        self.ir = None
        self.basic_block = None
        self.control_flow_graph = None

        # define start_node and end_node dictionaries for traversing the control flow graph
        # TODO: need to build up control flow graph first
        self.start_node = {}
        self.end_node = {}

        # define defaultdict that contains the control flow graph nodes as key which are pointed by instructions
        self.cfg_node_instructions = defaultdict(list)

        # track the last instruction for future value assignments.
        self.last_instruction = None

    def instruction_table(self, operator, *operands):
        """
        :param operator: instruction operator +-*/...
        :param operands: a list of operands str, int
        :return: instruction label counter number
        """
        if not operands:
            instruction = Instruction(operator)
            self.ir.append(instruction)
            return instruction.label

        # first operand
        operand1 = operands[0]
        if len(operands) == 1:
            instruction = Instruction(self.INSTRUCTION_MAP[operator][0], operand1)
            self.ir.append(instruction)
            return instruction.label

        for instruct, operand2 in zip(self.INSTRUCTION_MAP[operator], operands[1:]):
            instruction = Instruction(instruct, operand1, operand2)
            self.ir.append(instruction)
            operand1 = instruction.label

        return operand1


