import re


DOLLAR = r'(\$)(\d{1,100})\b'
HRIVNA1 = r'([а-яїіє]\s)\b(\d{1,100})\sгрн\b'
HRIVNA2 = r'([а-яїіє]\s)\b(\d{1,100})грн\b'
HRIVNA1_mod = r'\b(\d{1,3}\s\d{3})\sгрн\b'
HRIVNA2_mod = r'\b(\d{1,3}\s\d{3})грн\b'

dollars = []
hrivnas = []

f = open('mod_2.txt', 'r', encoding='utf-8')
for s in f:

    for match in re.finditer(DOLLAR, s):
        dollars.append(int(match.group(2)))

    for match in re.finditer(HRIVNA1, s):
        hrivnas.append(int(match.group(2)))

    for match in re.finditer(HRIVNA2, s):
        hrivnas.append(int(match.group(2)))

    for match in re.finditer(HRIVNA1_mod, s):
        match = match.group(1).split(' ')
        match = int(f'{match[0]}{match[1]}')
        hrivnas.append(match)

    for match in re.finditer(HRIVNA2_mod, s):
        match = match.group(1).split(' ')
        match = int(f'{match[0]}{match[1]}')
        hrivnas.append(match)

f.close()

sum_dol = 0
sum_hrn = 0

for i in dollars:
    sum_dol += i

for i in hrivnas:
    sum_hrn += i

print(f'hrn: {sum_hrn}, dol: {sum_dol}')
