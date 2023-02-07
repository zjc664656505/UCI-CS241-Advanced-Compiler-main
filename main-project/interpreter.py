from tokenizer import *
from parser import *


# build ip Symbol_Table to track variable names and variable values
class SymbolTable:
    def __init__(self):
        self.symbol_table = {}
        self.parent = None # to track the global symbol table

    def get(self, name):
        value = self.symbol_table.get(name, None)
        if value is None and self.parent:
            return self.parent.get(name)
        return value

    def set(self, name, value):
        self.symbol_table[name] = value

    def remove(self, name):
        del self.symbol_table[name]


# build up Context Class
class Context:
    def __init__(self, display_name, parent=None):
        self.display_name = display_name
        self.parent = parent
        self.symbol_table = None


# build value class for interpreter
class Number:
    def __init__(self, value):
        self.value = value
        self.set_context()

    def set_context(self, context=None):
        self.context = context
        return self

    def add_to(self, other):
        if isinstance(other, Number):
            return Number(self.value + other.value).set_context(self.context)

    def sub_by(self, other):
        if isinstance(other, Number):
            return Number(self.value - other.value).set_context(
            )

    def multi_by(self, other):
        if isinstance(other, Number):
            return Number(self.value * other.value).set_context(self.context)

    def div_by(self, other):
        if isinstance(other, Number):
            return Number(self.value / other.value).set_context(self.context)

    def copy(self):
        copy = Number(self.value)
        copy.set_context(self.context)
        return copy

    def cmp_eq(self, other):
        if isinstance(other, Number):
            return Number(int(self.value == other.value)).set_context(self.context)

    def cmp_neq(self, other):
        if isinstance(other, Number):
            return Number(int(self.value != other.value)).set_context(self.context)

    def cmp_geq(self, other):
        if isinstance(other, Number):
            return Number(int(self.value >= other.value)).set_context(self.context)

    def cmp_leq(self, other):
        if isinstance(other, Number):
            return Number(int(self.value <= other.value)).set_context(self.context)

    def cmp_gt(self, other):
        if isinstance(other, Number):
            return Number(int(self.value > other.value)).set_context(self.context)

    def cmp_lt(self, other):
        if isinstance(other, Number):
            return Number(int(self.value < other.value)).set_context(self.context)

    def and_by(self, other):
        if isinstance(other, Number):
            return Number(int(self.value and other.value)).set_context(self.context)

    def or_by(self, other):
        if isinstance(other, Number):
            return Number(int(self.value or other.value)).set_context(self.context)

    def __repr__(self):
        return str(self.value)

class Interpreter:
    def visit(self, node, context):
        #visit NumberNode
        #visit BinOpNOde
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.no_visit_method)
        return method(node, context)

    def no_visit_method(self, node, context):
        raise Exception(f'No visit_{type(node).__name__} method defined')

    def visit_VarAssignNode(self, node, context):
        var_name = node.var_name_token.value
        value = self.visit(node.value_node, context)
        context.symbol_table.set(var_name, value)
        return value

    def visit_VarAccessNode(self, node, context):
        var_name = node.var_name_token.value
        value = context.symbol_table.get(var_name)
        value = value.copy()
        return value

    def visit_NumberNode(self, node, context):
        return Number(node.token.value).set_context(context)

    def visit_BinOpNode(self, node, context):
        left = self.visit(node.left_node, context)
        right = self.visit(node.right_node, context)
        res = 0
        if node.op_token.type == PLUS:
            res = left.add_to(right)
        if node.op_token.type == MINUS:
            res = left.sub_by(right)
        if node.op_token.type == MUL:
            res = left.multi_by(right)
        if node.op_token.type == DIV:
            res = left.div_by(right)
        if node.op_token.value == '<':
            res = left.cmp_lt(right)
        if node.op_token.value == ">":
            res = left.cmp_gt(right)
        if node.op_token.value == ">=":
            res = left.cmp_geq(right)
        if node.op_token.value == "<=":
            res = left.cmp_leq(right)
        if node.op_token.value == "==":
            res = left.cmp_eq(right)
        if node.op_token.value == "!=":
            res = left.cmp_neq(right)
        if node.op_token.matches(KEYWORD, 'AND'):
            res = left.and_by(right)
        if node.op_token.matches(KEYWORD, 'OR'):
            res = left.or_by(right)

        return res

    def visit_UnaryOpNode(self, node, context):
        number = self.visit(node.node, context)
        if node.op_token.type == MINUS:
            res = number.multi_by(Number(-1))
        elif node.op_token.type == PLUS:
            res = number.multi_by(Number(1))
        return res

global_symbol_table = SymbolTable()
global_symbol_table.set("None", Number(0))
global_symbol_table.set('True', Number(1))
global_symbol_table.set('False', Number(0))


def main(text):
    lexer = Lexer(text)
    tokens, error = lexer.make_tokens()
    if error:
        return None, error
    else:
        ast = []
        print(f'Tokenizer: {tokens}')
        if all(isinstance(i, list) for i in tokens):
            for token in tokens:
                parser = Parser(token)
                ast.append(parser.computation())
        else:
            parser = Parser(tokens)
            ast = parser.computation()

        interpreter = Interpreter()
        context = Context('<main-dlx>')
        context.symbol_table = global_symbol_table
        res = [interpreter.visit(i.node, context) for i in ast]

        return res, [i.error for i in ast]

if __name__ == "__main__":
    text = "let var a <- 0; let var b <- 1; let var c <- (a AND b); let var d <- (a OR b)."
    result, error = main(text)

    for i in error:
        if i: print(i.error_string())
    else:
        print(result)