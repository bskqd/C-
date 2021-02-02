import numpy as np


TEST_NUM = 10000


def check(choice, to_extract):
    rez = np.zeros(choice.shape[0])
    for i in range(choice.shape[0]):
        k = 0
        for j in range(choice.shape[1]):
            if choice[i - 1, j - 1] == choice[i, j]:
                k += 1
        if k == len(to_extract):
            rez[i] = True
        else:
            rez[i] = False
    return rez


def beads_probability(beads, count, to_extract):
    choice = np.zeros((TEST_NUM, count))
    for i in range(TEST_NUM):
        choice[i, :] = np.random.choice(beads, count, replace=False)
    choice.sort(axis=1)
    to_extract = np.sort(to_extract)
    rez = check(choice, to_extract)
    return np.sum(rez) / TEST_NUM


if __name__ == '__main__':
    m = 5
    k = 4
    d = 2
    color = np.arange(m)

    beads = []
    to_ext = []
    for e in range(d):
        to_ext.append(0)
    for i in color:
        for j in range(k):
            beads.append(i)

    to_ext = tuple(to_ext)
    beads = tuple(beads)

    p = beads_probability(beads, d, to_ext)
    print(p)
