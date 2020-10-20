from urllib.request import urlopen
from bs4 import BeautifulSoup
from scrape.item import Item

def scrape(url):
    page = urlopen(url)

    html = page.read().decode("utf-8")
    soup = BeautifulSoup(html, "html.parser")

    ul = soup.find('ul', {'class': 'topic-list partial'});

    items = []
    for li in ul.find_all('li'):
        li_text = li.text
        last_space = li_text.rfind(' ')
        title = li_text[0:last_space]
        view = li_text[last_space+1:]

        if li.a is not None:
            link = li.a['href']
            items.append(Item(title, int(view), link))

    sorted_items = sorted(items, key=lambda x: x.view, reverse=True)[:10]
    for item in sorted_items:
        print(item)

