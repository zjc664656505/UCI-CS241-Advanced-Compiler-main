"""
Warmup Project 1 by Junchen Zhao - 63286594.
Address Illegal Character Error.
However, Other Errors are going to be addressed later.
"""

# define global digit constants
DIGIT = '0123456789'

# define global variable for the token type
INT = 'INT'
PLUS = 'PLUS'
MINUS = 'MINUS'
MUL = 'MUL'
DIV = 'DIV'
LPAREN = 'LPAREN'
RPAREN = 'RPAREN'


# build up token class
class Token:
    def __init__(self, type_, value=None):
        self.type = type_
        self.value = value

    def __repr__(self):
        if self.value:
            return f'{self.type}:{self.value}'
        return f'{self.type}'


# build up error class
class Error:
    def __init__(self, error_name, error_detail):
        self.error_name = error_name
        self.error_detail = error_detail

    def error_string(self):
        return f'{self.error_name}: {self.error_detail}'


class IllegalCharError(Error):
    def __init__(self, error_detail):
        super().__init__('Ilegal Character', error_detail=error_detail)


# build up lexer
class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = -1
        self.current_char = None
        self.next()

    # next to the next character in the text
    def next(self):
        self.pos += 1
        if self.pos < len(self.text):
            self.current_char = self.text[self.pos]
        else:
            self.current_char = None

    def make_number(self):
        num_str = ''

        while self.current_char != None and self.current_char in DIGIT:
            num_str += self.current_char
            self.next()
        return Token(INT, int(num_str))

    def make_tokens(self):
        tokens = []
        subtoken = []

        while self.current_char != None:
            if self.current_char in ' \t':
                self.next()
            elif self.current_char in DIGIT:
                subtoken.append(self.make_number())
            elif self.current_char == '+':
                subtoken.append(Token(PLUS))
                self.next()
            elif self.current_char == '-':
                subtoken.append(Token(MINUS))
                self.next()
            elif self.current_char == '*':
                subtoken.append(Token(MUL))
                self.next()
            elif self.current_char == '/':
                subtoken.append(Token(DIV))
                self.next()
            elif self.current_char == '(':
                subtoken.append(Token(LPAREN))
                self.next()
            elif self.current_char == ')':
                subtoken.append(Token(RPAREN))
                self.next()
            elif self.current_char == ".":
                tokens.append(subtoken)
                subtoken = []
                self.next()
            else:
                char = self.current_char
                self.next()
                return [], IllegalCharError(char)
        if "." in self.text:
            return tokens, None
        else:
            return subtoken, None


# build up node for taking token values
class NumberNode:
    def __init__(self, token):
        self.token = token

    def __repr__(self):
        return f'{self.token}'


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

    def register(self, res):
        if isinstance(res, ParseResult):
            if res.error:
                self.error = res.error
            return res.node
        return res

    def success(self, node):
        self.node = node
        return self

    def failure(self, error):
        self.error = error
        return self


# build up parser
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
            res.register(self.next())
            return res.success(NumberNode(token))
        elif token.type == LPAREN:
            self.next()
            expression = self.expression()
            if self.current_token.type == RPAREN:
                self.next()
                return expression


    def term(self):
        res = ParseResult()
        left = res.register(self.factor())
        if res.error:
            return res

        while self.current_token.type in (MUL, DIV):
            op_token = self.current_token
            res.register(self.next())
            right = res.register(self.factor())
            if res.error:
                return res
            left = BinOpNode(left, op_token, right)
        return res.success(left)

    def expression(self):
        res = ParseResult()
        left = res.register(self.term())

        while self.current_token.type in (PLUS, MINUS):
            op_token = self.current_token
            res.register(self.next())
            right = res.register(self.term())
            if res.error:
                return res
            left = BinOpNode(left, op_token, right)
        return res.success(left)

    def computation(self):
        res = self.expression()
        return res

# build value class for interpreter
class Number:
    def __init__(self, value):
        self.value = value

    def add_to(self, other):
        if isinstance(other, Number):
            return Number(self.value + other.value)

    def sub_by(self, other):
        if isinstance(other, Number):
            return Number(self.value - other.value)

    def multi_by(self, other):
        if isinstance(other, Number):
            return Number(self.value * other.value)

    def div_by(self, other):
        if isinstance(other, Number):
            return Number(self.value / other.value)

    def __repr__(self):
        return str(self.value)


# build up interpreter
class Interpreter:
    def visit(self, node):
        #visit NumberNode
        #visit BinOpNOde
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.no_visit_method)
        return method(node)

    def no_visit_method(self, node):
        raise Exception(f'No visit_{type(node).__name__} method defined')

    def visit_NumberNode(self, node):
        return Number(node.token.value)

    def visit_BinOpNode(self, node):
        left = self.visit(node.left_node)
        right = self.visit(node.right_node)
        res = 0
        if node.op_token.type == PLUS:
            res = left.add_to(right)
        if node.op_token.type == MINUS:
            res = left.sub_by(right)
        if node.op_token.type == MUL:
            res = left.multi_by(right)
        if node.op_token.type == DIV:
            res = left.div_by(right)

        return res

def main(text):
    lexer = Lexer(text)
    tokens, error = lexer.make_tokens()
    if error:
        return None, error
    else:
        ast = []
        if all(isinstance(i, list) for i in tokens):
            for token in tokens:
                parser = Parser(token)
                ast.append(parser.computation())
        else:
            parser = Parser(tokens)
            ast = parser.computation()

        # return [i.node for i in ast], [i.error for i in ast]

        interpreter = Interpreter()
        res = [interpreter.visit(i.node) for i in ast]

        return res, [i.error for i in ast]
