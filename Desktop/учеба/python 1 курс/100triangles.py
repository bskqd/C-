import turtle as t
import random

class Triangle:
    def __init__(self,x1,y1,x2,y2,x3,y3):
        self._x1=x1
        self._y1=y1
        self._x2=x2
        self._y2=y2
        self._x3=x3
        self._y3=y3

    def draw(self,color):
        t.color(color)
        t.penup()
        t.setpos(self._x1,self._y1)
        t.pendown()
        t.speed(1000000000000)
        t.goto(self._x2,self._y2)
        t.goto(self._x3,self._y3)
        t.goto(self._x1,self._y1)
        t.up()

for i in range(0,101):
    t1=Triangle(random.randrange(-500,500),random.randrange(-500,500),random.randrange(-500,500),random.randrange(-500,500),random.randrange(-500,500),random.randrange(-500,500))
    t1.draw('Green')
        
        
