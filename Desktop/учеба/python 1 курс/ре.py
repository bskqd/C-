import re

str = "My name is David. Hi David."
pattern = r"David"
newstr = re.sub(pattern, "Amy", str, count=1) #count=сколько раз менять
print(newstr)





pattern = r"gr.y"

if re.match(pattern, "grey"):
   print("Match 1")

if re.match(pattern, "gray"):
   print("Match 2")

if re.match(pattern, "blue"):
   print("Match 3")




pattern = r"^gr.y$" #^-начинается с gr,$-заканчивается на y

if re.match(pattern, "grey"):
   print("Match 1")

if re.match(pattern, "gray"):
   print("Match 2")

if re.match(pattern, "stingray"):
   print("Match 3")




pattern = r"spam"

if re.match(pattern, "eggspamsausagespam"):
   print("Match")
else:
   print("No match")

if re.search(pattern, "eggspamsausagespam"):
   print("Match")
else:
   print("No match")
    
print(re.findall(pattern, "eggspamsausagespam"))





pattern = r"[A-Z][A-Z][0-9]"

if re.search(pattern, "LS8"):
   print("Match 1")

if re.search(pattern, "E3"):
   print("Match 2")

if re.search(pattern, "1ab"):
   print("Match 3")
#[a-z]: 1 lower case letter
#[A-Z]: 1 upper case letter
#[A-Z]{3}: 3 consecutive upper case letters
#[A-Z]{3}[a-z][A-Z]{3}: 3 upper case letters + 1 lower case letter + 3 upper case letters
#[^A-Z]: any character BUT an upper case letter
#[^A-Z]+: at least one such character
#[^A-Z]+[A-Z]{3}[a-z][A-Z]{3}[^A-Z]+: something else before and after our patter(AAAbCCC) so there's no more than 3 consecutive upper case letters on each side




pattern = r"[^A-Z]"

if re.search(pattern, "this is all quiet"):
   print("Match 1")

if re.search(pattern, "AbCdEfG123"):
   print("Match 2")

if re.search(pattern, "THISISALLSHOUTING"):
   print("Match 3")




#Fill in the blanks to match strings that are not entirely composed of digits.
pattern = r"[^0-9]"
m = re.search(pattern, "Hi there!")





pattern = r"egg(spam)*"

if re.match(pattern, "egg"):
   print("Match 1")

if re.match(pattern, "eggspamspamegg"):
   print("Match 2")

if re.match(pattern, "spam"):
   print("Match 3")






pattern = r"g+"

if re.match(pattern, "g"):
   print("Match 1")

if re.match(pattern, "gggggggggggggg"):
   print("Match 2")

if re.match(pattern, "abc"):
   print("Match 3")





pattern = r"ice(-)?cream"

if re.match(pattern, "ice-cream"):
   print("Match 1")

if re.match(pattern, "icecream"):
   print("Match 2")

if re.match(pattern, "sausages"):
   print("Match 3")

if re.match(pattern, "ice--ice"):
   print("Match 4")




pattern = r"9{1,3}$"

if re.match(pattern, "9"):
   print("Match 1")

if re.match(pattern, "999"):
   print("Match 2")

if re.match(pattern, "9999"):
   print("Match 3")








pattern = r"a(bc)(de)(f(g)h)i"

match = re.match(pattern, "abcdefghijklmnop")
if match:
   print(match.group())
   print(match.group(0))
   print(match.group(1))
   print(match.group(2))
   print(match.groups())





pattern = r"(?P<first>abc)(?:def)(ghi)"

match = re.match(pattern, "abcdefghi")
if match:
   print(match.group("first"))
   print(match.groups())





pattern = r"gr(a|e)y"

match = re.match(pattern, "gray")
if match:
   print ("Match 1")

match = re.match(pattern, "grey")
if match:
   print ("Match 2")    

match = re.match(pattern, "griy")
if match:
    print ("Match 3")





#(.+) means 1 or more of any character
#\1 means a repetition of what was found in group number 1
pattern = r"(.+) \1"

match = re.match(pattern, "word word")
if match:
   print ("Match 1")

match = re.match(pattern, "?! ?!")
if match:
   print ("Match 2")    

match = re.match(pattern, "abc cde")
if match:
   print ("Match 3")








#More useful special sequences are \d, \s, and \w.
#These match digits, whitespace, and word characters respectively.
#In ASCII mode they are equivalent to [0-9], [ \t\n\r\f\v], and [a-zA-Z0-9_].
#In Unicode mode they match certain other characters, as well. For instance, \w matches letters with accents.
#Versions of these special sequences with upper case letters - \D, \S, and \W - mean the opposite to the lower-case versions. For instance, \D matches anything that isn't a digit.
pattern = r"(\D+\d)"

match = re.match(pattern, "Hi 999!")

if match:
   print("Match 1")

match = re.match(pattern, "1, 23, 456!")
if match:
   print("Match 2")

match = re.match(pattern, " ! $?")
if match:
    print("Match 3")








#\A is an anchor that says "the string starts here" so in other words no characters may occur before \A
#\Z is an anchor that says "the string ends here" so in other words no characters may occur after \Z
#\b matches 1 or more spaces and 0 or more letters (words). So in other words there must be at least 1 word to the left of \b and at least 1 word to the right of \b.
pattern = r"\b(cat)\b"

match = re.search(pattern, "The cat sat!")
if match:
   print ("Match 1")

match = re.search(pattern, "We s>cat<tered?")
if match:
   print ("Match 2")

match = re.search(pattern, "We scattered.")
if match:
   print ("Match 3")
