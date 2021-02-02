def find_smallest(lst):
    smallest_number = lst[0]
    smallest_index = 0
    for i in range(1, len(lst)):
        if lst[i] < smallest_number:
            smallest_number = lst[i]
            smallest_index = i
    return smallest_index


def selection_sort(lst):
    new_lst = []
    for i in range(len(lst)):
        smallest = find_smallest(lst)
        new_lst.append(lst.pop(smallest))
    return new_lst


arr = [11, 12, 53, 41, 124, 125, 12535, 12512, 13515, 26357, 35745, 2473, 262, 2785, 658, 68, 485]
print(selection_sort(arr))
