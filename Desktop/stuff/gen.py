def gen():
    n = 10
    while n <= 20:
        sq = n * n
        yield sq
        n += 1


for i in gen():
    print(i)
