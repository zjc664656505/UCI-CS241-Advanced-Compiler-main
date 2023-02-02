# build up parser
# build up node for taking token values
from tokenizer import *
class NumberNode:
    def __init__(self, token):
        self.token = token

    def __repr__(self):
        return f'{self.token}'


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
        if self.current_token.matches(KEYWORD, 'computation'):
            self.next()
            if self.current_token.matches(KEYWORD, 'var'):
                res = ParseResult()
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
            res = ParseResult()
            res.register_next()
            self.next()

            var_name = self.current_token
            res.register_next()
            self.next()
            res.register_next()
            self.next()
            expression = res.register(self.expression())
            return res.success(VarAssignNode(var_name, expression))
        else:
            res = ParseResult()
            left = res.register(self.term())
            if res.error:
                return res

            while self.current_token.type in (PLUS, MINUS):
                op_token = self.current_token
                res.register_next()
                self.next()
                right = res.register(self.term())
                if res.error:
                    return res
                left = BinOpNode(left, op_token, right)
            return res.success(left)

    def computation(self):
        res = self.expression()
        return res