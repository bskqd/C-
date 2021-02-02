def nadslovo(fname):
    f=open(fname)
    a=0
    x=''
    for line in f:
        for el in line.split():
            if len(el)>a:
                a=len(el)
                x=el
    print(x)
    f.close
def kilsliv(fname):
    f=open(fname)
    kil=0
    for line in f:
        for el in line.split():
            kil+=1
    print(kil)
    f.close
def delete(fname):
    f=open(fname)
    s=''
    for line in f:
        for el in line.split():
            if len(el)>2:
                s+=el
    print(s)
    f.close
def propuski(fname):
    f=open(fname)
    l=[]
    for line in f:
        s=''
        for el in line.split():
            s+=el
        l.append(s)
    f.close
    f=open(fname,'w')
    for i in l:
        f.write(i)

propuski("C:\\Users\\Богдан\\Desktop\\python\\t.13_7.txt")
