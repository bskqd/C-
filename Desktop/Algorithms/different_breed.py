mas = [[1, 2, 3], [5, 5, 6], [7, 8, 9]]


def any_d(ms):
    lst = []
    for i in ms:
        for j in i:
            lst.append(j)

    if len(set(lst)) == 9:
        return False
    else:
        return True


def any_d_v2(ms):
    baz = set(ms[0]+ms[1]+ms[2])
    if len(baz) == 9:
        return False
    else:
        return True


print(any_d(mas))
print(any_d_v2(mas))
