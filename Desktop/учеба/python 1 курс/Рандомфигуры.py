import turtle as t
import random


class Figure:
    """ Клас Фігура """

    def __init__(self, x, y, color):
        """ Конструктор
        :param x: координата x положення фігури
        :param y: координата y положення фігури
        :param color: колір фігури
        """
        self._x = x  # _x - координата x
        self._y = y  # _y - координата y
        self._visible = False  # _visible - чи є фіруга видимою на екрані
        self._color = color    # _color - колір фігури

    def _draw(self, color):
        """ Допоміжний метод, що зображує фігуру заданим кольором
        Тут здійснюється лише декларація методу, а конкретна
        реалізація буде здійснюватися у конкретних нащадках
        :param color: колір
        """
        pass

    def show(self):
        """ Зображує фігуру на екрані """
        if not self._visible:
            self._visible = True
            self._draw(self._color)

    def hide(self):
        """ Ховає фігуру (робить її невидимою на екрані) """
        if self._visible:
            self._visible = False
            # щоб сховати фігуру, потрібно
            # зобразити її кольором фону.
            self._draw(t.bgcolor())

    def move(self, dx, dy):
        """ Переміщує об'єкт
        :param dx: зміщення у пікселях по осі X
        :param dy: зміщення у пікселях по осі Y
        """
        isVisible = self._visible
        if isVisible:
            self.hide()
        self._x += dx
        self._y += dy
        if isVisible:
            self.show()

class Quadrate(Figure):
    def __init__ (self, x, y, a, color):
        super().__init__(x, y, color)
        self._a = a

    def _draw(self, color):
        t.speed(0)
        t.pencolor(color)
        t.up()
        t.setpos(self._x, self._y)
        t.setheading(0)
        t.down()
        t.forward(self._a)
        t.left(90)
        t.forward(self._a)
        t.left(90)
        t.forward(self._a)
        t.left(90)
        t.forward(self._a)  
        t.up()

class Circle (Figure):
    def __init__ (self, x, y, r, color):
        super().__init__(x, y, color)
        self._r = r
    def _draw(self, color):
        t.speed(0)
        t.pencolor(color)
        t.up()
        t.setpos(self._x, self._y -self._r)
        t.down()
        t.circle(self._r)
        t.up()

class Triangle(Figure):
    def __init__(self, x, y,x2,y2,x3,y3,color):
        super().__init__(x, y, color)
        self._x2 = x2
        self._x3 = x3
        self._y2 = y2
        self._y3 = y3

    def _draw(self, color):
        t.speed(10)
        t.pencolor(color)
        t.up()
        t.setpos(self._x, self._y)
        t.setheading(0)
        t.down()
        t.goto(self._x2,self._y2)
        t.goto(self._x3,self._y3)
        t.goto(self._x,self._y)
        t.up()

if __name__ == '__main__':
    for i in range(101):
        t.home()
        t.delay(30)
        j = random.random()*3
        if j > 0 and j<=1:
            c = "red"
        if j > 1 and j<=2:
            c = "green"
        if j > 2 and j<=3:
            c = "pink"
        j = random.random()*3
        if j > 0 and j<=1:
             q = Triangle(0,0,1,11,32,73,c)
             q.show()
             q.move(0, 140)
             q.hide()
             t.home()
             t.delay(30)
        if j > 1 and j<=2:
            q = Circle(120,120,50,c)
            q.show()
            q.move(0, 140)
            q.hide()
            t.home()
            t.delay(30)
        if j > 2 and j<=3:
            q = Quadrate(0,0,150,c)
            q.show()
            q.move(0, 140)
            q.hide()
            t.home()
            t.delay(30)


