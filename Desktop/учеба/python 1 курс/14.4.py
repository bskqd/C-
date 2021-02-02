def detect(fname):
    try:
        f=open(fname)
        for line in f:
            print(line)
        f.close
    except FileNotFoundError:
        print('None')


detect('C:\\Users\\Богдан\\Desktop\\python\\t.13_56.txt')
