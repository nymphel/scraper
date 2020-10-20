from urllib.request import urlopen
from bs4 import BeautifulSoup
from scrape.item import Item
import concurrent.futures
from collections import Counter

def scrape(url, agenda):
    page = urlopen(url + agenda)

    html = page.read().decode("utf-8")
    soup = BeautifulSoup(html, "html.parser")

    ul = soup.find('ul', {'class': 'topic-list partial'})

    items = []
    for li in ul.find_all('li'):
        li_text = li.text
        last_space = li_text.rfind(' ')
        title = li_text[0:last_space]
        view = li_text[last_space + 1:]

        if li.a is not None:
            link = li.a['href']
            items.append(Item(title, int(view), link))

    items = sorted(items, key=lambda x: x.view, reverse=True)[:10]

    all_authors = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:

        future_to_scrape = {executor.submit(scrape_child_authors_list, (url + item.link)): item for item in items}
        for future in concurrent.futures.as_completed(future_to_scrape):
            return_of_future = future_to_scrape[future]
            try:
                data = future.result()
            except Exception as exception:
                print('%r generated an exception: %s' % (return_of_future, exception))
            else:
                all_authors.extend(data)

    authors_grouped = dict(Counter(all_authors))
    authors_filtered = {k:v for (k,v) in authors_grouped.items() if v > 1}
    print(authors_filtered)

def scrape_child_authors_list(url):
    authors = []
    page = urlopen(url)

    html = page.read().decode("utf-8")
    soup = BeautifulSoup(html, "html.parser")
    ul = soup.find('ul', {'id': 'entry-item-list'})
    for li in ul.find_all('li'):
        authors.append(li['data-author'])

    return authors
