def zeros_to_end(ls):

    for i in range(len(ls) - 1):
        if ls[i] == 0:
            ls.append(0)
            ls.pop(i)
    return ls


l = [2, 1, 3, 0, 2, 0]

print(zeros_to_end(l))
