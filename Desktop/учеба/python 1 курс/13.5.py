#'C:\\Users\\Богдан\\Desktop\\python\\t.13_5.txt')
def parniv(fname):
    f=open(fname)
    sum=0
    for line in f:
        for el in line.split():
            if int(el)%2==0:
                sum+=1
    print(sum)
    f.close()
def kvadrat(fname):
    f=open(fname)
    sum=0
    for line in f:
        for el in line.split():
            if int(el)%2!=0 and ((int(el))**0.5)==(int((int(el))**0.5)):
                sum+=1
    print(sum)
    f.close()
def rizn(fname):
    f=open(fname)
    rizn=0
    mx=0
    mn=1352631643163613613463567316137371373575274572643513646265423
    for line in f:
        for el in line.split():
            if mx<int(el):
                mx=int(el)
            elif mn>int(el):
                mn=int(el)
    x=mx-mn
    print(x)
    f.close
def napos(fname):
    f=open(fname)
    suma=0
    a=-134123532151436436136436342673486903880345386936234692367
    for line in f:
        for el in line.split():
            if int(el)>a:
                a=int(el)
                suma+=1
            else:
                suma=0
                continue
    print(suma)
    f.close()

