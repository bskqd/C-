import math
import random


def cash(f):
    global results
    results = {}

    def _cash(*args):
        if args not in results:
            results[args] = f(*args)
        return results[args]
    return _cash


@cash
def is_prime(n):
    for i in range(2, math.floor(math.sqrt(n)) + 1):
        if n % i == 0:
            return False
    return True


def density(a, b):
    m = (b - a) * 100
    passed = 0
    for _ in range(m): #якась дія m раз
        x = random.randint(a, b)
        if is_prime(x):
            passed += 1
    return passed / m


if __name__ == '__main__':
    t = [(1, 50),
         (1, 100),
         (1, 200),
         (50, 100),
         (100, 200)]
    for a, b in t:
        print('Щільність простих чисел на відрізку ({}, {}): {:3.2}%'
              .format(a, b, density(a, b)))
    print(results)