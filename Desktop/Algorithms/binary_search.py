def binary_search(lst, item):
    low = 0
    high = len(lst)-1

    while low <= high:
        mid = (low + high) // 2
        guess = lst[mid]
        print('mid =', mid, 'guess =', guess, 'item =', item)
        if guess == item:
            return mid
        elif guess > item:
            high = mid - 1
        else:
            low = mid + 1
    return None


ls = [1, 3, 5, 7, 9, 12, 15, 19, 25, 29, 34, 39, 47, 56, 78, 90, 111, 123, 145, 165]

ls_u = [4252, 3252, 235, 124, 1, 214]

print(binary_search(ls, 47))
print(binary_search(sorted(ls_u), 235))
