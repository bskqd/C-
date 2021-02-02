def rmat(fname):
    f=open(fname)
    for line in f:
        print(line)
    f.close
def gmat(n,fname):
    f=open(fname)
    M=[]
    for i in range(n):
        r=[float(k) for k in input().split()]
        M.append(r)
    print(M,end='',sep='')
    f.close
    
gmat(3,"C:\\Users\\Богдан\\Desktop\\python\\t.13_3.txt")
