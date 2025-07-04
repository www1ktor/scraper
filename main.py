import requests
from bs4 import BeautifulSoup
import time

OTODOM_PL = "https://www.otodom.pl/"
base_url = OTODOM_PL + "pl/wyniki/sprzedaz/mieszkanie/wielkopolskie/poznan/poznan/poznan?limit=36&ownerTypeSingleSelect=ALL&priceMax=355553&by=DEFAULT&direction=DESC"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/119.0 Safari/537.36'
}

response = requests.get(base_url + '1', headers=headers)
soup = BeautifulSoup(response.content, 'lxml')

pages = soup.select_one(".css-15svspy.eawphu90").get_text(strip=True)[2:]

pages_start = ''
pages_stop = ''

for char in pages:
    if char != ' ': 
        pages_start += char
    else:
        break

for char in pages[::-1]:
    if char != ' ': 
        pages_stop += char
    else:
        break

pages_start = int(pages_start)
pages_stop = int(pages_stop[::-1])

n_pages = int(pages_stop/pages_start)

if pages_stop % pages_start != 0:
    n_pages += 1

results = []

for page in range(1, n_pages + 1):
    print(page)
    
    response = requests.get(base_url + f"&page={str(page)}", headers=headers)
    soup = BeautifulSoup(response.content, 'lxml')

    for offer in soup.find_all(attrs={'data-cy':'listing-item'}):
        #print(offer)
        rooms = offer.find(attrs={'data-sentry-component':'RoomsDefinition'})
        floor = offer.find(attrs={'data-sentry-component':'FloorsDefinition'})
        title = offer.find(attrs={'data-cy' : 'listing-item-title'})
        localisation = offer.find(attrs={'data-sentry-component':'Address'})

        for dt in offer.find_all("dt"):
            if "Powierzchnia" in dt.get_text(strip=True):
                dd = dt.find_next_sibling("dd")
                if dd:
                    area = dd

        link = OTODOM_PL[:-1] + soup.find(attrs={'data-cy' : 'listing-item-link'}).get("href")
        


        listing = requests.get(link, headers=headers)
        data = BeautifulSoup(listing.content, 'lxml')

        id = data.find(attrs={'data-sentry-element':'DetailsContainer'})
        price = data.find(attrs={'data-sentry-element':'Price'})
        #area = data.find(attrs={'aria-label':'Cena za metr kwadratowy'}).get_text(strip=True)
        price_per_meter = data.find(attrs={'aria-label':'Cena za metr kwadratowy'})
        
        #rent = data.find(attrs={'aria-label':'Cena za metr kwadratowy'}).get_text(strip=True)
        #description = data.find(attrs={'aria-label':'Cena za metr kwadratowy'}).get_text(strip=True)

        details = {
            'ID: ' : str(id.get_text(strip=True))[3:].lstrip(' '),
            'Cena: ' : price, 
            'Powierzchnia: ' : area,
            'Cena za metr: ' : price_per_meter, 
            'Pokoje: ' : rooms,
            'Lokalizacja: ' : localisation,
            'Piętro: ' : floor,
            
            'Tytuł: ' : title, 
            
            'Link: ': link
        }
        #print(id, price, area, price_per_meter, rooms, localisation, floor, rent, title, description, link)

        for k, v in zip(details.keys(), details.values()):
            if v and k != 'Link: ' and k != 'ID: ':
                print(k, v.get_text(strip=True))
            else:
                print(k, v)

        #soup.find_all()


    time.sleep(1)

 




