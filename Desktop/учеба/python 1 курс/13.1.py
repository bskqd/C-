def genfile(fname):
    f=open(fname,'wt')
    for i in range(1,10):
        for g in range(i):
            print(i,end='',file=f)
        print(file=f)
    f.close
    
genfile("C:\\Users\\Богдан\\Desktop\\python\\t.13_3.txt")
