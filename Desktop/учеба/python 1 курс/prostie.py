def p(k):
 for i in range(2,k):
  if k%i==0:
   return 0
 return 1

def su(k):
 s=0
 while(k>0):
  s= s+k%10
  k=k//10
 return(s)


n= 0
k= 1000
while(k<=9999):
 if p(k)==1 and p(su(k))==1:
  n+=1
 k+=1
print(n)
