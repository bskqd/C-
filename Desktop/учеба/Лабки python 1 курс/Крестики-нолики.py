import turtle as t

class Figure:
    def __init__(self,x,y):
        self._x=x
        self._y=y
    def draw(self):
        pass

class Board(Figure):
    def __init__(self,x,y):
        super().__init__(x,y)
    def draw(self):
        t.speed(0)
        t.up()
        t.setpos(self._x,self._y)
        t.down()
        t.forward(90)
        t.left(90)
        t.forward(90)
        t.left(90)
        t.forward(90)
        t.left(90)
        t.forward(90)
        t.up()
        t.setpos(self._x+90-30,self._y+90)
        t.down()
        t.forward(90)
        t.up()
        t.setpos(self._x+90-60,self._y+90)
        t.down()
        t.forward(90)
        t.up()
        t.setpos(self._x+90,self._y+90-30)
        t.down()
        t.right(90)
        t.forward(90)
        t.up()
        t.setpos(self._x+90,self._y+90-60)
        t.down()
        t.left(360)
        t.forward(90)
class Nolik(Figure):
    def __init__(self,x,y):
        super().__init__(x,y)
    def draw(self):
        t.speed(0)
        t.up()
        t.setpos(self._x,self._y)
        t.down()
        t.circle(15)
        t.up()
        t.setheading(0)
class Krestik(Figure):
    def __init__(self,x,y):
        super().__init__(x,y)
    def draw(self):
        t.speed(0)
        t.up()
        t.setpos(self._x,self._y)
        t.down()
        t.left(135)
        t.forward(21)
        t.up()
        t.setpos(self._x,self._y)
        t.down()
        t.left(90)
        t.forward(21)
        t.up()
        t.setpos(self._x,self._y)
        t.down()
        t.left(180)
        t.forward(21)
        t.up()
        t.setpos(self._x,self._y)
        t.down()
        t.right(90)
        t.forward(21)
        t.up()
        t.setheading(0)
        
bb=Board(0,0)
bb.draw()

l=[]
nextTurn='X'

