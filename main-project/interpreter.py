from tokenizer import *

def run_interpreter(text):
    tokenizer = Lexer(text)
    tokens, error = tokenizer.make_tokens()
    if error:
        print(error)
    else:
        print(tokens)

if __name__ == "__main__":
    text = input()
    run_interpreter(text)