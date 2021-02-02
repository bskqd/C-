from threading import Thread
import sys
import os
import time
from time import sleep


def create_file(dir1):
    root = sys.path[0]
    path = os.path.join(root, dir1)
    for i in range(100):
        s = 'text' + str(i) + '.tmp'
        filename = open(os.path.join(path, s), 'w', encoding='utf-8')
        filename.close()
        sleep(0.1)


def del_file(dir1, t1, t2):
    sleep(t1)
    root = sys.path[0]
    for name in os.listdir(dir1):
        print('hi')
        file = os.path.join(root, dir1, name)
        if file[-4:] == '.tmp' and os.path.getmtime(file) <= time.time() - t2:
            os.remove(file)


if __name__ == '__main__':
    t1 = 3
    t2 = 4
    create_file('dir1')
    th = Thread(target=del_file, args=('dir1', t1, t2), daemon=True)
    th.start()
    sleep(2*t1)
