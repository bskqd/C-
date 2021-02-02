def dec(func):

    def _inner(*args, **kwargs):
        res = func(*args, **kwargs)
        for arg in args:
            print(arg)
        return res

    return _inner


def dec_2(func):

    def _inner(a, b):
        if a < b:
            a, b = b, a
        return func(a, b)

    return _inner


@dec
def div(a, b):
    return a//b


@dec_2
def div_2(a, b):
    return a//b


print('res', div(6, 2))
print('res_2', div_2(3, 9))
