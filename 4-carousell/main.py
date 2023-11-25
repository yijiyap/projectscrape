# set the item you want, below what price to notify you on telegram. how often you want the bot to check for you

from scraper import scraper # import the scraper function from scraper.py

def main():
    item = input("Please enter the item you wish to get reminders for: ")
    item = item.replace(" ", "%20")
    min_price = float(input("Please enter a minimum price: "))
    max_price = float(input("Please enter a maximum price: "))
    # interval = int(input("Please enter an interval (in hours): "))
    # telegram_token = input("Please enter your telegram bot token: ")
    # telegram_chat_id = input("Please enter your telegram chat id: ")
    url = f"https://www.carousell.sg/search/{item}?sort_by=3"
    scraper(url, float(min_price), float(max_price))

if __name__ == "__main__":
    main()