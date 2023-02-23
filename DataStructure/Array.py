from DataStructure.Variable import Variable

class Array(Variable):
    def __init__(self, name=None, address=0x0, version=1, dimensionList=None):
        super().__init__(name, address, version)
        self.name = name
        self.address = address
        self.version = version
        self.dimensionList = dimensionList
        if dimensionList:
            # define temperal arraysize = 4.
            self.arraysize = 4
            for i in dimensionList:
                self.arraysize = self.arraysize*i
        else:
            self.arraysize = 0

        self.index_list = []
        self.array_addr = 0x0

    def getBaseAddress(self):
        return Variable(self.name, self.address, self.version)

    def getElementAddress(self, index_list):
        element_address = self.address
        element_idx = ""
        for index in index_list:
            element_address = element_address + index*4
            element_idx = '[' + str(index) + ']'
        return Variable(f"{self.name}-{element_idx}", element_address, self.version)

    def clone(self):
        arr = Array(self.name, self.address, self.version)
        arr.array_addr = self.array_addr
        arr.arraySize = self.arraysize
        arr.index_list = []
        for i in self.index_list:
            arr.index_list.append(i.clone())

        arr.dimensionList = []
        if self.dimensionList:
            for i in self.dimensionList:
                arr.dimensionList.append(i)

    def toString(self):
        return f"{self.name}: {self.version}"