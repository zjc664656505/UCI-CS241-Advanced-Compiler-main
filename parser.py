# build up parser
# build up node for taking token values
from tokenizer import *

"""
Update Parser to add parse tree and handle the type declaration, variable declaration
"""

# Build number node to assign the number to interpreter
class NumberNode:
    def __init__(self, token):
        self.token = token

    def __repr__(self):
        return f'{self.token}'


# Build Unary Operation node
class UnaryOpNode:
    def __init__(self, op_token, node):
        self.op_token = op_token
        self.node = node

    def __repr__(self):
        return f'({self.op_token}, {self.node})'


# update: build up variable access node
class VarAccessNode:
    def __init__(self, var_name_token):
        self.var_name_token = var_name_token


# update: build up variable assign node
class VarAssignNode:
    def __init__(self, var_name_token, value_node):
        self.var_name_token = var_name_token
        self.value_node = value_node


class BinOpNode:
    def __init__(self, left_node, op_token, right_node):
        self.left_node = left_node
        self.op_token = op_token
        self.right_node = right_node

    def __repr__(self):
        return f'({self.left_node}, {self.op_token}, {self.right_node})'

class VarDeclNode:
    def __init__(self, var_name_token):
        self.var_name_token = var_name_token



# parse result
class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None
        self.next_count = 0

    def register_next(self):
        self.next_count += 1

    def register(self, res):
        self.next_count += res.next_count
        if res.error:
            self.error = res.error
        return res.node

    def success(self, node):
        self.node = node
        return self

    def failure(self, error):
        self.error = error
        return self

    def __repr__(self):
        return f'{self.node}'


class Parser:
    def __init__(self, tokens):
        # tokens is a list of tokens from the lexer
        # interpreter needs to track the current token_index which is an index into the tokens list
        # current_token is the token that the interpreter is currently looking at
        self.tokens = tokens
        self.token_index = -1
        self.next()

    def next(self):
        self.token_index += 1
        if self.token_index < len(self.tokens):
            self.current_token = self.tokens[self.token_index]
        return self.current_token

    def factor(self):
        res = ParseResult()
        token = self.current_token
        if token == '.':
            self.next()
        if token.type == INT:
            res.register_next()
            self.next()
            return res.success(NumberNode(token))
        elif token.type == IDENTIFIER:
            res.register_next()
            self.next()
            return res.success(VarAccessNode(token))
        elif token.type == LPAREN:
            res.register_next()
            self.next()
            expression = res.register(self.expression())
            if self.current_token.type == RPAREN:
                res.register_next()
                self.next()
                return res.success(expression)
        elif token.type in (PLUS, MINUS):
            res.register_next()
            self.next()
            factor = res.register(self.factor())
            return res.success(UnaryOpNode(token, factor))


    def term(self):
        res = ParseResult()
        left = res.register(self.factor())
        if res.error:
            return res

        while self.current_token.type in (MUL, DIV):
            op_token = self.current_token
            res.register_next()
            self.next()
            right = res.register(self.factor())
            if res.error:
                return res
            left = BinOpNode(left, op_token, right)
        return res.success(left)

    def expression(self):
        res = ParseResult()
        if self.current_token.matches(KEYWORD, 'let'):
            self.next()
            if self.current_token.matches(KEYWORD, 'var'):
                res.register_next()
                self.next()

                var_name = self.current_token
                res.register_next()
                self.next()
                res.register_next()
                self.next()
                expression = res.register(self.expression())
                return res.success(VarAssignNode(var_name, expression))
        elif self.current_token.matches(KEYWORD, 'var'):
            res.register_next()
            self.next()

            var_name = self.current_token
            res.register_next()
            self.next()
            res.register_next()
            self.next()
            expression = res.register(self.expression())
            return res.success(VarAssignNode(var_name, expression))
        node = res.register(self.binary_op(self.relation, ((KEYWORD, 'AND'), (KEYWORD, 'OR'))))
        return res.success(node)

    def arith_expr(self):
        return self.binary_op(self.term, (PLUS, MINUS))

    def relation(self):
        res = ParseResult()
        node = res.register(self.binary_op(self.arith_expr, [RELOP]))
        return res.success(node)

    def binary_op(self, func_l, op, func_r=None):
        if func_r == None:
            func_r = func_l

        res = ParseResult()
        left = res.register(func_l())
        if res.error:
            return res

        while self.current_token.type in op or (self.current_token.type, self.current_token.value) in op:
            op_token = self.current_token
            res.register_next()
            self.next()
            right = res.register(func_r())
            if res.error:
                return res
            left = BinOpNode(left, op_token, right)

        return res.success(left)

    def computation(self):
        if self.current_token.matches(KEYWORD, 'main'):
            self.next()
        res = self.expression()
        return res