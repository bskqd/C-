def check(f):

    def _check(*args, **kwargs):
        text = f(*args, **kwargs)
        string = ''

        for char in text.lower():
            if char in '!&?.,;:-_':
                pass
            else:
                string += char

        return string

    return _check


@check
def f():
    string = ''
    fi = open('mod.txt', 'rt')
    for line in fi:
        string += line
    fi.close()
    return string


if __name__ == '__main__':
    string = f()
    print(string)
    sl = string.split()

    def sym(s):
        for n in range(0, len(s) // 2):
            if s[n] != s[len(s) - 1 - n]:
                return False
        return True
    for s in sl:
        if sym(s):
            print('sym: ', s)
