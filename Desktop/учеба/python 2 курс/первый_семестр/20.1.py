import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


a = -5
b = 5
m = 20

x = np.linspace(a, b, int((b - a) * 50))

fig = plt.figure()
ax = plt.axes(xlim=(a, b), ylim=(-4, 4))
line, = ax.plot([], [], lw=3)


def func_d(x, n):
    s = np.ones_like(x)
    a = np.ones_like(x)
    for k in range(1, n + 1):
        a *= x / k
        s += a
    return s


def init():
    # plt.plot(x, np.sin(x), "--r")
    plt.plot(x, np.exp(x), "--r")
    line.set_data([], [])
    return line,


def animate(i):
    y = func_d(x, i + 1)
    line.set_data(x, y)
    return line,


anim = FuncAnimation(fig, animate, init_func=init, frames=m, interval=20, repeat=False)
plt.show()
