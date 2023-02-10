class Variable:
    def __init__(self, name, address=int(0x0), version=int(-1)):
        self.name = name
        self.address = int(address)
        self.version = int(version)

    def clone(self):
        return Variable(self.name, self.address, self.version)

    def toString(self):
        res = "{}_{}".format(str(self.name), str(self.version))
        return res

    def equals(self, V):
        return (self.address == V.address) and (self.version == V.version)