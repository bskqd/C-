class Computer:
    computer = 'Simple'
    window = 'What window?'

    def __init__(self, st, lap_koc):
        self.st = list(st)
        self.lap = self.Laptop(lap_koc)

    def __getitem__(self, item):
        try:
            return self.st[item]
        except IndexError:
            return 'getter raised IndexError, index is out of range'

    def __setitem__(self, key, value):
        try:
            self.st[key] = value
        except IndexError:
            return 'setter raised IndexError is raised, index out of range'

    class Laptop:
        def __init__(self, lap_koc):
            cpu = 8
            self.koc = lap_koc


class SubClassForComp(Computer):
    def __init__(self, st, lap_koc):
        super(SubClassForComp, self).__init__(st, lap_koc)

    def show(self):
        return self.st


com = Computer('STB', 8)
print(com.computer, com.window, com.st)
com.st[2] = 4
print(com.st)
lap = com.lap
print(lap.koc)
com_inh = SubClassForComp('TCP', 9)
print(com_inh.show())
lap_inh = com_inh.lap
print(lap_inh.koc)
