def shift(c):
    if 'A'<=c<='Z':
        d=ord(c)-ord('A')
        d=d+7
        d=d%26
        return chr(d+ord('a'))
    elif 'a'<=c<='z':
        d=ord(c)-ord('a')
        d=d+7
        d=d%26
        return chr(d+ord('a'))
    elif c==' ':
        return '*'
    else:
        return c
s=input()
for el in s:
    print(shift(el),end='')
        
