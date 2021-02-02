def fac(n):
    fac = 1 
    i = 0 
    while i < n:
        i += 1
        fac = fac * i
    return fac

x=4
e=0.00000001
s=5
s1=1
i=2
while abs(s-s1)>=e:
    s1=s
    s+=(x**i)/fac(i)
    i+=1
print(i)
