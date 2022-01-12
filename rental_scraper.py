#Known Imports
import time
from datetime import datetime, timedelta
import json
import requests
from bs4 import BeautifulSoup
from discord_webhook import DiscordWebhook, DiscordEmbed
from discord import Webhook, RequestsWebhookAdapter
import locale
import config

locale.setlocale(locale.LC_ALL, 'en_US')

url = search_url
webhook = DiscordWebhook(url=webhook_url, adapter=RequestsWebhookAdapter())
tmpDict = {}
masterDict = {}

class Property:
    def __init__(self, sale, homeType, address, price, tax, link, bed, bath, sqft, parkingSpots):
        # use unformattedPrice 
        self.sale    = sale
        self.type    = homeType
        self.address = address
        self.price   = price
        self.tax     = tax
        self.link    = link
        self.bed     = bed
        self.bath    = bath
        self.sqft    = sqft
        self.parking = parkingSpots
    def __repr__(self):
        return f'{self.__class__.__name__}({self.sale!r}, {self.homeType!r}, {self.address!r}, {self.price}, {self.tax}, {self.link!r}, {self.bed}, {self.bath}, {self.sqft}, {self.parkingSpots})'
    def __eq__(self, other):
        return self.price == other.price
    def __lt__(self, other):
        return self.price < other.price

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0"
}

soup = BeautifulSoup(requests.get(url, headers=headers).content, "html.parser")

data = json.loads(
    soup.select_one("script[data-zrr-shared-data-key]")
    .contents[0]
    .strip("!<>-")
)

# uncomment this to print all data:
#print(json.dumps(data, indent=4))
count = 0

for result in data["cat1"]["searchResults"]["listResults"]:
    print(
        "{:<15} {:<50} {:<15}".format(
            result["statusText"], result["address"], result["price"]
        )
    )

    sale         = result["statusType"]
    homeType     = result["hdpData"]["homeInfo"]["homeType"]
    address      = result["address"]
    price        = result["unformattedPrice"]
    tax          = result["hdpData"]["homeInfo"]["taxAssessedValue"] #temporary until i figure out tax field
    link         = result["detailUrl"]
    bed          = result["hdpData"]["homeInfo"]["bedrooms"]
    bath         = result["hdpData"]["homeInfo"]["bathrooms"]
    sqft         = result["hdpData"]["homeInfo"]["livingArea"]
    parkingSpots = 0 #temporary until i figure out parking spots

    if result["address"] not in masterDict:
        tmpDict[address] = Property(sale, homeType, address, price, tax, link, bed, bath, sqft, 0)

        count += 1

        ##Notify Discord
        embed = DiscordEmbed(title=sale + " (" + result["addressCity"] + ", " + result["addressState"] + ")",
            description=
            ":moneybag: $"         + locale.format_string("%d", price, grouping=True) +
            "\n:bed:  "            + str(bed).strip('.0') +
            "\t:bath:  "           + str(bath).strip('.0') +
            "\t:straight_ruler:  " + str(sqft).strip('.0') + " ft²" +
            "\n:map: "             + address +
            "\n:bank: $"           + locale.format_string("%d", tax, grouping=True),
            #"\n:red_car:  "        + str("Not Implemted Yet"),
            color='03b2f8', url=link)

        embed.set_image(url=result["imgSrc"])
        #embed.timestamp = datetime.utcnow()
        #embed.set_footer(text='\u200b',icon_url="https://i.imgur.com/uZIlRnK.png")
        webhook.add_embed(embed)
        webhook.execute()

        break
