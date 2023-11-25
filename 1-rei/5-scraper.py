# to exract information from individual listings

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

def extract_info(html, selector, index): # index is for the case of multiple elements with the same selector
    try:
        return html.css(selector)[index].text(strip=True)
    except IndexError:
        return "None" # if that information doesn't exist for that specific listing, then at least we get readable output
    
def parse_detail(html):
    new_product = Product(
        name=extract_info(html, "h1.product-title", 0), # 0 is the index of the first element with that selector
        sku=extract_info(html, "span.sku", 0),
        price=extract_info(html, "span.price-value", 0),
        rating=extract_info(html, "span.cdr-rating__number_13-5-3", 0),
    )
    return new_product

def parse_links(html):
    links = html.css("div#search-results > ul > li > a")
    return set(link.attrs["href"] for link in links) # use set to get the non duplicated

def pagination_loop(client): # returns all pages of the individual backpacks listings
    url = "https://www.rei.com/c/backpacks" 
    page = get_page(client,url)
    links = parse_links(page.body_html)
    while page.next_page["href"]:
        url = urljoin(url, page.next_page["href"])
        page = get_page(client,url)
        links |= parse_links(page.body_html) # union the links
    return links

def detail_page_loop(client, links):
    products = []
    for link in links:
        url = urljoin("https://www.rei.com", link)
        page = get_page(client, url)
        products.append(parse_detail(page.body_html))
    return products

def export_csv(products):
    with open("products.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "sku", "price", "rating"])
        for product in products:
            writer.writerow([product.name, product.sku, product.price, product.rating])
    print("[green]CSV file exported![/green]")

def main():
    client = httpx.Client()
    links = pagination_loop(client)
    products = detail_page_loop(client, links)
    export_csv(products)
    
if __name__ == "__main__":
    main()