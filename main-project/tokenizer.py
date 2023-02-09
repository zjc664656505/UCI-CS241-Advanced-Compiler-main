import string

# define global digit constants
DIGIT = '0123456789'
LETTERS = string.ascii_letters
LETTERS_DIGITS = LETTERS + DIGIT
RELOP = "RELOP" #RELOPS = ["<", "<=", "==", "!=", ">", ">="]

# define global variable for the token type
INT = 'INT'
PLUS = 'ADD'
MINUS = 'SUB'
MUL = 'MUL'
DIV = 'DIV'
LPAREN = 'LPAREN'
RPAREN = 'RPAREN'
EQ = 'EQ'
IDENTIFIER = 'IDENTIFIER'
KEYWORD = 'KEYWORD'
KEYWORDS = ['var', 'AND', 'OR', 'let', 'array', 'main', 'if',
            'then', 'else', 'fi', 'while', 'do', 'od', 'return']
CONTROL_SYMBOL = ['.', ',', ';', '{', '}']



# build up token class
class Token:
    def __init__(self, type_, value=None):
        self.type = type_
        self.value = value

    def matches(self, type_, value):
        return self.type == type_ and self.value == value

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

    def make_identifier(self):
        identifier_str = ''
        while self.current_char != None and self.current_char in LETTERS_DIGITS:
            identifier_str += self.current_char
            self.next()

        token_type = KEYWORD if identifier_str in KEYWORDS else IDENTIFIER
        return Token(token_type, identifier_str)

    def make_less_than(self):
        token_type = RELOP
        relop_str = self.current_char
        self.next()
        if self.current_char == "=":
            relop_str += self.current_char
            self.next()
            return Token(token_type, relop_str)

        elif self.current_char == "-":
            self.next()
            token_type = EQ
            return Token(token_type)

        return Token(token_type, relop_str)

    def make_greater_than(self):
        token_type = RELOP
        relop_str = self.current_char
        self.next()

        if self.current_char == "=":
            relop_str += self.current_char
            self.next()
            return Token(token_type, relop_str)

        return Token(token_type, relop_str)

    def make_equal(self):
        token_type = RELOP
        relop_str = self.current_char
        self.next()

        if self.current_char == "=":
            relop_str += self.current_char
            self.next()
            return Token(token_type, relop_str)
        self.next()
        return None, IllegalCharError(self.current_char)

    def make_not_equal(self):
        token_type = RELOP
        relop_str = self.current_char
        self.next()
        if self.current_char == "=":
            relop_str += self.current_char
            self.next()
            return Token(token_type, relop_str)
        self.next()
        return None, IllegalCharError(self.current_char)

    def make_tokens(self):
        tokens = []
        subtoken = []

        while self.current_char != None:
            if self.current_char in ' \t':
                self.next()
            elif self.current_char in DIGIT:
                subtoken.append(self.make_number())
            elif self.current_char in LETTERS:
                subtoken.append(self.make_identifier())
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
            elif self.current_char == '<':
                subtoken.append(self.make_less_than())
                # self.next()
            elif self.current_char == '>':
                subtoken.append(self.make_greater_than())
            elif self.current_char == '!':
                subtoken.append(self.make_not_equal())
            elif self.current_char == "=":
                subtoken.append(self.make_equal())
            elif self.current_char == '(':
                subtoken.append(Token(LPAREN))
                self.next()
            elif self.current_char == ')':
                subtoken.append(Token(RPAREN))
                self.next()
            # elif self.current_char == "." or self.current_char == ";":
            #     tokens.append(subtoken)
            #     subtoken = []
            #     self.next()
            else:
                char = self.current_char
                self.next()
                return [], IllegalCharError(char)
        # if "." in self.text or ";" in self.text:
        #     return tokens, None
        # else:
        return subtoken, None