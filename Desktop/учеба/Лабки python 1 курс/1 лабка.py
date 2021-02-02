import math
class Tetraedr:
    def __init__(self,a):
        assert a!=0
        self._a=a

    def sb(self):
        return (3*(self._a**2)*(3**0.5))/4

    def v(self):
        return (self._a**2)/(6*(2**0.5))


class Chotpir:
    def __init__(self,a,b,c,d,l,h,H):
        assert a!=0 and b!=0 and c!=0 and d!=0 and l!=0 and h!=0 and H!=0
        self._a=a
        self._b=b
        self._c=c
        self._d=d
        self._l=l
        self._h=h
        self._H=H

    def sb(self):
        return ((self._a+self._b+self._c+self._d)/2)*self._l

    def so(self):
        if self._a==self._b==self._c==self._d==self._h:
            return (self._a)**2
        elif self._a==self._b==self._c==self._d!=self._h:
            return self._a*self._h
        elif (self._a==self._b and self._c==self._d and (self._a==self._b==self._h or self._c==self._d==self._h)) or (self._a==self._c and self._b==self._d and (self._a==self._c==self._h or self._b==self._d==self._h)) or (self._a==self._d and self._b==self._c and (self._a==self._d==self._h or self._b==self._c==self._h)):
            return self._a*self._h
        elif ((self._a==self._b!=self._h) and (self._c==self._d!=self._h)) or ((self._a==self._c!=self._h) and (self._b==self._d!=self._h)) or ((self._c==self._b!=self._h) and (self._a==self._d!=self._h)):
            return self._a*self._h
        else:
            return ((self._a+self._b)/2)*self._h #a,b-основи

    def v(self):
        so=self.so()
        return (so*self._H)/3


class Nechotpir:
    def __init__(self,a,b,c,d,e,f,g,k,l,h,h1,H):
        assert a!=0 and b!=0 and c!=0 and d!=0 and l!=0 and h!=0 and H!=0 and e!=0 and f!=0 and g!=0 and k!=0 and h1!=0
        self._a=a
        self._b=b
        self._c=c
        self._d=d
        self._l=l
        self._h=h
        self._H=H
        self._e=e
        self._f=f
        self._g=g
        self._k=k
        self._h1=h1

    def sb(self):
        return (((self._a+self._b+self._c+self._d)+(self._e+self._f+self._g+self._k))/2)*self._l

    def so(self):
        if self._a==self._b==self._c==self._d==self._h:
            return (self._a)**2
        elif self._a==self._b==self._c==self._d!=self._h:
            return self._a*self._h
        elif (self._a==self._b and self._c==self._d and (self._a==self._b==self._h or self._c==self._d==self._h)) or (self._a==self._c and self._b==self._d and (self._a==self._c==self._h or self._b==self._d==self._h)) or (self._a==self._d and self._b==self._c and (self._a==self._d==self._h or self._b==self._c==self._h)):
            return self._a*self._h
        elif ((self._a==self._b!=self._h) and (self._c==self._d!=self._h)) or ((self._a==self._c!=self._h) and (self._b==self._d!=self._h)) or ((self._c==self._b!=self._h) and (self._a==self._d!=self._h)):
            return self._a*self._h
        else:
            return ((self._a+self._b)/2)*self._h #a,b-основи

    def so2(self):
        if self._e==self._f==self._g==self._k==self._h1:
            return (self._e)**2
        elif self._e==self._f==self._g==self._k!=self._h1:
            return self._e*self._h1
        elif (self._e==self._f and self._g==self._k and (self._e==self._f==self._h1 or self._g==self._k==self._h1)) or (self._e==self._g and self._f==self._k and (self._e==self._g==self._h1 or self._f==self._k==self._h1)) or (self._e==self._k and self._f==self._g and (self._e==self._k==self._h1 or self._f==self._g==self._h1)):
            return self._e*self._h1
        elif ((self._e==self._f!=self._h1) and (self._g==self._k!=self._h1)) or ((self._e==self._g!=self._h1) and (self._f==self._k!=self._h1)) or ((self._g==self._f!=self._h1) and (self._e==self._k!=self._h1)):
            return self._e*self._h1
        else:
            return ((self._e+self._f)/2)*self._h1 #a,b-основи
        

    def v(self):
        so=self.so()
        so2=self.so2()
        return (self._H*(so+(so*so2)**0.5+so2))/3

class Kulya:
    def __init__(self,R):
        assert R!=0
        self._R=R

    def sb(self):
        return 4*(math.pi)*self._R**2

    def v(self):
        return (4*(math.pi)*self._R**3)/3

def q(fname):
    obemi=[]
    bploshi=[]
    obemi_o=[]
    bploshi_o=[]
    max_sb=0
    max_v=0 
    max_sb_o=0
    max_v_o=0
    f=open(fname)
    for line in f:
        if line.split()[0]=='tr':
            a=Tetraedr(int(line.split()[1]))
            obemi.append(a.v())
            bploshi.append(a.sb())
            obemi_o.append('Tetraedr')
            bploshi_o.append('Tetraedr')
        elif line.split()[0]=='chp':
            a=Chotpir(int(line.split()[1]),int(line.split()[2]),int(line.split()[3]),int(line.split()[4]),int(line.split()[5]),int(line.split()[6]),int(line.split()[7]))
            obemi.append(a.v())
            obemi_o.append('Чотирикутна піраміда')
            bploshi_o.append('Чотирикутна піраміда')
            bploshi.append(a.sb())
        elif line.split()[0]=='nchp':
            a=Nechotpir(int(line.split()[1]),int(line.split()[2]),int(line.split()[3]),int(line.split()[4]),int(line.split()[5]),int(line.split()[6]),int(line.split()[7]),int(line.split()[8]),int(line.split()[9]),int(line.split()[10]),int(line.split()[11]),int(line.split()[12]))
            obemi.append(a.v())
            bploshi.append(a.sb())
            obemi_o.append('Зрізана піраміда')
            bploshi_o.append('Зрізана піраміда')
        elif line.split()[0]=='kl':
            a=Kulya(int(line.split()[1]))
            obemi.append(a.v())
            bploshi.append(a.sb())
            obemi_o.append('Куля')
            bploshi_o.append('Куля')
    for el in range(len(obemi)):
        if obemi[el]>max_v:
            max_v=obemi[el]
            max_v_o=obemi_o[el]
    for el in range(len(bploshi)):
        if bploshi[el]>max_sb:
            max_sb=bploshi[el]
            max_sb_o=bploshi_o[el]
    f.close()
    return 'Найбільший об’єм у',max_v_o,max_v,'Найбільша бічна площа у',max_sb_o,max_sb      
            
        

print(q('C:\\Users\\Богдан\\Desktop\\python\\1.lab.txt'))
