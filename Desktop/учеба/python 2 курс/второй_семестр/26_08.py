import re
from urllib.request import urlopen

from bs4 import BeautifulSoup

ASTRO_DESC = r'<p>(?P<content>.+)</p>'


def download_examples(astro):
    main_url = "https://elle.ua/astro/"

    astro_url_today = main_url + f'{astro}/'
    astro_url_tomorrow = main_url + f'{astro}/' + 'tomorrow/'

    web_soup_today = BeautifulSoup(urlopen(astro_url_today), features="html.parser")
    desc_div_today = web_soup_today.find(name="div", attrs={'class': 'zodiac-desc'})

    web_soup_tomorrow = BeautifulSoup(urlopen(astro_url_tomorrow), features="html.parser")
    desc_div_tomorrow = web_soup_tomorrow.find(name="div", attrs={'class': 'zodiac-desc'})

    print('TODAY: ', find_prediction(str(desc_div_today)))
    print('TOMORROW: ', find_prediction(str(desc_div_tomorrow)))


def find_prediction(html):
    return re.search(ASTRO_DESC, html).group('content')


if __name__ == '__main__':
    download_examples('taurus')
