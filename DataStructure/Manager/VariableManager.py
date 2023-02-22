from DataStructure.Array import Array
from util.Constants import Constants
from DataStructure.Variable import Variable

class VariableManager:
    def __init__(self):
        self.varibles = set()
        self.ssaMap = {}
        self.arrays = {}
        self.arrayAddress = Constants.ARRAY_ADDRESS_OFFSET

    def addVariable(self, variable):
        if variable in self.varibles:
            print("VARIABLE ALREADY EXISTED.")
        else:
            self.varibles.add(variable)

    def getVariable(self):
        return self.varibles

    def isVariable(self, variable):
        if isinstance(variable, Variable):
            var = variable.address
        elif isinstance(variable, int):
            var = variable
        else:
            return False
        return var in self.varibles

    def addArray(self, variable, arrayvar):
        if variable in self.varibles:
            print("VARIABLE AREALDY EXISTED.")
        else:
            arrayvar.array_addr = self.arrayAddress
            #print(f"Arrayaddress: {self.arrayAddress}, ArraySize {arrayvar.arraysize}")
            self.arrayAddress = int(self.arrayAddress) + int(arrayvar.arraysize)

            self.arrays[variable] = arrayvar
            self.varibles.add(variable)

    def isArray(self, variable):
        if variable in self.varibles:
            return variable in self.arrays.keys()
        return False

    def getArray(self, variable):
        return self.arrays[variable]

    def updatessamap(self, variable, version):
        self.ssaMap[variable] = version

    def setssamap(self, restoressa):
        self.ssaMap.clear()
        self.ssaMap.update(restoressa.copy())


    def getssaversion(self, variable):
        if variable in self.ssaMap:
            return self.ssaMap[variable]
        return -1

    def copyssato(self, to):
        to.ssaMap.update(self.ssaMap.copy())
