def quick_sort(arr):
    if len(arr) < 2:
        return arr
    else:
        separate_num = arr[0]
        smaller_nums = [i for i in arr[1::] if i <= separate_num]
        bigger_nums = [i for i in arr[1::] if i > separate_num]
        return quick_sort(smaller_nums) + [separate_num] + quick_sort(bigger_nums)


test_arr = [3, 1, 2, 4, 5, 7, 10, 23, 4, 8, 9]
print(quick_sort(test_arr))
