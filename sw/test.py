import requests
from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import chromedriver_autoinstaller
import csv

chromedriver_autoinstaller.install()

options = Options()
options.add_argument("--headless") 
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")

driver = webdriver.Chrome(options=options)
url = ['https://www.otodom.pl/pl/oferta/rezydencja-san-petrus-ID4wZGn', 'https://www.otodom.pl/pl/oferta/os-lotnictwa-polskiego-12-ID4u9wv', 'https://www.otodom.pl/pl/oferta/osiedle-naturama-ii-ID4uard', 'https://www.otodom.pl/pl/oferta/naramowicka-172-ID4wW7M', 'https://www.otodom.pl/pl/oferta/naramowicka-172-ID4wW7M', 'https://www.otodom.pl/pl/oferta/nadolnik-compact-apartments-ID45iR1', 'https://www.otodom.pl/pl/oferta/nadolnik-compact-apartments-ID45iR1', 'https://www.otodom.pl/pl/oferta/rezydencja-san-petrus-ID4wZGn', 'https://www.otodom.pl/pl/oferta/nadolnik-compact-apartments-ID45iR1', 'https://www.otodom.pl/pl/oferta/rezydencja-san-petrus-ID4wZGn', 'https://www.otodom.pl/pl/oferta/naramowicka-172-ID4wW7M', 'https://www.otodom.pl/pl/oferta/nadolnik-compact-apartments-ID45iR1', 'https://www.otodom.pl/pl/oferta/naramowicka-172-ID4wW7M', 'https://www.otodom.pl/pl/oferta/rezydencja-san-petrus-ID4wZGn', 'https://www.otodom.pl/pl/oferta/naramowicka-172-ID4wW7M', 'https://www.otodom.pl/pl/oferta/naramowicka-172-ID4wW7M', 'https://www.otodom.pl/pl/oferta/nadolnik-compact-apartments-ID45iR1', 'https://www.otodom.pl/pl/oferta/osiedle-naturama-ii-ID4uard']
url = list(set(url))
links = []
listings = []

OTODOM_PL = "https://www.otodom.pl"
PRICE_FILTER = "?priceMax=355553"

for link in url:
    driver.get(link + PRICE_FILTER)
    time.sleep(5)      
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')
    flag = False

    while True:
        for h in soup.find_all(attrs={'data-sentry-element':'StyledAnchor'}):
            links.append(h.get("href"))
        for h in soup.find_all(attrs={'data-sentry-element':'Link'}):
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
        
links = list(set(links))

for adv_link in links:
    time.sleep(1)
    id, price, area, price_per_meter, rooms, address, district, administrative_area, city, voivodeship, floor, elevator, rent, title, link = None, None, None, None, None, None, None, None, None, None, None, None, None, None, None
    #print(OTODOM_PL + adv_link)
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
    
    for k, v in zip(details.keys(), details.values()):
        print(k, v)
    print('\n')
    
    listings.append(details)
    #print(listings)
    
with open('test.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=details.keys())
    writer.writeheader()
    writer.writerows(listings)

