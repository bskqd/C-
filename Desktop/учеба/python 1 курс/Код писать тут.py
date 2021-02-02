def cont(fname):
    try:
        try:
            f=open(fname)
            for line in f:
                g=open(line)
                for el in g:
                    print(el)
                g.close()
        except FileNotFoundError:
            print('None') 
    except FileNotFoundError:
        print('durak')
    f.close()

print(cont('content.txt'))