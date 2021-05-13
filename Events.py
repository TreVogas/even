import requests
from bs4 import BeautifulSoup
from urllib.parse import quote, urljoin
import numpy as np
import urllib3
import json
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from datetime import datetime
import time

start_time = datetime.now()
base_url = "https://it-events.com/"

HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                         'Chrome/88.0.4324.190 Safari/537.36', 'accept': '*/*'}
urllib3.disable_warnings()


def get_html(url, params=None):
    r = requests.get(url, headers=HEADERS, params=params, verify=False)  # proxies=proxy
    return r


def get_links(html):  # get links on the events
    soup = BeautifulSoup(html, 'html.parser')
    links = soup.find_all('a', class_='event-list-item__title')
    all_links = []
    for link in links:
        all_links.append('https://it-events.com/' + link.get('href'))
    return all_links


def get_pages_link(html, url_list=[]):  # get the number of pages, which will be scraping
    soup = BeautifulSoup(html, 'html.parser')
    count_page = soup.find_all('a', class_='paging__item')
    for page in count_page:
        if page.text == 'Следующая':
            url = base_url + page.get('href')
            url_list.append(url)
            get_pages_link(get_html(url).content)
            return url_list


def get_pages_info(html):
    soup = BeautifulSoup(html, 'html.parser')
    event_name = soup.find('h1', class_='event-header__title').text
    return event_name


def get_city(html):
    soup = BeautifulSoup(html, 'html.parser')
    event_city = soup.find('a',
                           class_='event-header__line event-header__line_icon event-header__line_icon_location')
    if event_city == None:
        event_city == 0
        return event_city
    event_city = soup.find('a',
                           class_='event-header__line event-header__line_icon event-header__line_icon_location').text
    return event_city


def get_type_of_event(html):
    soup = BeautifulSoup(html, 'html.parser')
    event_type = soup.find('div', class_='event-header__line event-header__line_icon event-header__line_icon_online')
    if event_type is None:
        event_type == 0
        return event_type
    event_type = soup.find('div',
                           class_='event-header__line event-header__line_icon event-header__line_icon_online').text
    return event_type


def get_price(html):
    soup = BeautifulSoup(html, 'html.parser')
    event_price = soup.find('div',
                            class_='event-header__line event-header__line_icon event-header__line_icon_price').text
    return event_price


def get_day(html):
    soup = BeautifulSoup(html, 'html.parser')
    event_day = soup.find('div', class_='event-header__line event-header__line_bold event-header__line_icon').text
    return event_day


def get_reg(html):
    soup = BeautifulSoup(html, 'html.parser')
    event_reg = soup.find('button', class_='button').text
    return event_reg


z = True
while z is True:

    html = get_html(base_url)
    paper = get_pages_link(html.content)
    paper.insert(0, base_url)
    events = np.array([])
    for link in paper:
        html = get_html(link)
        events = np.append(events, get_links(html.content))

    info = {}
    number = 0
    for event in events:
        html = get_html(event).content
        soup = BeautifulSoup(html, 'html.parser')
        event_info = {}
        event_info = get_pages_info(html)
        city = get_city(html)
        price = get_price(html)
        typo = get_type_of_event(html)
        day = get_day(html)
        reg = get_reg(html)
        info[number] = [event_info, event, city, typo, price, day, reg]
        number = number + 1

    print(info)
    s = json.dumps(info, ensure_ascii=False)
    print(s)

    with open('a.json', 'wb') as file_end:  # wb - write bytes
        file_end.write(bytes(s, encoding='utf-16'))
    cred = credentials.Certificate(r'projects-d0f06-firebase-adminsdk-36fer-ef3ed002bd.json')
    default_app = firebase_admin.initialize_app(cred, {'databaseURL': 'https://projects-d0f06-default-rtdb.firebaseio.com/'})

    ref = db.reference("/")
    firebase_json = ref.get()
    ref.update(info)
    print(datetime.now() - start_time)
    time.sleep(300)