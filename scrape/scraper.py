import datetime
import threading
from urllib.request import urlopen
from bs4 import BeautifulSoup
from scrape.item import Item
import concurrent.futures
from collections import defaultdict
from dao.repository import insert_records

top_view_count = 20
parallel_call_count = 10
author_minimum_occurrence = 2


def scrape(url, agenda):
    page = urlopen(url + agenda)

    html = page.read().decode("utf-8")
    soup = BeautifulSoup(html, "html.parser")

    # we will find all topics with css class topic-list partial
    ul = soup.find('ul', {'class': 'topic-list partial'})

    items = []
    for li in ul.find_all('li'):
        li_text = li.text  # text of the li is stg like that: epic games store 25
        last_space = li_text.rfind(' ')
        title = li_text[0:last_space]
        view = li_text[last_space + 1:]

        # we should eliminate advertisement section
        if li.a is not None:
            link = li.a['href']
            items.append(Item(title, int(view), link))

    # we need title with top 10 view count
    items = sorted(items, key=lambda x: x.view, reverse=True)[:top_view_count]

    # we will scrape deep down every child, so that we need an array to collect them
    all_authors = []

    # I used concurrent features of python with 10 parallel tasks
    print('Starting execution: ' + str(datetime.datetime.now()))

    # with keyword eqv try-with-resources (java)
    with concurrent.futures.ThreadPoolExecutor(max_workers=parallel_call_count) as executor:

        future_to_scrape = {executor.submit(scrape_child_authors_list, url, item.link): item for item in items}

        for future in concurrent.futures.as_completed(future_to_scrape):
            future_item = future_to_scrape[future]
            try:
                data = future.result()
            except Exception as exception:
                print('%r generated an exception: %s' % (future_item, exception))
            else:
                all_authors.extend(data)

    print('Ending execution: ' + str(datetime.datetime.now()))

    # we will create a dictionary with authors as keys and their topics as value
    authors_grouped = defaultdict(list)
    for k, v in all_authors:
        authors_grouped[k].append(v)

    # we want to show only n+ occurrences of authors among pages
    authors_filtered = {k: v for (k, v) in authors_grouped.items() if len(v) >= author_minimum_occurrence}
    print(authors_filtered)

    if len(authors_filtered) > 0:
        try:
            insert_records(authors_filtered)
        except:
            print("Something went wrong :(")
    else:
        print('No operation will be done')

def scrape_child_authors_list(url, part):
    print('Execution of child with ' + part + ' and thread id: ' + str(threading.get_ident()) + " - " + str(
        datetime.datetime.now()))

    authors = []
    page = urlopen(url + part)

    end_part = part.find('--')  # /masumlar-apartmani--6648335?a=popular'
    part = part[1:end_part]

    html = page.read().decode("utf-8")
    soup = BeautifulSoup(html, "html.parser")

    # we will scrape all li items in the first page with id entry-item-list
    ul = soup.find('ul', {'id': 'entry-item-list'})
    for li in ul.find_all('li'):
        authors.append((li['data-author'], part))

    return authors
