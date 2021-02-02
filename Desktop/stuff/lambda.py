def my_func(n):
    return lambda a: a - n


m = my_func(10)

print(m(3))

my_2 = lambda a: a * 10

print(my_2)
