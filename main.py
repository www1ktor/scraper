import requests
from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
import csv

listings = []

OTODOM_PL = "https://www.otodom.pl/"
base_url = OTODOM_PL + "pl/wyniki/sprzedaz/mieszkanie/wielkopolskie/poznan/poznan/poznan?limit=36&ownerTypeSingleSelect=ALL&priceMax=355553&by=DEFAULT&direction=DESC"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/119.0 Safari/537.36'
}

response = requests.get(base_url + '1', headers=headers)
soup = BeautifulSoup(response.content, 'lxml')

pages = soup.find(attrs={'data-sentry-component':'ItemsCounter'}).get_text(strip=True)[2:]
 

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

    for thumbnail in soup.find_all(attrs={'data-cy':'listing-item'}):
        rooms = thumbnail.find(attrs={'data-sentry-component':'RoomsDefinition'})
        floor = thumbnail.find(attrs={'data-sentry-component':'FloorsDefinition'})
        title = thumbnail.find(attrs={'data-cy' : 'listing-item-title'})
        localisation = thumbnail.find(attrs={'data-sentry-component':'Address'})

        for dt in thumbnail.find_all("dt"):
            if "Powierzchnia" in dt.get_text(strip=True):
                dd = dt.find_next_sibling("dd")
                if dd:
                    area = dd

        link = OTODOM_PL[:-1] + thumbnail.find(attrs={'data-cy' : 'listing-item-link'}).get("href")
        
        listing = requests.get(link, headers=headers)
        offer = BeautifulSoup(listing.content, 'lxml')

        id = offer.find(attrs={'data-sentry-element':'DetailsContainer'})
        price = offer.find(attrs={'data-sentry-element':'Price'})
        price_per_meter = offer.find(attrs={'aria-label':'Cena za metr kwadratowy'})
        
        items = offer.find_all(attrs={'data-sentry-element':"Item"})

        for p in items:
            label = p.get_text(strip=True).replace(":", "")
            sibling = p.find_next_sibling()
            value = sibling.get_text(strip=True) if sibling else None

            if label == 'Czynsz':
                rent = value
            elif label == 'Winda':
                elevator = value

        driver = webdriver.Chrome()
        driver.get(link)
        description = str(driver.find_element(By.CSS_SELECTOR, '[data-sentry-element="DescriptionWrapper"]').text)
        driver.quit()
        
        details = {
            'ID: ' : str(id.get_text(strip=True))[3:].lstrip(' '),
            'Cena: ' : price, 
            'Powierzchnia: ' : area,
            'Cena za metr: ' : price_per_meter, 
            'Pokoje: ' : rooms,
            'Lokalizacja: ' : localisation,
            'Piętro: ' : floor,
            'Winda: ' : elevator,
            'Czynsz: ' : rent,
            'Tytuł: ' : title, 
            'Opis: ' : description,
            'Link: ': link
        }

        for k, v in zip(details.keys(), details.values()):
            if v and type(v) is not str:
                v = v.get_text(strip=True)
            
            print(k, v)


        listings.append(details)

        time.sleep(5)

with open('data.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=details.keys())
    writer.writeheader()
    writer.writerows(listings)

 




