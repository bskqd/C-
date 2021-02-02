import re


PIB1 = r"\b([А-ЯЇІЄ][а-яїіє]+)(.)([А-ЯЇІЄ][а-яїіє]+)(.)([А-ЯЇІЄ][а-яїіє]+)"
PIB2 = r"\b([А-ЯЇІЄ][а-яїіє]+)(.)([А-ЯЇІЄ]\.)(.)([А-ЯЇІЄ]\.)"
PIB = PIB1 + "|" + PIB2

PHONE1 = r"\b([тТ].+:.?)(\d{10,12})"
PHONE2 = r"\b([тТ].+.?)(\d{10,12})"
PHONE = PHONE1 + "|" + PHONE2

CREDIT = r"\b([б][о][р][г].+?)(?P<cr>\d{1,1000000})"


def test_def(string):
    pib_s = []
    phone_s = []
    credit_s = []
    result_s = ""
    result_l = []
    for match in re.finditer(PIB, string):
        pib_s.append(match.group())
    for match in re.finditer(PHONE, string):
        phone_s.append(match.group())
    for match in re.finditer(CREDIT, string):
        credit_s.append(match.group("cr"))
    for result in zip(pib_s, phone_s, credit_s):
        result_l.append(result)
    for result in result_l:
        result_s += f"{result[0]}, {result[1]}, борг: {result[2]} \n"
    return result_s


if __name__ == '__main__':
    s = ""
    lst_d = []
    f = open('draft_re_inp.txt', 'r', encoding='utf-8')
    for line in f:
        line = test_def(line)
        d = {'pib': line.split(',')[0], 'phone': line.split(',')[1].split(': ')[1], 'credit': int(line.split(':')[2])}
        lst_d.append(d)
    for i in range(len(lst_d) - 1):
        for j in range(len(lst_d) - 1 - i):
            if lst_d[j]['credit'] < lst_d[j + 1]['credit']:
                lst_d[j], lst_d[j + 1] = lst_d[j + 1], lst_d[j]
    f.close()
    f = open('draft_re_out_2.txt', 'w', encoding='utf-8')
    s = ''
    for item in lst_d[:100]:
        s += f"{item['pib']}, телефон: {item['phone']}, борг: {item['credit']}\n"
    f.write(s)
    f.close()
