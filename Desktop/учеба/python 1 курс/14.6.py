def s(a):
    kil=0
    suma=0
    try:
        while True:
            suma+=a[kil]
            kil+=1
    except ValueError:
        print('One of your numbers is wrong')
    except BaseException:
        print('The End')
    finally:
        return 'Сума=',suma,'Кількість=',kil

a=(1,7)
print(s(a))
