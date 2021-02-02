def rarity(f):
    results = {}

    def _rarity(*args, **kwargs):
        res = f(*args, **kwargs)
        zeros = 0
        el_res = []

        for i in range(len(res)):
            for j in range(len(res[0])):
                if res[i][j] == 0:
                    zeros += 1
                else:
                    el_res.append(res[i][j])

        for j in el_res:
            results['Element: {}'.format(j)] = j


        if zeros / len(res) > 0.1:
            return res
        else:
            return results

    return _rarity


@rarity #якщо перевіряти addition, то не використовуємо декоратор
def matrix(r, c):
    mat = []
    print("Enter the rows: ")

    for i in range(r):
        a = []
        for j in range(c):
            a.append(int(input()))
        mat.append(a)

    return mat

@rarity
def addition(m1, m2):
    result = []

    for i in range(len(m1)):
        a = []
        for j in range(len(m1[0])):
            a.append(0)
        result.append(a)

    for i in range(len(m1)):
        for j in range(len(m1[0])):
            result[i][j] = m1[i][j] + m2[i][j]

    return result



if __name__ == '__main__':
    '''
    m1 = matrix(2, 2)
    m2 = matrix(2, 2)
    print(addition(m1=m1, m2=m2))
    це для перевірки роботи addition, обов'язково прибрати @rarity перед matrix
    '''

    '''
    print(matrix(2, 3))
    це для перевірки роботи matrix
    '''

