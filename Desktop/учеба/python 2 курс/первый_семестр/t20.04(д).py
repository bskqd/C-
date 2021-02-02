import numpy as np
import matplotlib.pyplot as plt


NUM = 5000

def func5(n):
    def _func5(x):
        s = np.ones_like(x)
        a = np.ones_like(x)
        for i in range(1, n + 1):
            a *= x / i
            s += a
        return s
    return _func5


def mc_square(f1, f2, xmin, xmax, ymin, ymax):
    box_square = (xmax - xmin) * (ymax - ymin)
    count = int(box_square) * NUM
    x = np.random.uniform(xmin, xmax, count)
    y = np.random.uniform(ymin, ymax, count)
    y1 = f1(x)
    y2 = f2(x)
    count_in = len(y[np.logical_or(
        np.logical_and(y1 <= y, y <= y2),
        np.logical_and(y2 <= y, y <= y1))])

    return box_square * count_in / count, box_square


def movespinesticks():
    ax = plt.gca()
    ax.spines["top"].set_color("none")
    ax.spines["right"].set_color("none")
    ax.spines["bottom"].set_position(("data", 0))
    ax.spines["left"].set_position(("data", 0))


def plotf1f2(a, b, n, f1, f2):
    x = np.linspace(a, b, n)
    y1 = f1(x)
    y2 = f2(x)

    plt.subplot(2, 1, 1)
    plt.plot(x, y1)
    plt.plot(x, y2)
    plt.fill_between(x, y1, y2, where=np.abs(y2 - y1) >= 0, facecolor="green")

    a0, b0, c0, d0 = plt.axis()
    square, box_square = mc_square(f1, f2, a0, b0, c0, d0)
    print("Error: ", np.sqrt(square / box_square))

    movespinesticks()
    plt.xlabel("x")
    plt.ylabel("y")

    ydif = np.abs(y2 - y1)

    plt.subplot(2, 1, 2)
    plt.plot(x, ydif, label="diff")

    movespinesticks()
    plt.xlabel("x")
    plt.ylabel("y")
    plt.legend(loc="best")

    plt.show()


if __name__ == '__main__':
    a = -5
    b = 5
    m = 5
    plotf1f2(a, b, 1000, lambda x: np.e ** x, func5(m))