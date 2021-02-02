class MutableString:
    def __init__(self,s):
        self._s=s
        self._cursor=0
        
    def __len__(self):
        return len(self._s)
    
    def __str__(self):
        return str(self._s)
    
    def __contains__(self,i):
        return i in self._s

    def __next__(self):
        try:
            i=self._s[self._cursor]
            if i==ord('i'):
                i=chr('і')
                self._cursor+=1
            elif i==ord('p'):
                i==chr('р')
                self._cursor+=1
            elif i==ord('c'):
                i==chr('с')
                self._cursor+=1
            elif i==ord('o'):
                i==chr('о')
                self._cursor+=1
            elif i==ord('H'):
                i==chr('Н')
                self._cursor+=1
            elif i==ord('a'):
                i==chr('а')
                self._cursor+=1
            elif i==ord('A'):
                i==chr('А')
                self._cursor+=1
            elif i==ord('E'):
                i==chr('Е')
                self._cursor+=1
            elif i==ord('e'):
                i==chr('е')
                self._cursor+=1
            elif i==ord('T'):
                i==chr('Т')
                self._cursor+=1
            elif i==ord('K'):
                i==chr('К')
                self._cursor+=1
            elif i==ord('x'):
                i==chr('х')
                self._cursor+=1
            elif i==ord('X'):
                i==chr('Х')
                self._cursor+=1
            elif i==ord('C'):
                i==chr('С')
                self._cursor+=1
            elif i==ord('P'):
                i==chr('Р')
                self._cursor+=1
            elif i==ord('O'):
                i==chr('О')
                self._cursor+=1
            elif i==ord('B'):
                i==chr('В')
                self._cursor+=1
            elif i==ord('M'):
                i==chr('М')
                self._cursor+=1
            else:
                self._cursor+=1
            return i
        except IndexError:
            raise StopIteration

    def __getitem__(self):
        return self._s[item]

    def __add__(self, other):
        return MutableString(self._s+other)

    def __mul__(self, other):
        return MutableString(self._s*int(other))

    def __iter__(self):
        return MutableString(self._s)



q=MutableString('dacs')
print((q)*('2'))


def q(fname):
    f=open(fname)
    l=''
    for line in f:
        line=MutableString(line)
        for i in line:
            l+=i
    f.close()
    f=open(fname,'wt')
    f.write(l)
    f.close()
print(q('C:\\Users\\Богдан\\Desktop\\python\\fg.txt'))
