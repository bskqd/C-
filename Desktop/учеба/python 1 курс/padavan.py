def f(i):
    r = 1
    for j in range(1,i+1):
        r*=j
    return r
s=0
s1=0
x=4
for i in range(0,1000000000):
    s1=s
    s+=(x**i)/f(i)
    if s-s1<0.00000001:
        print(i)
        break
print(s)
    
