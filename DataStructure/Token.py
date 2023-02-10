import enum
import re


class Tuple:
    def __init__(self, X, Y):
        self.X = X
        self.Y = Y


# define TokenType class which uses enum package to map class variable to specific memory address
# enum object has 2 variables: name and value. For example, TokenType.errorToken.name -> errorToken and
# TokenType.errorToken.name -> 0x0.
class TokenType(enum.Enum):
    errorToken = 0x0  # ("", 0x0)

    timesToken = 0x1  # ("*", 0x1)
    divToken = 0x2  # ("/", 0x2)

    plusToken = 0x10  # ("+",0x10)
    minusToken = 0x11  # ("-" 0x11)

    eqlToken = 0x20  # ("==",0x20)
    neqToken = 0x21  # ("!=",0x21)
    lssToken = 0x22  # ("<",0x22)
    gtrToken = 0x23  # (">",0x23)
    leqToken = 0x24  # ("<=",0x24)
    geqToken = 0x25  # (">=",0x25)

    periodToken = 0x30  # (".", 0x30)
    commaToken = 0x31  # (",", 0x31)
    openbracketToken = 0x32  # ("[", 0x32)
    closebracketToken = 0x33  # ("]", 0x34)
    openparenToken = 0x35  # ("(",0x35)
    closeparenToken = 0x36  # (")", 0x36)
    beginToken = 0x37  # ("{",0x37)
    endToken = 0x38  # ("}",0x38)
    returnToken = 0x39  # ("return",0x39)

    becomesToken = 0x40  # ("<-", 0x40)
    letToken = 0x42  # ("let",0x42)

    ifToken = 0x50  # ("if", 0x50)
    fiToken = 0x51  # ("fi", 0x51)
    elseToken = 0x52  # ("else", 0x52)
    thenToken = 0x53  # ("then",0x53)

    doToken = 0x60  # ("do",0x40)
    odToken = 0x61  # ("od",0x41)
    whileToken = 0x63  # ("while", 0x43)

    semiToken = 0x70  # (";", 0x70)
    callToken = 0x71  # ("call", 0x71)
    funcToken = 0x72  # ("function", 0x72)
    voidToken = 0x73  # ("void", 0x73)

    number = 0x80  # ("", 0x80)
    ident = 0x81  # ("", 0x81)
    varToken = 0x82  # ("var", 0x82)
    arrToken = 0x83  # ("array", 0x83)
    sequalToken = 0x84  # ("=", 0x84)
    exclaimToken = 0x85  # ("!", 0x85)

    mainToken = 0x90  # ('main' 0x90)
    eofToken = 0x91  # ('' empty string, 0x91)

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_


class Token:
    tokenValueMap = {
        "*": TokenType.timesToken,
        "/": TokenType.divToken,
        "+": TokenType.plusToken,
        "-": TokenType.minusToken,
        "=": TokenType.sequalToken,
        "==": TokenType.eqlToken,
        "!": TokenType.exclaimToken,
        "!=": TokenType.neqToken,
        "<": TokenType.lssToken,
        ">=": TokenType.geqToken,
        "<=": TokenType.leqToken,
        ">": TokenType.gtrToken,
        ".": TokenType.periodToken,
        ",": TokenType.commaToken,
        "[": TokenType.openbracketToken,
        "]": TokenType.closebracketToken,
        ")": TokenType.closeparenToken,
        "(": TokenType.openparenToken,
        "<-": TokenType.becomesToken,
        "then": TokenType.thenToken,
        "do": TokenType.doToken,
        ";": TokenType.semiToken,
        "}": TokenType.endToken,
        "od": TokenType.odToken,
        "fi": TokenType.fiToken,
        "else": TokenType.elseToken,
        "let": TokenType.letToken,
        "call": TokenType.callToken,
        "if": TokenType.ifToken,
        "while": TokenType.whileToken,
        "return": TokenType.returnToken,
        "var": TokenType.varToken,
        "array": TokenType.arrToken,
        "function": TokenType.funcToken,
        "void": TokenType.voidToken,
        "{": TokenType.beginToken,
        "main": TokenType.mainToken,
        "": TokenType.eofToken
    }

    def __init__(self, value, type, id):
        # value -> the token character
        # type -> the token type such as the divtoken, etc.
        # id -> the token id such as 0x0, etc.
        self.value = value
        self.type = type
        self.id = id

    @classmethod
    def getToken(cls, tokenChars):
        if tokenChars in cls.tokenValueMap:
            return cls(tokenChars, cls.tokenValueMap[tokenChars].name,
                       cls.tokenValueMap[tokenChars].value)
        else:
            expr1 = re.compile('[0-9]+')
            expr2 = re.compile("[a-zA-Z]([a-zA-Z0-9])*")
            if expr1.match(tokenChars):
                return cls(tokenChars, TokenType.number.name, TokenType.number.value)
            elif expr2.match(tokenChars):
                return cls(tokenChars, TokenType.ident.name, TokenType.ident.value)
            else:
                print(f"TokenError: {tokenChars}")
                return cls(tokenChars, TokenType.errorToken.name, TokenType.errorToken.value)

    def clone(self):
        return Token(self.value, self.type, self.id)

    def checkSameType(self, char):
        return char.name == self.type

    def toString(self):
        return f"{self.value}, {self.id}"

    def checkTerm(self):
        return 0x0 < self.id < 0x10

    def checkExpression(self):
        return 0x10 <= self.id < 0x20

    def checkRelation(self):
        return 0x20 <= self.id <0x30

    def compareToken(self, token):
        return token.value == self.value and token.name == self.name

    def checkTokenKey(self, token):
        return token in self.tokenValueMap




