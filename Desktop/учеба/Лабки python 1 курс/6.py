class MutableString:
    def __init__(self, s):
        self._s = list(s)
        self.cursor = 0

    def __len__(self):
        return len(self._s)

    def __str__(self):
        return str(self._s)

    def __contains__(self, i):
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
        return MutableString(self._s + other)

    def __mul__(self, other):
        return MutableString(self._s * int(other))

    def __next__(self):
        try:
            element = self._s[self.cursor]
            self.cursor += 1
            return element
        except IndexError:
            raise StopIteration

    def __iter__(self):
        return MutableString(self._s)




s = ''

def q(fname):
    global s
    f=open(fname)
    for line in f:
        ms=MutableString(line)
        for i in ms:
            if i == 'i':
                i = 'і'
                s += i
            elif i == 'p':
                i = 'р'
                s += i
            elif i == 'c':
                i = 'с'
                s += i
            elif i == 'o':
                i = 'о'
                s += i
            elif i == 'H':
                i = 'Н'
                s += i
            elif i == 'a':
                i = 'а'
                s += i
            elif i == 'A':
                i = 'А'
                s += i
            elif i == 'E':
                i = 'Е'
                s += i
            elif i == 'e':
                i = 'е'
                s += i
            elif i == 'T':
                i = 'Т'
                s += i
            elif i == 'K':
                i = 'К'
                s += i
            elif i == 'x':
                i = 'х'
                s += i
            elif i == 'X':
                i = 'Х'
                s += i
            elif i == 'C':
                i = 'С'
                s += i
            elif i == 'P':
                i = 'Р'
                s += i
            elif i == 'O':
                i = 'О'
                s += i
            elif i == 'B':
                i = 'В'
                s += i
            elif i == 'M':
                i = 'М'
                s += i
            else:
                s += i
    f.close()
    f=open(fname,'wt')
    f.write(s)
    f.close()
print(q('lab6.txt'))

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
print(w('lab6.txt'))

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
        return  len(l)
    else:
        return len(l)-r+1
    f.close()
print(e('lab6.txt'))

