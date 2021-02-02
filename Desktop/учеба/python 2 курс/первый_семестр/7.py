import numpy as np


def dis(x1, x2):
    return np.sqrt(np.sum((x2 - x1) ** 2))


def calc_per(x1, x2, x3):
    a = dis(x1, x2)
    b = dis(x2, x3)
    c = dis(x3, x1)
    return a + b + c


def max_per(x):
    maximum = 0
    for i in range(0, x.size, 2):
        for j in range(i + 2, x.size, 2):
            for k in range(j + 2, x.size, 2):
                x1 = x[i:i + 2]
                x2 = x[j:j + 2]
                x3 = x[k:k + 2]
                if calc_per(x1, x2, x3) > maximum:
                    maximum = calc_per(x1, x2, x3)
    return maximum


if __name__ == '__main__':
    a = np.array([-1, 0, 1, 0, 0, np.sqrt(3), 0, -np.sqrt(3)])
    print(max_per(a))
