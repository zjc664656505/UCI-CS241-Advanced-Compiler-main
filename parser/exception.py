class illegalTokenException(Exception):
    def __init__(self,message):
        super().__init__(message)

class illegalVariableException(Exception):
    def __init__(self,message):
        super().__init__(message)

class incorrectSyntaxException(Exception):
    def __init__(self,message):
        super().__init__(message)
