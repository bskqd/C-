def trace(f):
    depth = 0

    def _trace(*args, **kwargs):
        nonlocal depth
        depth += 1
        print("Входження у функцію: {}".format(f.__name__), end="; ")
        print("Глибина: {}".format(depth), end="; ")
        print("Позиційні параметри: {}".format(args), end="; ")
        print("Ключові параметри: {}".format(kwargs), end="; ")
        res = f(*args, **kwargs)
        print("Вихід з функції: {}".format(f.__name__), end="; ")
        print("Глибина: {}".format(depth), end="; ")
        print("результат: {}".format(res))
        depth -= 1
        return res
    return _trace


@trace
def fib(n):
    if n == 0:
        return 0
    elif n ==1:
        return 1
    else:
        return fib(n-1) + fib(n-2)


@trace
def fact(n):
    if n ==0:
        return 1
    else:
        return n * fact(n-1)


print(fib(7), fact(7))