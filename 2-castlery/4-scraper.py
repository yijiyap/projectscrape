# for pagination, we need to get the next page link and then parse the links from that page.

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
    price: str

@dataclass
class Response:
    body_html: HTMLParser
    next_page: str

def get_page(client, url, n):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
    }
    urlPage = url[:-1] + f"{n}" 
    r = client.get(urlPage, headers=headers)
    html = HTMLParser(r.text)
    # check if the current page is in range by checking for presence of a div with the data-qa attribute of hits
    if html.css_first("div[data-qa=hits]"):
        next_page = url[:-1] + f"{n+1}"
    else:
        next_page = "None"
    return Response(body_html=html, next_page=next_page)

def extract_info(html, selector, index):
    try:
        return html.css(selector)[index].text(strip=True)
    except IndexError:
        return "None"

def parse_detail(html):
    new_product = Product(
        name=extract_info(html, "h1", 0),
        price=extract_info(html, "span[data-selenium=product-price]", 0),
    )
    return new_product

def parse_listings(html):
    listings = html.css("div[data-qa=hits] > div > div > div > a")
    return set(link.attrs["href"] for link in listings)

def pagination_loop(client): # returns all pages of individual sofa listings
    url = "https://www.castlery.com/sg/sofas/all-sofas?p=1"
    page_num = 1
    page = get_page(client, url, page_num)
    links = parse_listings(page.body_html)
    while page.next_page != "None":
        print("current page: ", page_num)
        page = get_page(client,page.next_page, page_num)
        links |= parse_listings(page.body_html) # union the links
        print("links: ", len(links))
        page_num += 1
    return links

def detail_page_loop(client, links):
    products = []
    for link in links:
        url = urljoin("https://www.castlery.com", link)
        r = client.get(url)
        html = HTMLParser(r.text)
        products.append(parse_detail(html))
    return products

def export_csv(products):
    with open("products.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "price"])
        for product in products:
            writer.writerow([product.name, product.price])
    print("[green]CSV file exported![/green]")

def main():
    client = httpx.Client()
    links = pagination_loop(client)
    products = detail_page_loop(client, links)
    export_csv(products)

if __name__ == "__main__":
    main()