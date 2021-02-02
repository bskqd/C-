FUNCTION = type(lambda: None)
s = ''


def catch_exception(f):
    print(f'Зайшли в декоратор функції {f.__name__}')

    def func(*args, **kwargs):
        global s
        try:
            return f(*args, **kwargs)
        except Exception as e:
            s += f'Помилка в {f.__name__}: {e}' + '\n'
            pass

    return func


class CatchExceptions(type):

    def __new__(mcs, classname, bases, cls_dct):
        for name, attr in cls_dct.items():
            if isinstance(attr, FUNCTION):
                cls_dct[name] = catch_exception(attr)
        return super().__new__(mcs, classname, bases, cls_dct)


def write_exceptions(s):
    f = open('19_13.txt', 'wt')
    f.write(s)
    f.close()


class SimpleClass(metaclass=CatchExceptions):

    def __init__(self, a):
        self.a = int(a)

    def f(self):
        res = self.a / 0
        return res

    def g(self):
        res = self.a / 0
        return res

    def q(self):
        res = self.a + 5
        return res


if __name__ == '__main__':
    k = SimpleClass(5)
    print(k.f(), k.q(), k.g())
    write_exceptions(s)
