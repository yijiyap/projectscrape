# to get all the next pages of the sofas listings

import httpx
from selectolax.parser import HTMLParser
from dataclasses import dataclass
from urllib.parse import urljoin
from rich import print
import json
import csv

@dataclass
class Product:
    name: str
    sku: str
    price: str
    rating: str # store the html for now. all are SVGs. looks sussy 

@dataclass
class Response:
    body_html: HTMLParser
    next_page: str

def get_page(client, url, n):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
    }
    urlPage = url + f"?p={n}"
    r = client.get(urlPage, headers=headers)
    html = HTMLParser(r.text)
    # check if the current page is in range by checking for presence of a div with the data-qa attribute of hits
    if html.css_first("div[data-qa=hits]"):
        next_page = url + f"?p={n+1}"
    else:
        next_page = "None"
    return Response(body_html=html, next_page=next_page)

def parse_listings(html):
    listings = html.css("div[data-qa=hits] > div > div > div > a")
    return set(link.attrs["href"] for link in listings)

def main():
    client = httpx.Client()
    url = "https://www.castlery.com/sg/sofas/all-sofas"
    page = get_page(client,url, 1)
    print(parse_listings(page.body_html))


if __name__ == "__main__":
    main()