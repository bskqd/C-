print('Введіть досить для отримання результату')
ValError=0
RunError=0
TpError=0
while True:
    x=input()
    if x=='досить':
        break
    try:
        0<int(x)<9
    except ValueError:
        ValError+=1
        continue
    try:
        if int(x)>9:
            raise RuntimeError
    except RuntimeError:
        RunError+=1
        continue
    try:
        if int(x)<0:
            raise TypeError
    except TypeError:
        TpError+=1
        continue
    
print('TypeError = ',TpError,'RuntimeError = ',RunError,'ValueError = ',ValError)
