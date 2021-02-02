

import tkinter as tk
from concurrent.futures import ThreadPoolExecutor


def prime_number(n):

    if n <= 1:
        return "Число менше чи рівне одиниці"
    i = 2
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return f"Число {n} не є простим"
        i = i + 1

    return f"число {n} є простим"


class FibSubGUI:

    def __init__(self, n):
        self._top = tk.Toplevel()
        self._top.minsize(300, 100)

        lbl = tk.Label(self._top,
                       text="Число {} є ...".format(n),
                       font=("Arial", 24))
        lbl.pack()
        btn = tk.Button(self._top,
                        text="Закрити",
                        font=("Arial", 24),
                        command=self._top.destroy)
        btn.pack()

        result = prime_number(n)
        lbl.configure(text=result)


class FibMainGUI:

    def __init__(self):
        self._top = tk.Tk()
        self._executor = ThreadPoolExecutor(max_workers=2)

        self._var = tk.IntVar(self._top, 17)
        self._make_widgets()
        self._top.mainloop()

    def _make_widgets(self):
        self._top.title("Перевірка чи є число простим")
        self._top.minsize(400, 200)

        ent = tk.Entry(self._top,
                       font=("Arial", 24),
                       textvariable=self._var)
        ent.pack()
        btn = tk.Button(self._top,
                        text="Визначити",
                        font=("Arial", 24),
                        command=self._button_handler)
        btn.pack()
        btn = tk.Button(self._top,
                        text="Закрити",
                        font=("Arial", 24),
                        command=self._top.quit)
        btn.pack()

    def _button_handler(self):
        n = self._var.get()
        self._executor.submit(FibSubGUI, n)


if __name__ == '__main__':
    FibMainGUI()