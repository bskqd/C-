def biggest_item_rec(arr):
    if len(arr) == 1:
        return arr[0]
    else:
        b_i = biggest_item_rec(arr[1::])
        return b_i if b_i > arr[0] else arr[0]


arr_3 = [1, 2, 3, 4, 5]
print(biggest_item_rec(arr_3))
