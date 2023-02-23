from DataStructure.Token import TokenType
from DataStructure.Token import Token
from util.Constants import Constants
import traceback
import sys
from parser.exception import illegalTokenException, illegalVariableException, incorrectSyntaxException


class Tokenizer:
    def __init__(self, fileName):
        self.reader = FileReader(fileName)
        self.inputSym = self.reader.getSym()
        self.prevToken = None
        self.errorFlag = False
        self.currentString = ""
        self.identAddrCounter = Constants.SCANNER_IDENTIFIER_ADDRESS_OFFSET
        self.scannerState = {"stop": 0,
                             "start": 1,
                             "relop": 2,
                             "digit": 3,
                             "letter": 4}
        self.ident2Addr = {}
        self.addr2Ident = {}

    def next(self):
        self.inputSym = self.reader.getSym()

    def nextLine(self):
        self.reader.nextLine()

    def add2String(self):
        self.currentString = self.currentString + self.inputSym

    def error(self, exception):
        self.reader.error(exception)

    def getSym(self):
        if self.prevToken is not None and self.prevToken.checkSameType(TokenType.eofToken):
            return self.prevToken
        self.runStateMachine()
        token = Token.getToken(self.currentString)
        print(f"Token value: {token.value}, Token Id: {token.id}, Token Type: {token.type}")
        if self.errorFlag or token.checkSameType(TokenType.errorToken):
            self.error(illegalTokenException("Token is illegal" + self.currentString))
            sys.exit(1)
        if token.checkSameType(TokenType.ident):
            if token.value not in self.ident2Addr:
                self.ident2Addr[token.value] = self.identAddrCounter
                self.addr2Ident[self.identAddrCounter] = token.value
                # Comment out ident2AddrCounter to make all variables point to the same address
                self.identAddrCounter += 1
        self.prevToken = token
        return token

    def runStateMachine(self):
        state = self.scannerState['start']
        self.currentString = ''
        while state != self.scannerState["stop"]:
            if state == self.scannerState['start']:
                if self.inputSym == '#':
                    self.nextLine()
                    self.next()
                elif self.inputSym == " " or self.inputSym == "\t" or self.inputSym == "\r" or self.inputSym == "\n":
                    if len(self.currentString) > 0 and self.currentString in Token.tokenValueMap:
                        state = self.scannerState["stop"]
                    elif state == self.scannerState['digit'] or state == self.scannerState['letter'] or \
                            state == self.scannerState['relop']:
                        state = self.scannerState['stop']
                        self.errorFlag = True
                    self.next()
                elif self.inputSym in Token.tokenValueMap:
                    self.add2String()
                    if self.inputSym == "":
                        state = self.scannerState['stop']
                    elif self.inputSym == "=" or self.inputSym == "!" or \
                            self.inputSym == ">" or self.inputSym == "<":
                        state = self.scannerState["relop"]
                        self.next()
                    elif self.inputSym == "/":
                        self.next()
                        if self.inputSym == "/":
                            self.currentString = ""
                            self.nextLine()
                            self.next()
                        else:
                            state = self.scannerState["stop"]
                    else:
                        state = self.scannerState["stop"]
                        self.next()
                elif self.inputSym.isdigit():
                    self.add2String()
                    state = self.scannerState["digit"]
                    self.next()
                elif self.inputSym.isalpha():
                    self.add2String()
                    state = self.scannerState['letter']
                    self.next()
            elif state == self.scannerState['relop']:
                state = self.scannerState['stop']
                if self.inputSym == "=" or self.inputSym == "-":
                    self.add2String()
                    self.next()
            elif state == self.scannerState['digit']:
                if self.inputSym.isdigit():
                    self.add2String()
                    self.next()
                else:
                    state = self.scannerState['stop']
            elif state == self.scannerState['letter']:
                if self.inputSym.isdigit() or self.inputSym.isalpha():
                    self.add2String()
                    self.next()
                else:
                    state = self.scannerState["stop"]
            else:
                state = self.scannerState['stop']


class FileReader:
    def __init__(self, fileName: str):

        self.fileName = fileName
        self.line = None
        self.lineNo = 0
        self.charPosition = 0
        try:
            self.file = open(fileName, 'r')
        except Exception as ex:
            self.error(ex)
            sys.exit(1)

    def nextLine(self):
        try:
            self.line = self.file.readline()
            self.lineNo += 1
            self.charPosition = 0
            while (self.line != '') and (len(self.line.strip()) == 0):
                self.line = self.file.readline()
                self.lineNo += 1
            self.line = self.line.strip()
        except Exception as ex:
            self.error(ex)
            sys.exit(1)

    def getSym(self):
        if (self.line != '') and (self.line is not None) and (self.charPosition < len(self.line)):
            self.charPosition += 1
            return self.line[self.charPosition - 1]
        elif (self.line != '') and (self.line is not None):
            self.nextLine()
            return '\n'
        elif self.line is None:
            self.nextLine()
            return self.getSym()
        else:
            return ''

    def error(self, exception):
        print('Exception while parsing file: ' + self.fileName + ' at line: ' +
              str(self.lineNo) + ' column: ' + str(self.charPosition))
        print("".join(traceback.TracebackException.from_exception(exception).format()))
        sys.exit(-1)
