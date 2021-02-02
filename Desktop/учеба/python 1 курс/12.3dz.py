x=float(input())
eps=0.00001
S=x
a=x
n=1
while abs(a)>=eps:
    n+=1
    a=-(x*(n-1)*a)/n
    S=S+a
print(S)
