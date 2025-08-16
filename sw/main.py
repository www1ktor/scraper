import requests
from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import chromedriver_autoinstaller
import csv

listings = []
multiadvert_links = []
err = []
ids = []

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/119.0 Safari/537.36'
}

OTODOM_PL = "https://www.otodom.pl"
base_url = OTODOM_PL + "/pl/wyniki/sprzedaz/mieszkanie/wielkopolskie/poznan/poznan/poznan?limit=36&ownerTypeSingleSelect=ALL&priceMax=355553&by=DEFAULT&direction=DESC"
PRICE_FILTER = "?priceMax=355553"

def single():
    chromedriver_autoinstaller.install()

    options = Options()
    options.add_argument('--headless')  
    options.add_argument('--disable-gpu')  
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")

    service = Service()
    driver = webdriver.Chrome(options=options)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/119.0 Safari/537.36'
    }

    response = requests.get(base_url + '/1', headers=headers)
    soup = BeautifulSoup(response.content, 'lxml')
    time.sleep(2)
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
    
    for page in range(1, n_pages + 1):
        response = requests.get(base_url + f"/&page={str(page)}", headers=headers)
        soup = BeautifulSoup(response.content, 'lxml')
        
        for thumbnail in soup.find_all(attrs={'data-sentry-component':'AdvertCard'}):
            time.sleep(2)
            id, price, area, price_per_meter, rooms, address, district, administrative_area, city, voivodeship, floor, elevator, rent, title, link = None, None, None, None, None, None, None, None, None, None, None, None, None, None, None
            
            try:
                title = thumbnail.find(attrs={'data-cy' : 'listing-item-title'})
                localisation = thumbnail.find(attrs={'data-sentry-component':'Address'}).get_text(strip=True)
                link = OTODOM_PL + thumbnail.find(attrs={'data-cy' : 'listing-item-link'}).get("href")
                keys = ['Ulica', 'Dzielnica', 'Obszar administracyjny', 'Miasto', 'Województwo'][::-1]
                localisation = localisation.split(',')[::-1]

                address = { key: val for key, val in zip(keys, localisation) }    

                for dt in thumbnail.find_all("dt"):
                    if "Piętro" in dt.get_text(strip=True):
                        dd = dt.find_next_sibling("dd")
                        if dd:
                            floor = dd
                            
                link = OTODOM_PL + thumbnail.find(attrs={'data-cy' : 'listing-item-link'}).get("href")
                
                listing = requests.get(link, headers=headers)
                offer = BeautifulSoup(listing.content, 'lxml')
                time.sleep(2)
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

                        if rent.startswith('.css'):
                            rent = "brak informacji"
                        elif rent.endswith('zł'):
                            rent = rent.strip()

                    elif label == 'Winda':
                        elevator = value
                        
                    elif label == "Powierzchnia":
                        area = value
                        
                    elif label == "Liczba pokoi":
                        rooms = value

                driver.get(link)
                html = driver.page_source
                #description = str(driver.find_element(By.CSS_SELECTOR, '[data-sentry-element="DescriptionWrapper"]').text)

                if '/hpr/' in link:
                    pass
                
                id = str(id.get_text(strip=True))[3:].lstrip(' ')
                
                if id not in ids:
                    ids.append(id)
                    
                    details = {
                        'ID' : id,
                        'Cena' : price, 
                        'Powierzchnia' : area,
                        'Cena za metr' : price_per_meter, 
                        'Pokoje' : rooms,
                        'Ulica' : address.get('Ulica', ''),
                        'Dzielnica' : address.get('Dzielnica', ''),
                        'Obszar administracyjny' : address.get('Obszar administracyjny', ''), 
                        'Miasto' : address.get('Miasto', ''),
                        'Województwo' : address.get('Województwo', ''),
                        'Piętro' : floor,
                        'Winda' : elevator,
                        'Czynsz' : rent,
                        'Tytuł' : title, 
                        'Link': link
                    }

                    listing = {}

                    for k, v in zip(details.keys(), details.values()):
                        if v and type(v) is not str:
                            v = v.get_text(strip=True)
                        
                        listing[k] = v
                        #print(k, v)

                    listings.append(listing)
                    
                else:
                    pass
                

                #print(listings)
            
            except:
                if link:
                    print(Exception)
                    err.append(link)
                else:
                    err.append("ERROR")
        
        for thumbnail in soup.find_all(attrs={'data-sentry-component':'CombinedInvestmentCard'}):
            try:
                link = OTODOM_PL + thumbnail.find(attrs={'data-cy' : 'listing-item-link'}).get("href")
                
                if link not in multiadvert_links:
                    multiadvert_links.append(link)
            except:
                pass
            
            

    driver.quit()
    print(multiadvert_links)
#multiadvert_links = ['https://www.otodom.pl/pl/oferta/rezydencja-san-petrus-ID4wZGn', 'https://www.otodom.pl/pl/oferta/os-lotnictwa-polskiego-12-ID4u9wv', 'https://www.otodom.pl/pl/oferta/naramowicka-172-ID4wW7M', 'https://www.otodom.pl/pl/oferta/naramowicka-172-ID4wW7M', 'https://www.otodom.pl/pl/oferta/nadolnik-compact-apartments-ID45iR1', 'https://www.otodom.pl/pl/oferta/nadolnik-compact-apartments-ID45iR1', 'https://www.otodom.pl/pl/oferta/rezydencja-san-petrus-ID4wZGn', 'https://www.otodom.pl/pl/oferta/nadolnik-compact-apartments-ID45iR1', 'https://www.otodom.pl/pl/oferta/rezydencja-san-petrus-ID4wZGn', 'https://www.otodom.pl/pl/oferta/naramowicka-172-ID4wW7M', 'https://www.otodom.pl/pl/oferta/nadolnik-compact-apartments-ID45iR1', 'https://www.otodom.pl/pl/oferta/naramowicka-172-ID4wW7M', 'https://www.otodom.pl/pl/oferta/rezydencja-san-petrus-ID4wZGn', 'https://www.otodom.pl/pl/oferta/naramowicka-172-ID4wW7M', 'https://www.otodom.pl/pl/oferta/naramowicka-172-ID4wW7M', 'https://www.otodom.pl/pl/oferta/nadolnik-compact-apartments-ID45iR1', 'https://www.otodom.pl/pl/oferta/osiedle-naturama-ii-ID4uard']

keys = ['ID', 'Cena', 'Powierzchnia', 'Cena za metr', 'Pokoje', 'Ulica', 'Dzielnica', 'Obszar administracyjny',  'Miasto', 'Województwo', 'Piętro', 'Winda', 'Czynsz', 'Tytuł', 'Link']

single()

with open('single.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=keys)
    writer.writeheader()
    writer.writerows(listings)

print("err's", len(err), err)
 