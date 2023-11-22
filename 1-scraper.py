# to get all the next pages of the backpacks listings

import httpx
from selectolax.parser import HTMLParser
from dataclasses import dataclass
from urllib.parse import urljoin
from rich import print

@dataclass
class Product:
    name: str
    sku: str
    price: str # keep as string until we need to do math
    rating: str

@dataclass
class Response: # to store the HTML to see next pages and whatnot
    body_html: HTMLParser
    next_page: dict

def get_page(client, url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
    }
    r = client.get(url, headers=headers)
    html = HTMLParser(r.text)
    if html.css_first("a[data-id=pagination-test-link-next]"): # check if next page exists by the presence of the next button
        next_page = html.css_first("a[data-id=pagination-test-link-next]").attributes
    else: 
        next_page = {"href": False}
    return Response(body_html=html, next_page=next_page)

def main():
    client = httpx.Client()
    url = "https://www.rei.com/c/backpacks?page=22"
    print(get_page(client,url))

if __name__ == "__main__":
    main()