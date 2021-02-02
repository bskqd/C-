import turtle as t

class Flower:
    def __init__(self,n,r,m,f):
        self._n=n
        self._r=r
        self._m=m
        self._f=f
    def petals(self):
        t.color("red")
        t.begin_fill()
        t.up()
        t.setpos(0,0)
        t.down()
        t.speed(100)
        for i in range(self._n):
            for i in range(2):
                t.circle(self._r,self._m)
                t.left(180-self._m)
            t.left((360.0)/self._n)
        t.end_fill()
        t.up()
    def steam(self):
        t.pensize(5)
        t.color("green")
        t.speed(100)
        t.up()
        t.setpos(0,-600)
        t.down()
        t.left(90)
        t.forward(self._f)
    def leaf1(self):
        t.color("green")
        t.begin_fill()
        t.speed(100)
        t.up()
        t.setpos(0,-250)
        t.down()
        for i in range(2):
            t.circle(self._r,self._m)
            t.left(180-self._m)
        t.end_fill()
    def leaf2(self):
        t.color("green")
        t.begin_fill()
        t.speed(100)
        t.up()
        t.setpos(0,-300)
        t.down()
        t.right(105)
        for i in range(2):
            t.circle(self._r,self._m)
            t.left(180-self._m)
        t.end_fill()
class Flower2:
    def __init__(self,n,r,m):
        self._n=n
        self._r=r
        self._m=m
    def petals(self):
        t.color("yellow")
        t.begin_fill()
        t.up()
        t.setpos(-300,0)
        t.down()
        t.speed(100)
        for i in range(self._n):
            for i in range(2):
                t.circle(self._r,self._m)
                t.left(180-self._m)
            t.left((360.0)/self._n)
        t.end_fill()
        t.up()
    def steam(self):
        t.color("green")
        t.speed(100)
        t.up()
        t.setpos(0,-500)
        t.down()
        t.goto(-262,-64)
        t.up()
    def leaf(self):
        t.color("green")
        t.begin_fill()
        t.speed(100)
        t.up()
        t.setpos(-150,-250)
        t.left(155)
        t.down()
        for i in range(2):
            t.circle(self._r,self._m)
            t.left(180-self._m)
        t.end_fill()
        t.mainloop()
        t.up()
class Flower1:
    def __init__(self,n,r,m):
        self._n=n
        self._r=r
        self._m=m
    def petals(self):
        t.color("pink")
        t.begin_fill()
        t.up()
        t.setpos(300,0)
        t.down()
        t.speed(100)
        for i in range(self._n):
            for i in range(2):
                t.circle(self._r,self._m)
                t.left(180-self._m)
            t.left((360.0)/self._n)
        t.end_fill()
        t.up()
    def steam(self):
        t.pensize(5)
        t.color("green")
        t.speed(100)
        t.up()
        t.setpos(0,-500)
        t.down()
        t.goto(267,-42)
        t.up()
    def leaf(self):
        t.color("green")
        t.begin_fill()
        t.speed(100)
        t.up()
        t.setpos(150,-250)
        t.down()
        t.right(19)
        for i in range(2):
            t.circle(self._r,self._m)
            t.left(180-self._m)
        t.end_fill()
        t.up()    

tr=Flower(6,100,79,500)
tr1=Flower1(6,100,79)
tr2=Flower2(8,100,79)
tr.petals()
tr.steam()
tr.leaf1()
tr.leaf2()
tr1.petals()
tr1.steam()
tr1.leaf()
tr2.petals()
tr2.steam()
tr2.leaf()
