def gam(d):
    sum=0
    for i in range(1,501):
        try:
            sum+=i*d[i]
        except KeyError:
            continue
    return sum

d={5:5,10:5,2:5}
print(gam(d))
