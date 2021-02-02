def stri(s):
    sum=0
    for i in s:
        try:
            sum+=int(i)
        except ValueError:
            continue
    return sum
s='JFIoa437221d32324y'  
print(stri(s))
    
