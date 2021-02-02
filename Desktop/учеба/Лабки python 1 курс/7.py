#a
def rec1(k, x):
    a = x
    for k in range(2, k + 1):
        a *= x-(x/k)
    return a

a = rec1(8, 2)
print(a)

def gen_rec1(k, x):
    a = x
    yield a
    for k in range(2, k + 1):
        a *= x-(x/k)
        yield a
for i in gen_rec1(8,2):
    print(i)

#b
def almost_factorial(N):
    a = 1/2
    for i in range(2, N + 1):
        a *= 1/(i + 1)
    return a

al_a = almost_factorial(5)
print(al_a)

def gen_almost_factorial(N):
    a = 1/2
    yield a
    for i in range(2, N + 1):
        a *= 1/(i + 1)
        yield a
for i in gen_almost_factorial(5):
    print(i)

#c
def determinant(N):
    d2 = 2
    d1 = 1
    for n in range(3, N + 1):
        d2, d1 = d1, 2*d1 - 3*d2
    return d1

N = int(input('N = '))
print("determinant_%d = %d" % (N, determinant(N)))

def gen_determinant(N):
    d2 = 2
    yield d2
    d1 = 1
    yield d1
    for n in range(3, N + 1):
        d2, d1 = d1, 2*d1 - 3*d2
        yield d1
for i in gen_determinant(8):
    print(i)

#d
def suma(N):
    a2 = 0
    a1 = 1
    s = 4
    for n in range(3, N + 1):
        a2, a1 = a1, a1 + n*a2
        s = (2**n) * a1 + s
    return s
            
N = int(input('N = '))
print("suma_%d = %d" % (N, suma(N)))

def gen_suma(N):
    a2 = 0
    yield a2
    a1 = 1
    yield a1
    s = 4
    yield s
    for n in range(3, N + 1):
        a2, a1 = a1, a1 + n*a2
        yield a1
        s = (2**n) * a1 + s
        yield s
for i in gen_suma(9):
    print(i)

#e
def sin(x):
    S = x
    a = x
    n = 0
    eps = 0.00001
    while abs(a) >= eps:
        n = n + 1
        a = ((-x)*x)/(2*n*(2*n+1))
        S = S + a
    return S

print(sin(2))

def gen_sin(x):
    S = x
    yield S
    a = x
    yield a
    n = 0
    yield n
    eps = 0.00001
    yield eps
    while abs(a) >= eps:
        n = n + 1
        yield n
        a = ((-x)*x)/(2*n*(2*n+1))
        yield a
        S = S + a
        yield S
for i in gen_sin(2):
    print(i)