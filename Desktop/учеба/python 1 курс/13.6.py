def genfile(fname):
    f=open(fname,'wt')
    c=''
    s=input()
    for i in s:
        c+=i
        if len(c)==40:
            print(c,file=f)
            c=''
    print(c,file=f)
    f.close
    
genfile("C:\\Users\\Богдан\\Desktop\\python\\t.13_6.txt")
