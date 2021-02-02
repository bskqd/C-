class Employee:
    def __init__(self,a,y):
        self._a=a
        self._y=y
    
    def calculateSalary(self):
        S=self._y*100   
class Ing(Employee):
    def __init__(self,a,g,y):
        super().__init__(a,y)
        self._g=g
    def calculateSalary(self):
        return self._g*1000*(1+self._y/10) #1000-базовий оклад інженера(900-тест.,800-прац.кадрів)
class Test(Employee):
    def __init__(self,a,y):
        super().__init__(a,y)
    def calculateSalary(self):
        return 900*(1+(0.1)*(self._y/3))
class Kadr(Employee):
    def __init__(self,a,y):
        super().__init__(a,y)
    def calculateSalary(self):
        return 800*(1+self._y/5)

def q(fname):
    f=open(fname)
    d=[]
    S=0
    for line in f:
        if line.split()[0]=='Engineer:':
            r=Ing((line.split()[1]),int(line.split()[2]),int(line.split()[3]))
            d.append(r)
        elif line.split()[0]=='Intern:':
            w=Test((line.split()[1]),int(line.split()[2]))
            d.append(w)
        elif line.split()[0]=='Staff_worker:':
            t=Kadr((line.split()[1]),int(line.split()[2]))
            d.append(t)
    for i in d:
        S+=i.calculateSalary()
    print('загальну суму видатків по заробітній платі',S,'$')
    pros=(S*20)/100
    print('податок',pros,'$')
    print('загальну суму виплат працівникам компанії:',S-pros,'$')
    return ''
print(q("Файл"))
