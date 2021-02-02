def rivn(a,b,c):
    try:
        assert a!=0
        D=b**2-4*a*c
        x1=((-b)+((D)**0.5))/(a*2)
        x2=((-b)-((D)**0.5))/(a*2)
        return x1,x2
    except AssertionError:
        return 'Не квадратне'
    
print(rivn(1,-4,4))
    
