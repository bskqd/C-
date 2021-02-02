import numpy as np


def dis(x1, x2):
    return np.sqrt(np.sum((x2 - x1)**2, axis=1))


def find_per(x):
    x1 = np.vstack((x[1:], x[:1]))
    dist = dis(x, x1)
    per = np.sum(dist)
    return per


def def_max_per(x):
    y = x.copy()
    y.shape = (x.size // 2, 2)
    max_per = 0
    for i in range(y.shape[0]):
        for j in range(i + 1, y.shape[0]):
            for k in range(j + 1, y.shape[0]):
                cur = y[np.array((i, j, k))]
                if find_per(cur) > max_per:
                    max_per = find_per(cur)
                    s = f'First point: {cur[0]}, Second point: {cur[1]}, Third point: {cur[2]}'
    return max_per, s


if __name__ == '__main__':
    points = np.array([-1, 0, 1, 0, 0, np.sqrt(3), 0, -np.sqrt(3)])
    print(def_max_per(points))
