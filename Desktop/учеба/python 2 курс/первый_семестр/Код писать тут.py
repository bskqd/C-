b_t = [['a', 'b'], ['b', 'c'], ['b', 'a'], ['c', 'b'], ['a', 'b']]

lst = []

def practice():
    global b_t, lst
    for i in range(len(b_t) - 1):
        count = 1
        first_name_i = b_t[i][0]
        second_name_i = b_t[i][1]
        for j in b_t[i + 1:]:
            first_name_j = j[0]
            second_name_j = j[1]

            if first_name_i == first_name_j and second_name_i == second_name_j:
                count += 1
            elif first_name_i == second_name_j and second_name_i == first_name_j:
                count += 1
            else:
                continue

        if count > 1:
            if len(lst) > 0:
                for dt in lst:
                    if first_name_i == dt['full_name'].split(', ')[0] and\
                            second_name_i == dt['full_name'].split(', ')[1]:
                        break
                    elif first_name_i == dt['full_name'].split(', ')[1] and \
                            second_name_i == dt['full_name'].split(', ')[0]:
                        break
                    else:
                        full_name = first_name_i + ', ' + second_name_i
                        lst.append({'full_name': full_name, 'count': count})
            else:
                full_name = first_name_i + ', ' + second_name_i
                lst.append({'full_name': full_name, 'count': count})

    return lst

print(practice())

