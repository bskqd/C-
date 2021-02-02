import os
from tkinter import *

root = Tk()

count = 0
taxes = 0
salary = 0
s = ''
s1 = ''

fr=Frame(root, width=500, height=500)
fr.pack()

ein = Entry(fr, font=('arial', 16))
ein.grid(row=1, column=2, sticky=W)
ein.focus()
eni = (ein.get()).split()

def tomenu():
    for i in range(15):
        clear()

    Label(fr, text='Input : surname, name, position, experience in years, qualification for engineers',
          font=('arial', 16)).grid(row=1, column=1, sticky=W)
    ein = Entry(fr, font=('arial', 16))
    ein.grid(row=1, column=2, sticky=W)
    ein.focus()
    eni = (ein.get()).split()
    lrez = Label(fr, font=('arial', 16),
                 text='Positions : \"Ing\", \"Kadr\", \"Test\"; Qualification for engineers : 1, 2, 3')
    lrez.grid(row=2, column=1, sticky=W)
    btn = Button(fr, text='Add', font=('arial', 16), command=lambda: add(ein.get()))
    btn.grid(row=2, column=2, sticky=N)

    Button(fr, text='List of workers', font=('arial', 16), command=tex).grid(row=3, column=1, sticky=W)
    Button(fr, text='Exit', font=('arial', 16), command=e).grid(row=3, column=3, sticky=W)
    Button(fr, text='Salary', font=('arial', 16), command=calculate).grid(row=3, column=1, sticky=E)
    root.mainloop()


def clear():
    if fr.winfo_children():
        fr.winfo_children()[0].destroy()

def e():
    exit(0)
    sys.exit
    os.abort()


def tex():
    for i in range(15):
        clear()
    f = open("lab11.txt")
    tx = Text(fr, width=80, height=25)
    for line in f:
        tx.insert(1.0,line)
    b2 = Button(fr, text='Add an employee', width=20, height=5, bg="white", fg="black", font='Arial 15', command=tomenu)
    b2.pack()
    tx.pack()
    root.mainloop()

def calculatesalaryI(y, q):
    return q * 1000 * (1 + y/10)

def calculatesalaryT(y):
    return 900 * (1 + y/5)

def calculatesalaryK(y):
    return 800 * (1 + 0.1 * (y/3))


def add(inp):
    global s, s1
    f = open('lab11.txt')
    for line in f:
        s1 += line
    f.close()
    f = open('lab11.txt', 'w')
    s = ''
    eni = inp.split()
    if eni[2] == 'Ing':
        s += str(eni[0]) + ' ' + str(eni[1]) + ' ' + str(eni[2]) + ' ' + str(eni[3]) + ' ' + str(eni[4]) + '\n'
    else:
        s += str(eni[0]) + ' ' + str(eni[1]) + ' ' + (eni[2]) + ' ' + str(eni[3]) + '\n'
    f.write(s1,)
    f.write(s,)
    s1 = ''
    f.close()

def calculate():
    for i in range(15):
        clear()
    global count, salary, taxes
    lrez3 = Label(fr, font=('arial', 16), text='Money, company has to pay to all employees (without taxes) :   ')
    lrez3.grid(row=1, column=1, sticky=W)

    lrez4 = Label(fr, font=('arial', 16), text='Taxes, company has to pay :   ')
    lrez4.grid(row=2, column=1, sticky=W)

    lrez5 = Label(fr, font=('arial', 16), text='Money, company has to pay to all employees (with taxes) :   ')
    lrez5.grid(row=3, column=1, sticky=W)

    Button(fr, text='Back', font=('arial', 16), command = tomenu).grid(row=4, column=1, sticky=W)

    f = open('lab11.txt', 'r')
    for line in f:
        if line.split() == []:
            pass
        elif line.split()[2] == 'Ing':
            s = calculatesalaryI(int(line.split()[3]), int(line.split()[4]))
            count += s
            taxes = count * 0.2
            salary = count - taxes
        elif line.split()[2] == 'Test':
            s = calculatesalaryT(int(line.split()[3]))
            count += s
            taxes = count * 0.2
            salary = count - taxes
        elif line.split()[2] == 'Kadr':
            s = calculatesalaryK(int(line.split()[3]))
            count += s
            taxes = count * 0.2
            salary = count - taxes
    lrez3['text'] = 'Money, company has to pay to all employees (without taxes) : {}'.format(count)
    lrez4['text'] = 'Taxes, company has to pay : {}'.format(taxes)
    lrez5['text'] = 'Money, company has to pay to all employees (with taxes) : {}'.format(salary)
    Button(fr, text='Back', font=('arial', 16), command=tomenu).grid(row=4, column=1, sticky=W)
    f.close()
    root.mainloop()


Label(fr, text='Input : surname, name, position, experience in years, qualification for engineers',
          font=('arial', 16)).grid(row=1, column=1, sticky=W)
lrez = Label(fr, font=('arial', 16),
                 text='Positions : \"Ing\", \"Kadr\", \"Test\"; Qualification for engineers : 1, 2, 3')
lrez.grid(row=2, column=1, sticky=W)
btn = Button(fr, text='Add', font=('arial', 16), command=lambda: add(ein.get()))
btn.grid(row=2, column=2, sticky=N)


Button(fr, text='List of workers', font=('arial', 16), command=tex).grid(row=3, column=1, sticky=W)
Button(fr, text='Exit', font=('arial', 16), command=e).grid(row=3, column=3, sticky=W)
Button(fr, text='Salary', font=('arial', 16), command=calculate).grid(row=3, column=1, sticky=E)



root.mainloop()