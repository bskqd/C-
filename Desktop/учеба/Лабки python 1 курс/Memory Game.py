from tkinter import *
from random import shuffle
from random import randint
import time
import tkinter.messagebox as box


window = Tk()
window.title('Memory Game')
window.minsize(width = 700, height = 700)
canvas = Canvas(window, width = 700, height = 600, bg = 'black')
canvas.pack()

label_1 = Label(window, text = 'Welcome to the Memory Game!\n Pick a card to reveal a fruit!', font = 20)
label_1.pack()

cards = []

fruits = ['Apple', 'Orange', 'Banana', 'Blueberry',
          'Strawberry', 'Pineapple', 'Olive', 'Tomato',
          'Avocado', 'Kiwi', 'Pear', 'Papaya']

class Cards():
    def __init__(self, x, y, text_on_front_side):
        self.x = x
        self.y = y
        self.text_on_front_side = text_on_front_side

    def front_side_of_card(self):
        canvas.create_rectangle(self.x, self.y, self.x + 80, self.y + 80, fill = 'yellow')
        canvas.create_text(self.x + 40, self.y + 40, text = self.text_on_front_side, width = 70)
        self.front_side_up = True

    def back_side_of_card(self):
        canvas.create_rectangle(self.x, self.y, self.x + 80, self.y + 80, fill = 'light blue')
        canvas.create_text(self.x + 40, self.y + 40, text = 'Guess :)', width = 70)
        self.front_side_up = False

    def is_equal(self, event):
        if event.x > self.x and event.x < self.x + 80:
            if event.y > self.y and event.y < self.y + 80:
                    return True


randomly_selected_fruit = []
for i in range(10):
    random_index = randint(0, len(fruits) - 1)
    var = fruits[random_index]
    randomly_selected_fruit.append(var)
    randomly_selected_fruit.append(var)
    del fruits[random_index]
shuffle(randomly_selected_fruit)

flipped_cards = []
flipped_this_time = 0

def mouse_clicked(event):
    global flipped_cards
    global flipped_this_time
    for card in cards:
        if card.is_equal(event):
            if not card.front_side_up:
                card.front_side_of_card()
                flipped_cards.append(card)
                flipped_this_time += 1
            if flipped_this_time == 2:
                window.after(500, check_cards)
                flipped_this_time = 0

def check_cards():
    start = time.monotonic()
    global number_of_pairs
    if not flipped_cards[-1].text_on_front_side == flipped_cards[-2].text_on_front_side:
        flipped_cards[-1].back_side_of_card()
        flipped_cards[-2].back_side_of_card()
        del flipped_cards[-2:]
    elif flipped_cards[-1].text_on_front_side == flipped_cards[-2].text_on_front_side:
        number_of_pairs -= 1
        box.showinfo('Congratulations', 'You\'ve found a pair. Keep looking for a new one!')
        if number_of_pairs == 0:
            end = time.monotonic()
            play_time = end - start
            box.showinfo('Congratulations', 'You\'ve won. Your time is: {:.1f} in minutes and seconds'.format(play_time))

def restart():
    start = time.monotonic()
    number_of_pairs = (number_of_columns * number_of_rows) / 2
    if number_of_pairs == 0:
        end = time.monotonic()
        play_time = end - start
        box.showinfo('Congratulations', 'You\'ve won. Your time is: {:.1f} in minutes and seconds'.format(play_time))
    global randomly_selected_fruit, cards
    fruits = ['Apple', 'Orange', 'Banana', 'Blueberry',
              'Strawberry', 'Pineapple', 'Olive', 'Tomato',
              'Avocado', 'Kiwi', 'Pear', 'Papaya']
    for i in range(10):
        random_index = randint(0, len(fruits) - 1)
        var = fruits[random_index]
        randomly_selected_fruit.append(var)
        randomly_selected_fruit.append(var)
        del fruits[random_index]
    shuffle(randomly_selected_fruit)
    del cards[ : : ]
    for x in range(0, number_of_columns):
        for y in range(0, number_of_rows):
            cards.append(Cards(x * 150 + 10, y * 150 + 40, randomly_selected_fruit.pop()))
    for i in range(len(cards)):
        cards[i].back_side_of_card()

number_of_columns = 5
number_of_rows = 4
number_of_pairs = (number_of_columns * number_of_rows) / 2

for x in range(0, number_of_columns):
    for y in range(0, number_of_rows):
        cards.append(Cards(x * 150 + 10, y * 150 + 40, randomly_selected_fruit.pop()))
for i in range(len(cards)):
    cards[i].back_side_of_card()



window.bind('<Button>', mouse_clicked)


btn_restart = Button(window, text = 'Restart', command = restart, font = 12)
btn_restart.pack()

btn_end = Button(window, text = 'Exit', command = exit, font = 12)
btn_end.pack()


window.mainloop()