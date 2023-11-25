import httpx
from selectolax.parser import HTMLParser
from dataclasses import dataclass
from urllib.parse import urljoin
from rich import print
import csv

@dataclass
class Response:
    body_html: HTMLParser
    next_page: dict

@dataclass
class Product:
    name: str
    selling_price: str
    original_price: str
    warranty: str
    width: str
    depth: str
    height: str
    color: str
    material: str

def get_page(client, url): # to get all the different listings on main page
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
    }
    r = client.get(url, headers=headers)
    html = HTMLParser(r.text)
    if html.css_first("a[title=next]"):
        next_page = html.css_first("a[title=next]").attributes
    else:
        next_page = {"href": False}
    return Response(body_html=html, next_page=next_page)

def parse_links(html): # from the main page, get the link to individual listing
    links = html.css("ul#catalog-listing > li > div > div > a")
    return set(link.attrs["href"] for link in links)

def pagination_loop(client): # loop through different main pages, and get the links to the individual listings of each main page
    url = "https://www.fortytwo.sg/study-room/study-desk.html"
    page = get_page(client, url)
    links = parse_links(page.body_html)
    while page.next_page["href"]:
        url = page.next_page["href"]
        page = get_page(client,url)
        links |= parse_links(page.body_html)
    return links

def detail_page_loop(client, links): # from each individual listing page, get the necessary information
    products = []
    n = 0
    for url in links:
        print(url)
        page = get_page(client, url)
        new_product = parse_detail(page.body_html)
        if new_product.name == "None":
            continue
        products.append(parse_detail(page.body_html))
        print(f"product {n}: {new_product}")
        n += 1
        if n % 20 == 0:
            print("current product: ", n)
    return products

def extract_info(html, selector, index):
    try:
        return html.css(selector)[index].text(strip=True)
    except IndexError:
        return "None" # if that info don't exist, return a readable none

def parse_detail(html): # what kind of data you want from each individual listing
    new_product = Product(
        name = extract_info(html, "h1[itemprop=name]", 0),
        selling_price = extract_info(html, "p.special-price > span.price", 0),
        original_price = extract_info(html, "p.old-price > span.price", 0),
        warranty = extract_info(html, "div.warranty-information", 0),
        width = extract_info(html, "table#product-attribute-specs-table-1 > tbody > tr:nth-child(2) > td.data", 0),
        depth = extract_info(html, "table#product-attribute-specs-table-1 > tbody > tr:nth-child(3) > td.data", 0),
        height = extract_info(html, "table#product-attribute-specs-table-1 > tbody > tr:nth-child(4) > td.data", 0),
        color = extract_info(html, "table#product-attribute-specs-table-2 > tbody > tr:nth-child(1) > td.data", 0),
        material = extract_info(html, "table#product-attribute-specs-table-2 > tbody > tr:nth-child(2) > td.data", 0),
    )
    return new_product

def export_csv(products):
    with open("fortytwo_studydesk.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "selling_price", "original_price", "warranty", "width", "depth", "height", "color", "material"])
        for product in products:
            writer.writerow([product.name, product.selling_price, product.original_price, product.warranty, product.width, product.depth, product.height, product.color, product.material])
    print("[green]CSV file exported![/green]")

def main():
    client = httpx.Client()
    links = pagination_loop(client)
    products = detail_page_loop(client, links)
    export_csv(products)

if __name__ == "__main__":
    main()