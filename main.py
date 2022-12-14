import asyncio
import csv
import json
import time
from typing import Union
import aiohttp
import pandas as pd
import pymongo
import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import *

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
    max_age=3600,
)


class Search:
    def __init__(self, search_term):
        self.search_term = search_term
        with open('output.csv', 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(
                f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(['store', 'name', 'price', 'link', 'image', 'id'])

    def alta(self):
        url = f'https://alta.ge/?subcats=Y&pcode_from_q=Y&pshort=Y&pfull=Y&pname=Y&pkeywords=Y&search_performed=Y&q={self.search_term}&dispatch=products.search&items_per_page=1000'
        r = requests.get(url.format(search_term=self.search_term))
        soup = BeautifulSoup(r.text, 'html.parser')
        products = soup.find_all('div', attrs={'class': 'ty-column3'})
        tags = soup.find_all('a', attrs={'class': 'product-title'})
        prices = soup.find_all('span', attrs={'class': 'ty-price-num'})
        # images = soup.find_all('img', attrs={'class': 'ty-pict    '})
        num = 0
        with open('output.csv', 'a', encoding='utf-8', newline='') as f:
            output = ''
            writer = csv.writer(
                f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for product, tag, price in zip(products, tags, prices):
                num += 1
                name = tag.text.strip()
                link = product.find('a', class_='product-title').get('href')
                amount = price.text.strip()
                # thumbnail = image['src']
                output = "Alta", name, f"{amount}", link
                writer.writerow(["Alta", name, f"{amount}", link])
            return output

    def ee(self):
        url = "https://api.ee.ge/07072022/product/filter_products"
        payload = {
            "min_price": 0,
            "max_price": 0,
            "category": "",
            "sort_by": "",
            "item_per_page": 1000,
            "page_no": "",
            "search_text": self.search_term,
            "sale_products": 0,
            "slug": "",
            "pageno": ""
        }
        r = requests.request("POST", url, json=payload)
        num = 0
        with open('output.csv', 'a', encoding='utf-8', newline='') as f:
            output = ''
            writer = csv.writer(
                f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for item in r.json()["data"]:
                num += 1
                a = item["parent_category_slug_gr"]
                b = item["category_slug_gr"]
                c = item["product_slug_gr"]
                output = 'Elit', item["product_desc"], f'{item["actual_price"]}', f'https://ee.ge/{a}/{b}/{c}', item['image']
                writer.writerow(['Elit', item["product_desc"],
                                f'{item["actual_price"]}', f'https://ee.ge/{a}/{b}/{c}', item['image']])
            return output

    def ada(self):
        url = "https://api.adashop.ge/api/v1/products/rest_search/search"
        payload = {"search": self.search_term}
        r = requests.request("POST", url, json=payload)
        num = 0
        with open('output.csv', 'a', encoding='utf-8', newline='') as f:
            output = ''
            writer = csv.writer(
                f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for item in r.json()["searched_products"]:
                num += 1
                output = 'Ada', item["name"], f'{item["price_with_price_tag"]}', f'https://adashop.ge/product/{item["_id"]}', f'https://adashop.ge/_next/image?url=http%3A%2F%2Flocalhost%3A5001%2Fimages%2Fproducts%2F{item["image"]}&w=640&q=75'
                writer.writerow(['Ada', item["name"], f'{item["price_with_price_tag"]}', f'https://adashop.ge/product/{item["_id"]}',
                                f'https://adashop.ge/_next/image?url=http%3A%2F%2Flocalhost%3A5001%2Fimages%2Fproducts%2F{item["image"]}&w=640&q=75'])
            return output

    def zoomer(self):
        url = f'https://zoommer.ge/search?q={self.search_term}&CategoryIds=0'
        r = requests.get(url)
        soup = BeautifulSoup(r.content, 'html.parser')
        products = soup.find_all('h4')
        prices = soup.find_all('div', {'class': 'product_new_price'})
        links = soup.find_all(
            'a', attrs={'class': 'carousel-inner product_link'})
        num = 0
        print(products, prices, links)
        with open('output.csv', 'a', encoding='utf-8', newline='') as f:
            writer = csv.writer(
                f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for product, price, link in zip(products, prices, links):
                num += 1
                name = product['title']
                cost = price.text.strip().replace('???', '')
                domain = link.get('href')
                output = "Zoomer", name, cost, f'https://zoommer.ge{domain}'
                writer.writerow(
                    ["Zoomer", name, cost, f'https://zoommer.ge{domain}'])

        # imgsoup = BeautifulSoup(r.text, 'xml')
        # images = imgsoup.find_all(
        #     'img', {'class': 'd-block w-100 product_img'})
        # for image in images:
        #     data = {'image': [image['data-src']]}
        #     df = pd.DataFrame(data)
        #     df.to_csv('output.csv', mode='a', index=False)

        mores = soup.find_all('a', attrs={'class': 'show_more_btn'})
        for more in mores:
            page = more.get('href')
            if page is not None:
                r1 = requests.get(page)
                soup1 = BeautifulSoup(r1.content, 'html.parser')
                products1 = soup1.find_all('h4')
                prices1 = soup1.find_all(
                    'div', attrs={'class': 'product_new_price'})
                links1 = soup1.find_all(
                    'a', attrs={'class': 'carousel-inner product_link'})
                iamges1 = soup1.find_all(
                    'img', {'class': 'd-block w-100 product_img'})
            with open('output.csv', 'a', encoding='utf-8', newline='') as f1:
                writer1 = csv.writer(
                    f1, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                for product1, price1, link1 in zip(products1, prices1, links1):
                    num += 1
                    name1 = product1['title']
                    cost1 = price1.text.strip().replace('???', '')
                    domain1 = link1.get('href')
                    output1 = f'Zoomer | {num} | {name1} | {cost1} | https://zoommer.ge{domain1}'
                    writer1.writerow(
                        ["Zoomer", name1, cost1, f'https://zoommer.ge{domain1}'])

    def all(self):
        self.alta()
        self.ee()
        self.ada()
        self.zoomer()

    def test1(self):
        client = pymongo.MongoClient(
            'mongodb+srv://nav:BuS9KbKz0VT4Zx8m@cluster0.d8y51mh.mongodb.net/?retryWrites=true&w=majority')
        db = client['searcher']
        posts = db.requests
        collection = posts.find({'store': self.search_term})
        if self.search_term == '':
            collection = posts.find({})
        for item in collection:
            with open('output.csv', 'a', encoding='utf-8', newline='') as f:
                writer = csv.writer(
                    f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                writer.writerow([item['store'], item['name'],
                                item['price'], item['link'], item['image']])


def sort():
    df = pd.read_csv("output.csv")
    df['id'] = df.index
    try:
        df['price'] = df['price'].astype(str).str.strip()
        df['price'] = df['price'].astype(str).str.replace('??', '')
        df['price'] = df['price'].astype(int)
    except ValueError:
        df['price'] = df['price'].astype(float).astype(int)
    # df = df.sort_values(by="price")
    df.to_csv("output.csv", index=False)
    print('\nsorted!')


@app.post("/search-item")
async def search(item: str, store: Union[str, None] = None):
    fsearch = Search(item)
    if store is not None:
        store = store.replace(' ', '')
        store = store.split(',')
        options = {
            'alta': fsearch.alta,
            'ee': fsearch.ee,
            'elitelectronics': fsearch.ee,
            'ada': fsearch.ada,
            'adashop': fsearch.ada,
            'zoomer': fsearch.zoomer,
            'all': fsearch.all,
            "test1": fsearch.test1,
        }
        for thing in store:
            thing = thing.lower()
            options[thing]()
    elif store is None:
        fsearch.all()

    sort()
    df = pd.read_csv('output.csv')
    df.to_json('output.json', orient='records')
    with open('output.json') as jf:
        parsed = json.load(jf)
        return parsed
