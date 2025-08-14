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
                
                details = {
                    'ID' : str(id.get_text(strip=True))[3:].lstrip(' '),
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
                #print(listings)
            
            except:
                if link:
                    err.append(link)
                else:
                    err.append("ERROR")
            
            time.sleep(1)

        for thumbnail in soup.find_all(attrs={'data-sentry-component':'CombinedInvestmentCard'}):
            try:
                link = OTODOM_PL + thumbnail.find(attrs={'data-cy' : 'listing-item-link'}).get("href")
                multiadvert_links.append(link)
        
            except:
                pass
            
            time.sleep(1)

    driver.quit()

#print(list(set(multiadvert_links)))

multiadvert_links = ['https://www.otodom.pl/pl/oferta/rezydencja-san-petrus-ID4wZGn', 'https://www.otodom.pl/pl/oferta/os-lotnictwa-polskiego-12-ID4u9wv', 'https://www.otodom.pl/pl/oferta/osiedle-naturama-ii-ID4uard', 'https://www.otodom.pl/pl/oferta/naramowicka-172-ID4wW7M', 'https://www.otodom.pl/pl/oferta/naramowicka-172-ID4wW7M', 'https://www.otodom.pl/pl/oferta/nadolnik-compact-apartments-ID45iR1', 'https://www.otodom.pl/pl/oferta/nadolnik-compact-apartments-ID45iR1', 'https://www.otodom.pl/pl/oferta/rezydencja-san-petrus-ID4wZGn', 'https://www.otodom.pl/pl/oferta/nadolnik-compact-apartments-ID45iR1', 'https://www.otodom.pl/pl/oferta/rezydencja-san-petrus-ID4wZGn', 'https://www.otodom.pl/pl/oferta/naramowicka-172-ID4wW7M', 'https://www.otodom.pl/pl/oferta/nadolnik-compact-apartments-ID45iR1', 'https://www.otodom.pl/pl/oferta/naramowicka-172-ID4wW7M', 'https://www.otodom.pl/pl/oferta/rezydencja-san-petrus-ID4wZGn', 'https://www.otodom.pl/pl/oferta/naramowicka-172-ID4wW7M', 'https://www.otodom.pl/pl/oferta/naramowicka-172-ID4wW7M', 'https://www.otodom.pl/pl/oferta/nadolnik-compact-apartments-ID45iR1', 'https://www.otodom.pl/pl/oferta/osiedle-naturama-ii-ID4uard']
def multi():
    service, driver, soup = None, None, None
    
    links = []
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
    #for link in multiadvert_links:
    for link in list(set(multiadvert_links)):
        driver.get(link + PRICE_FILTER)
        time.sleep(5)      
        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')
        flag = False
        print(soup.prettify())
        while True:
            for h in soup.find_all(attrs={'data-sentry-element':'StyledAnchor'}):
                print(h.prettify())
                links.append(h.get("href"))
            for h in soup.find_all(attrs={'data-sentry-element':'Link'}):
                print(h.prettify())
                links.append(h.get("href"))
            try:
                next_btn = driver.find_element(By.XPATH, '//li[@aria-label="Go to next Page"]')
                disabled = next_btn.get_attribute("aria-disabled")

                if disabled == 'true': break
                
                driver.execute_script("arguments[0].click();", next_btn)
                time.sleep(3)  
                html = driver.page_source
                soup = BeautifulSoup(html, 'lxml')
            except:
                flag = True
                
            if flag is True:
                break
            #print(links)
    
    links = list(set(links))
    print("list set links", links)
    for adv_link in links:
        time.sleep(1)
        try:
            id, price, area, price_per_meter, rooms, address, district, administrative_area, city, voivodeship, floor, elevator, rent, title, link = None, None, None, None, None, None, None, None, None, None, None, None, None, None, None
            driver.get(OTODOM_PL + adv_link)
            html = driver.page_source
            soup = BeautifulSoup(html, 'lxml')
            
            id = soup.find(attrs={'data-sentry-element':'DetailsProperty'}).get_text(strip=True)[3:]
            price = soup.find(attrs={'aria-label':'Cena'}).get_text(strip=True)
            price_per_meter = soup.find(attrs={'aria-label':'Cena za metr kwadratowy'}).get_text(strip=True)
            
            for item in soup.find_all(attrs={"data-sentry-element": "Item"}):
                label = item.get_text(strip=True).lower()
                value_tag = item.find_next_sibling("p")
                
                if "powierzchnia" in label: area = value_tag.get_text(strip=True)
                elif "liczba pokoi" in label: rooms = value_tag.get_text(strip=True)
                elif "czynsz" in label:
                    rent = value_tag.get_text(strip=True)

                    if rent.startswith('.css'): rent = "brak informacji"
                    elif rent.endswith('zł'): rent = rent.strip()

                elif "winda" in label: elevator = value_tag.get_text(strip=True)
                elif "piętro" in label: floor = value_tag.get_text(strip=True).split('/')[0]    
            
            localisation = soup.find(attrs={'data-sentry-component':'MapLink'}).get_text(strip=True)
            keys = ['Ulica', 'Dzielnica', 'Obszar administracyjny', 'Miasto', 'Województwo'][::-1]
            localisation = localisation.split(',')[::-1]

            address = { key: val for key, val in zip(keys, localisation) }      
            
            title = soup.find(attrs={'data-cy':'adPageAdTitle'}).get_text(strip=True)
            
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
                'Link': OTODOM_PL + adv_link
            }
            
            #for k, v in zip(details.keys(), details.values()):
                #print(k, v)
            #print('\n')
            
            listings.append(details)  
            print(len(listings))   
        except:
            if link:
                err.append(link)   
            else:
                err.append("ERROR")

    #listings = list(set(listings))
keys = ['ID', 'Cena', 'Powierzchnia', 'Cena za metr', 'Pokoje', 'Ulica', 'Dzielnica', 'Obszar administracyjny',  'Miasto', 'Województwo', 'Piętro', 'Winda', 'Czynsz', 'Tytuł', 'Link']

single()
multi()

with open('data.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=keys)
    writer.writeheader()
    writer.writerows(listings)

print("err's", len(err), err)
 