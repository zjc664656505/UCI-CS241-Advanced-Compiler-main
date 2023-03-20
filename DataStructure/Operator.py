from DataStructure.Token import Token, TokenType
import enum


class OperatorCode(enum.Enum):
    # represent the operator code in hexidecimal format
    add = 0x1
    sub = 0x2
    mul = 0x3
    div = 0x4
    cmp = 0x5
    adda = 0x6
    load = 0x7
    store = 0x8
    move = 0xA
    phi = 11
    end = 0xC
    bra = 0xD
    bne = 0xE
    beq = 0xF
    ble = 0x10
    blt = 0x11
    bge = 0x12
    bgt = 0x13
    read = 0x14
    write = 0x15
    writeNL = 0x16
    const = 0x17


class Operator:
    arithmeticOperator = {TokenType.plusToken: OperatorCode.add, TokenType.minusToken: OperatorCode.sub,
                          TokenType.timesToken: OperatorCode.mul, TokenType.divToken: OperatorCode.div}

    relationOperator = {TokenType.eqlToken: OperatorCode.cmp, TokenType.neqToken: OperatorCode.cmp,
                        TokenType.lssToken: OperatorCode.cmp, TokenType.geqToken: OperatorCode.cmp,
                        TokenType.leqToken: OperatorCode.cmp, TokenType.gtrToken: OperatorCode.cmp}

    branchingOperator = {TokenType.eqlToken: OperatorCode.beq, TokenType.neqToken: OperatorCode.bne,
                         TokenType.lssToken: OperatorCode.blt, TokenType.leqToken: OperatorCode.ble,
                         TokenType.gtrToken: OperatorCode.bgt, TokenType.geqToken: OperatorCode.bge,
                         TokenType.thenToken: OperatorCode.bra, TokenType.doToken: OperatorCode.bra,
                         TokenType.callToken: OperatorCode.bra}

    assignmentOperator = {TokenType.letToken: OperatorCode.move, TokenType.becomesToken: OperatorCode.move,
                          TokenType.returnToken: OperatorCode.move}

    standardIoOperator = {"InputNum": OperatorCode.read, "OutputNum": OperatorCode.write,
                          "OutputNewLine": OperatorCode.writeNL}

    constOperator = {TokenType.number: OperatorCode.const}

    def __init__(self):
        pass

    def getToken(self, opToken: Token):
        try:
            token_type = Token.tokenValueMap[opToken.value]
        except KeyError:
            token_type = 'not in tokenValueMap'
        if token_type in self.arithmeticOperator:
            return self.arithmeticOperator[token_type]
        elif token_type in self.relationOperator:
            return self.relationOperator[token_type]
        elif token_type in self.assignmentOperator:
            return self.assignmentOperator[token_type]
        elif opToken.value in self.standardIoOperator:
            return self.standardIoOperator[opToken.value]
        elif opToken.checkSameType(TokenType.periodToken):
            return OperatorCode.end
        else:
            return None
