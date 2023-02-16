from DataStructure.Operator import OperatorCode, Operator
from DataStructure.Token import Token, TokenType
from DataStructure.Variable import Variable
from parser.parse_util import Tokenizer

file_dir = "./test/sample_test.txt"
tokenize = Tokenizer(file_dir)
sym = tokenize.getSym()