def clicked(x,y):
    global nextTurn,l
    if nextTurn=='X':
        if (x>0 and x<30) and (y>60 and y<90):
            l.append('1X')
            g=Krestik(15,75)
            g.draw()
            nextTurn='O'
        elif (x>30 and x<60) and (y>60 and y<90):
            l.append('2X')
            g=Krestik(45,75)
            g.draw()
            nextTurn='O'
        elif (x>60 and x<90) and (y>60 and y<90):
            l.append('3X')
            g=Krestik(75,75)
            g.draw()
            nextTurn='O'
        elif (x>0 and x<30) and (y>30 and y<60):
            l.append('4X')
            g=Krestik(15,45)
            g.draw()
            nextTurn='O'
        elif (x>30 and x<60) and (y>30 and y<60):
            l.append('5X')
            g=Krestik(45,45)
            g.draw()
            nextTurn='O'
        elif (x>60 and x<90) and (y>30 and y<60):
            l.append('6X')
            g=Krestik(75,45)
            g.draw()
            nextTurn='O'
        elif (x>0 and x<30) and (y>0 and y<30):
            l.append('7X')
            g=Krestik(15,15)
            g.draw()
            nextTurn='O'
        elif (x>30 and x<60) and (y>0 and y<30):
            l.append('8X')
            g=Krestik(45,15)
            g.draw()
            nextTurn='O'
        elif (x>60 and x<90) and (y>0 and y<30):
            l.append('9X')
            g=Krestik(75,15)
            g.draw()
            nextTurn='O'
    elif nextTurn=='O':
        if (x>0 and x<30) and (y>60 and y<90):
            l.append('1O')
            g=Nolik(15,60)
            g.draw()
            nextTurn='X'
        elif (x>30 and x<60) and (y>60 and y<90):
            l.append('2O')
            g=Nolik(45,60)
            g.draw()
            nextTurn='X'
        elif (x>60 and x<90) and (y>60 and y<90):
            l.append('3O')
            g=Nolik(75,60)
            g.draw()
            nextTurn='X'
        elif (x>0 and x<30) and (y>30 and y<60):
            l.append('4O')
            g=Nolik(15,30)
            g.draw()
            nextTurn='X'
        elif (x>30 and x<60) and (y>30 and y<60):
            l.append('5O')
            g=Nolik(45,30)
            g.draw()
            nextTurn='X'
        elif (x>60 and x<90) and (y>30 and y<60):
            l.append('6O')
            g=Nolik(75,30)
            g.draw()
            nextTurn='X'
        elif (x>0 and x<30) and (y>0 and y<30):
            l.append('7O')
            g=Nolik(15,0)
            g.draw()
            nextTurn='X'
        elif (x>30 and x<60) and (y>0 and y<30):
            l.append('8O')
            g=Nolik(45,0)
            g.draw()
            nextTurn='X'
        elif (x>60 and x<90) and (y>0 and y<30):
            l.append('9O')
            g=Nolik(75,0)
            g.draw()
            nextTurn='X'
    for i in l:
        if i in '1X':
            for i in l:
                if i in '2X':
                    for i in l:
                        if i in '3X':
                            t.reset()
                            t.up()
                            t.pensize(15)
                            t.setpos(-250,0)
                            t.down()
                            t.write("Crosses is winner", "center", font=("Arial", 50, "normal"))
                            t.mainloop()
                            t.up()
    for i in l:
        if i in '4X':
            for i in l:
                if i in '5X':
                    for i in l:
                        if i in '6X':
                            t.reset()
                            t.up()
                            t.pensize(15)
                            t.setpos(-250,0)
                            t.down()
                            t.write("Crosses is winner", "center", font=("Arial", 50, "normal"))
                            t.mainloop()
                            t.up()
    for i in l:
        if i in '7X':
            for i in l:
                if i in '8X':
                    for i in l:
                        if i in '9X':
                            t.reset()
                            t.up()
                            t.pensize(15)
                            t.setpos(-250,0)
                            t.down()
                            t.write("Crosses is winner", "center", font=("Arial", 50, "normal"))
                            t.mainloop()
                            t.up()
    for i in l:
        if i in '1X':
            for i in l:
                if i in '4X':
                    for i in l:
                        if i in '7X':
                            t.reset()
                            t.up()
                            t.pensize(15)
                            t.setpos(-250,0)
                            t.down()
                            t.write("Crosses is winner", "center", font=("Arial", 50, "normal"))
                            t.mainloop()
                            t.up()
    for i in l:
        if i in '2X':
            for i in l:
                if i in '5X':
                    for i in l:
                        if i in '8X':
                            t.reset()
                            t.up()
                            t.pensize(15)
                            t.setpos(-250,0)
                            t.down()
                            t.write("Crosses is winner", "center", font=("Arial", 50, "normal"))
                            t.mainloop()
                            t.up()
    for i in l:
        if i in '3X':
            for i in l:
                if i in '6X':
                    for i in l:
                        if i in '9X':
                            t.reset()
                            t.up()
                            t.pensize(15)
                            t.setpos(-250,0)
                            t.down()
                            t.write("Crosses is winner", "center", font=("Arial", 50, "normal"))
                            t.mainloop()
                            t.up()
    for i in l:
        if i in '1X':
            for i in l:
                if i in '5X':
                    for i in l:
                        if i in '9X':
                            t.reset()
                            t.up()
                            t.pensize(15)
                            t.setpos(-250,0)
                            t.down()
                            t.write("Crosses is winner", "center", font=("Arial", 50, "normal"))
                            t.mainloop()
                            t.up()
    for i in l:
        if i in '3X':
            for i in l:
                if i in '5X':
                    for i in l:
                        if i in '7X':
                            t.reset()
                            t.up()
                            t.pensize(15)
                            t.setpos(-250,0)
                            t.down()
                            t.write("Crosses is winner", "center", font=("Arial", 50, "normal"))
                            t.mainloop()
                            t.up()
    for i in l:
        if i in '1O':
            for i in l:
                if i in '2O':
                    for i in l:
                        if i in '3O':
                            t.reset()
                            t.up()
                            t.pensize(15)
                            t.setpos(-200,0)
                            t.down()
                            t.write("Toes is winner", "center", font=("Arial", 50, "normal"))
                            t.mainloop()
                            t.up()
    for i in l:
        if i in '4O':
            for i in l:
                if i in '5O':
                    for i in l:
                        if i in '6O':
                            t.reset()
                            t.up()
                            t.pensize(15)
                            t.setpos(-250,0)
                            t.down()
                            t.write("Toes is winner", "center", font=("Arial", 50, "normal"))
                            t.mainloop()
                            t.up()
    for i in l:
        if i in '7O':
            for i in l:
                if i in '8O':
                    for i in l:
                        if i in '9O':
                            t.reset()
                            t.up()
                            t.pensize(15)
                            t.setpos(-250,0)
                            t.down()
                            t.write("Toes is winner", "center", font=("Arial", 50, "normal"))
                            t.mainloop()
                            t.up()
    for i in l:
        if i in '1O':
            for i in l:
                if i in '4O':
                    for i in l:
                        if i in '7O':
                            t.reset()
                            t.up()
                            t.pensize(15)
                            t.setpos(-250,0)
                            t.down()
                            t.write("Toes is winner", "center", font=("Arial", 50, "normal"))
                            t.mainloop()
                            t.up()
    for i in l:
        if i in '2O':
            for i in l:
                if i in '5O':
                    for i in l:
                        if i in '8O':
                            t.reset()
                            t.up()
                            t.pensize(15)
                            t.setpos(-250,0)
                            t.down()
                            t.write("Toes is winner", "center", font=("Arial", 50, "normal"))
                            t.mainloop()
                            t.up()
    for i in l:
        if i in '3O':
            for i in l:
                if i in '6O':
                    for i in l:
                        if i in '9O':
                            t.reset()
                            t.up()
                            t.pensize(15)
                            t.setpos(-250,0)
                            t.down()
                            t.write("Toes is winner", "center", font=("Arial", 50, "normal"))
                            t.mainloop()
                            t.up()
    for i in l:
        if i in '1O':
            for i in l:
                if i in '5O':
                    for i in l:
                        if i in '9O':
                            t.reset()
                            t.up()
                            t.pensize(15)
                            t.setpos(-250,0)
                            t.down()
                            t.write("Toes is winner", "center", font=("Arial", 50, "normal"))
                            t.mainloop()
                            t.up()
    for i in l:
        if i in '3O':
            for i in l:
                if i in '5O':
                    for i in l:
                        if i in '7O':
                            t.reset()
                            t.up()
                            t.pensize(15)
                            t.setpos(-250,0)
                            t.down()
                            t.write("Toes is winner", "center", font=("Arial", 50, "normal"))
                            t.mainloop()
                            t.up()
    for i in l:
        if i in '1X' or i in '1O':
            for i in l:
                if i in '2X' or i in '2O':
                    for i in l:
                        if i in '3X' or i in '3O':
                            for i in l:
                                if i in '4X' or i in '4O':
                                    for i in l:
                                        if i in '5X' or i in '5O':
                                            for i in l:
                                                if i in '6X' or i in '6O':
                                                    for i in l:
                                                        if i in '7X' or i in '7O':
                                                            for i in l:
                                                                if i in '8X' or i in '8O':
                                                                    for i in l:
                                                                        if i in '9X' or i in '9O':
                                                                            t.reset()
                                                                            t.up()
                                                                            t.pensize(15)
                                                                            t.setpos(-150,0)
                                                                            t.down()
                                                                            t.write("It's a draw!", "center", font=("Arial", 50, "normal"))
                                                                            t.mainloop()
                                                                            t.up()
                                                                                    
                                                                                    
        
t.onscreenclick(clicked)
t.mainloop()
