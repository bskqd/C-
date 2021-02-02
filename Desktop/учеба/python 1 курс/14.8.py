def fl(fname):
    f = open(fname)
    for i in f:
        for j in i.split():
            try:
                int(j)
            except ValueError:
                print("Not int")
            else:
                print(j, end=" ")
    f.close()
try:
    f = open("content.txt")
except FileNotFoundError:
    print("File is not found")
else:
    for i in f:
        for j in i.split():
            try:
                fl(j)
            except FileNotFoundError:
                print("File is not found")
    f.close()
