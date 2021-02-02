import sys
import os
import time


root = sys.path[0]


def combine_notes(index):
    lst = []
    s = ''
    for name in os.listdir(index):
        file = os.path.join(root, index, name)
        if os.path.isfile(file):
            ctime = os.path.getctime(file)
            dt = {'file': file, 'ctime': time.ctime(ctime)}
            lst.append(dt)
    for i in range(len(lst) - 1):
        for j in range(len(lst) - 1 - i):
            if lst[j]['ctime'] > lst[j + 1]['ctime']:
                lst[j], lst[j + 1] = lst[j + 1], lst[j]
    for item in lst:
        f = open(item['file'], 'r', encoding='utf-8')
        for line in f:
            s += line + '\n'
        f.close()
    f = open(os.path.join(root, 'notes_comb.txt'), 'w', encoding='utf-8')
    f.write(s)
    f.close()
    return None


if __name__ == '__main__':
    d = os.path.join(root, 'notes')
    combine_notes(d)
