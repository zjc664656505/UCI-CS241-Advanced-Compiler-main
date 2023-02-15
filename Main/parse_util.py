from DataStructure.Token import TokenType
from DataStructure.Token import Token

import traceback
import sys






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

