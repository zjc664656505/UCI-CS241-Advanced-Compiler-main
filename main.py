from DataStructure.Operator import OperatorCode, Operator
from DataStructure.Token import Token, TokenType
from DataStructure.Variable import Variable
from parser.parse_util import Tokenizer
from parser.Parser import Parser
from DataStructure.Dom.DominantTree import DomNodeCSE, DominantTreeNode





file_dir = "./test/sample_test.txt"
# tokenize = Tokenizer(file_dir)
# sym = tokenize.getSym()
parse = Parser(file_dir)
parse.run_parser()
