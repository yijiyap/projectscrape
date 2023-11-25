import httpx
from selectolax.parser import HTMLParser
from dataclasses import dataclass
from urllib.parse import urljoin
from rich import print
import csv

@dataclass
class Product:
    name: str
    price: str
    condition: str
    posted_time: str
    seller_name: str
    url: str
    description: str

def get_page(client, url): # return the html of the main page
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) \
            AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
    }
    r = client.get(url, headers=headers)
    return HTMLParser(r.text)

def parse_links(html): # from the main page, get links to individual listing
    links = html.css("div.D_ST > div.D_sV.D_AI > div.D__w > div.D__x > a.D_nJ")
    all_links = set()
    for link in links:
        if link.attributes["href"][1] == "p": # get only the product links, not the user profile links
            all_links.add(link.attributes["href"]) 
    return all_links

def extract_info(html, selector, index):
    try:
        return html.css(selector)[index].text(strip=True)
    except IndexError:
        return "None" # if that info don't exist, return a readable none

def detail_page_loop(client, links, min_price, max_price): # from each individual listing page, get the necessary information
    products = []
    n = 0
    for url in links:
        url = urljoin("https://www.carousell.sg", url)
        page = get_page(client, url)
        new_product = parse_detail(page, url, min_price, max_price)
        if new_product.name == "None":
            continue
        products.append(new_product)
        n += 1
        print(f"product {n}: {new_product}")
    return products

def parse_detail(html, url, min_price, max_price): # from each individual listing page, get the necessary information
    name = extract_info(html, "h1", 0)
    price = extract_info(html, "h3", 0)
    if (price[2:] and (min_price > float(price[2:]) or float(price[2:]) > max_price)): # if is more than that price, return "None" so that it will be removed later
        return Product("None", "None", "None", "None", "None", "None", "None") 
    condition = extract_info(html, "span.D_nL.D_nF.D_nM.D_nP.D_nT.D_nW.D_nY.D_bcS.D_ob", 0)
    posted_time = extract_info(html, "span.D_nL.D_nE.D_nM.D_nP.D_nT.D_nW.D_nY.D_bcS.D_ob", 1)
    if posted_time == "In":
        posted_time = extract_info(html, "span.D_nL.D_nE.D_nM.D_nP.D_nT.D_nW.D_nY.D_bcS.D_ob", 0)
    seller_name = extract_info(html, "a.D_sE.D_nJ", 0)
    url = url
    description = extract_info(html, "p.D_nL.D_nG.D_nM.D_nQ.D_nT.D_nW.D_nY.D_a_M.D_a_O.D_ob", 0)
    return Product(name, price, condition, posted_time, seller_name, url, description)

def export_csv(products):
    with open("products.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "price", "condition", "posted_time", "seller_name", "url", "description"])
        for product in products:
            writer.writerow([product.name, product.price, product.condition, product.posted_time, product.seller_name, product.url, product.description])
    print("[green]CSV file exported![/green]")

def scraper(url, min_price, max_price):
    client = httpx.Client()
    page = get_page(client, url)
    links = parse_links(page)
    products = detail_page_loop(client, links, min_price, max_price)
    export_csv(products)
