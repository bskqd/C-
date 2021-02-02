class MutableString:
    def __init__(self,s):
        self._s=list(s)
        
    def __len__(self):
        return len(self._s)
    
    def __str__(self):
        return str(self._s)
    
    def __contains__(self,i):
        return i in self._s

    
    def __getitem__(self, item):
        try:
            return self._s[item]
        except IndexError:
            pass
            
    

    def __setitem__(self, key, value):
        try:
            self._s[key] = value
        except IndexError:
            pass
        
    def __add__(self, other):
        return MutableString(self._s+other)

    def __mul__(self, other):
        return MutableString(self._s*int(other))

s = ''

def q(fname):
    global s
    f = open(fname)
    for line in f:
        ms = MutableString(line)
        for i in range(len(ms)):
            if ms[i] == 'i':
                ms[i] = 'і'
                s += ms[i]
            elif ms[i] == 'p':
                ms[i] = 'р'
                s += ms[i]
            elif ms[i] == 'c':
                ms[i] = 'с'
                s += ms[i]
            elif ms[i] == 'o':
                ms[i] = 'о'
                s += ms[i]
            elif ms[i] == 'H':
                ms[i] = 'Н'
                s += ms[i]
            elif ms[i] == 'a':
                ms[i] = 'а'
                s += ms[i]
            elif ms[i] == 'A':
                ms[i] = 'А'
                s += ms[i]
            elif ms[i] == 'E':
                ms[i] = 'Е'
                s += ms[i]
            elif ms[i] == 'e':
                ms[i] = 'е'
                s += ms[i]
            elif ms[i] == 'T':
                ms[i] = 'Т'
                s += ms[i]
            elif ms[i] == 'K':
                ms[i] = 'К'
                s += ms[i]
            elif ms[i] == 'x':
                ms[i] = 'х'
                s += ms[i]
            elif ms[i] == 'X':
                ms[i] = 'Х'
                s += ms[i]
            elif ms[i] == 'C':
                ms[i] = 'С'
                s += ms[i]
            elif ms[i] == 'P':
                ms[i] = 'Р'
                s += ms[i]
            elif ms[i] == 'O':
                ms[i] = 'О'
                s += ms[i]
            elif ms[i] == 'B':
                ms[i] = 'В'
                s += ms[i]
            elif ms[i] == 'M':
                ms[i] = 'М'
                s += ms[i]
            else:
                s += ms[i]
    f.close()
    f=open(fname,'wt')
    f.write(s)
    f.close()
print(q('lab5.txt'))

# якщо треба підрахувати з пробілами 
def w(fname):
    f=open(fname)
    l=''
    r=0
    for line in f:
        r+=1
        for i in line:
            l+=i
        
    if r==1:
        return  len(l)
    else:
        return len(l)-r+1  
    f.close()
print(w('lab5.txt'))

# якщо треба підрахувати без пробілів:
def e(fname):
    f=open(fname)
    l=''
    r=0 
    for line in f:
        r+=1
        for i in line:
            if i==' ':
                l==l
            else:
                l+=i
    if r==1:
        return  len(l),r
    else:
        return len(l)-r+1
    f.close()
print(e('lab5.txt'))
