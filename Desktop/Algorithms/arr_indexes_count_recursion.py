def index_count_rec(arr):
    if len(arr) == 0:
        return 0
    else:
        return 1 + index_count_rec(arr[1::])


arr_2 = [1, 2, 3, 4, 6, 13, 124, 12]
print(index_count_rec(arr_2))
