from DataStructure.DataResult.IResult import IResult
from DataStructure.DataResult.InstructionResult import InstructionResult

class RegisterResult(IResult):
    register = -1
    iid = -1
    def __int__(self, reg_num=-1, iid=-1):
        self.register = reg_num
        self.iid = iid

    def set(self, value):
        self.register = int(value)

    def setiid(self,iid):
        self.iid = iid

    def getiid(self):
        return self.iid

    def clone(self):
        register_res = RegisterResult()
        register_res.iid = self.iid
        register_res.register = self.register
        return register_res

    def equals(self, result):
        if isinstance(result, RegisterResult):
            return self.register == result.register
        return False

    def toInstruction(self):
        return InstructionResult(self.iid)

    def toString(self):
        return f"R{self.register}"