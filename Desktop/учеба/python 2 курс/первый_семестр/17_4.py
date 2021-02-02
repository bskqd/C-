import math

def correct(a, b):
    def _correct(f):
        def __correct(*args, **kwargs):
            res = f(*args, **kwargs)
            res = math.exp(res) + 1
            res = 1 / res
            res = (b - a) * res
            res = a * res
            return res
        return __correct
    return _correct

@correct(12, 100)
def c_sin(x):
    return math.sin(x)

for i in range(1, 10):
    print(c_sin)