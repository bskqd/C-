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
m=[]
S=0
r=Ing('ghj',5,2)
m.append(r)
q=Test('ds',5)
m.append(q)
w=Kadr('bhjk',9)
m.append(w)
e=Ing('ghj',5,2)
m.append(e)
t=Test('ds',5)
m.append(t)
y=Kadr('bhjk',9)
m.append(y)
u=Ing('ghj',5,2)
m.append(u)
i=Test('ds',5)
m.append(i)
o=Kadr('bhjk',9)
m.append(o)
for i in m:
    S+=i.calculateSalary()
print('загальну суму видатків по заробітній платі',S,'$')
pros=(S*20)/100
print('податок',pros,'$')
print('загальну суму виплат працівникам компанії:',S-pros,'$')




