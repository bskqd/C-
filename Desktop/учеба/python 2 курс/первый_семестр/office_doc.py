from docx import Document
import re

from datetime import datetime


DATE1 = r"\b\d{1,2}\.\d{1,2}\.\d{1,4}"  # 12.3.1999
DATE2 = r"\b\_\_\.\_\_\.\_\_\_\_"  # __.__.____
DATE = DATE1 + "|" + DATE2


def _change_date(match):
    date = match.group()
    d, m, y = date.split(".")
    if '_' in date:
        d = datetime.today().strftime('%d')
        m = datetime.today().strftime('%m')
        y = datetime.today().strftime('%Y')
    date = ".".join((d, m, y))
    return date


def change_dates(string):
    return re.sub(DATE, _change_date, string)


def change_dates_docx(document):
    doc = Document(document)

    for paragraph in doc.paragraphs:
        paragraph.text = change_dates(paragraph.text)

    doc.save(document)


if __name__ == '__main__':
    change_dates_docx("office_doc.docx")
