def sum_rec(arr):
    if len(arr) == 0:
        return 0
    else:
        return arr[0] + sum_rec(arr[1::])


arr_1 = [3, 4, 5]
print(sum_rec(arr_1))
