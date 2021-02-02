s=input()
l=''
for i in s:
    if i in 'x':
        l+='a'
    else:
        l+=i
print(l)
