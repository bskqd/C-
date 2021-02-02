class EQ:
    def init(self,b,c):
        self._b=b
        self._c=c
    def solve(self):
        if self._b==0 and self._c==0:
            return ('R')
        elif self._b==0 and self._c!=0:
            return ()
        else:
            return (-self._c)/self._b
class QE(EQ):
    def init(self,a,b,c):
        super().init(b,c)
        self._a=a
    def d(self):
        return self._b**2-4*self._a*self._c
    def solve(self):
        d=self.d()
        if self._a==0:
            return super().solve()
        else:
            if d<0:
                return ()
            elif d==0:
                x1=-self._b/(2*self._a)
                return(x1,) #кома для того, щоб показати список
            else:
                d=d**0.5
                x1=(-self._b-d)/(2*self._a)
                x2=(-self._b+d)/(2*self._a)
                return (x1,x2)
class BQE(QE):
    def init(self,a,b,c):
        super().init(a,b,c)
    def solve(self):
        m=[]
        sol=super().solve()
        for i in sol:
            if i<0:
                pass
            elif i==0:
                m.append(i)
            else:
                m.append(i**0.5)
                m.append(-i**0.5)
        return m
qe=BQE(1,-5,-36)
print(qe.solve())
