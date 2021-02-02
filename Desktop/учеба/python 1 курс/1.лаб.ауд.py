class QE:
    def __init__(self,a,b=0,c=0):
        if not isinstance(a,QE):
            assert a!=0
            self._a=a
            self._b=b
            self._c=c
        else:
            self._a=a._a
            self._b=a._b
            self._c=a._c

    def d(self):
        return self._b**2-4*self._a*self._c

    def solve(self):
        d=self.d()
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

eq=QE(2,4,5)
eq1=QE(eq)
eq1._c=-1
print(eq1.solve())
print(eq.solve())

    
