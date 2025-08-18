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

#multiadvert_links = ['https://www.otodom.pl/pl/oferta/rezydencja-san-petrus-ID4wZGn', 'https://www.otodom.pl/pl/oferta/os-lotnictwa-polskiego-12-ID4u9wv', 'https://www.otodom.pl/pl/oferta/naramowicka-172-ID4wW7M', 'https://www.otodom.pl/pl/oferta/nadolnik-compact-apartments-ID45iR1', 'https://www.otodom.pl/pl/oferta/osiedle-naturama-ii-ID4uard']
multiadvert_links = []

def read_multiadvert_links():
    with open('links.txt') as links:
        for link in links.readlines():
            multiadvert_links.append(link[:-1])
            
def multi():
    print(multiadvert_links)
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
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/119.0 Safari/537.36',
        'Referer': 'https://www.otodom.pl/'
    }
    
    #driver.get("https://www.otodom.pl/")  # wejście na główną dla ciasteczek
    time.sleep(3)   
    
    #for link in multiadvert_links:
    for link in list(set(multiadvert_links)):
        driver.get(link + PRICE_FILTER)
        time.sleep(5)
        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')
        
        flag = False
        #print(soup.prettify())
        while True:
            for h in soup.find_all(attrs={'data-sentry-element':'StyledAnchor'}):
                #print(h.prettify())
                links.append(h.get("href"))
            for h in soup.find_all(attrs={'data-sentry-element':'Link'}):
                #print(h.prettify())
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
        time.sleep(2)
        try:
            id, price, area, price_per_meter, rooms, address, district, administrative_area, city, voivodeship, floor, elevator, rent, title, link = None, None, None, None, None, None, None, None, None, None, None, None, None, None, None
            driver.get(OTODOM_PL + adv_link)
            html = driver.page_source
            soup = BeautifulSoup(html, 'lxml')
            
            id = soup.find(attrs={'data-sentry-element':'DetailsProperty'}).get_text(strip=True)[3:]
            price = soup.find(attrs={'aria-label':'Cena'}).get_text(strip=True)
            price_per_meter = soup.find(attrs={'aria-label':'Cena za metr kwadratowy'}).get_text(strip=True)
            
            for item in soup.find_all(attrs={"data-sentry-element": "Item"}):
                print(item.prettify())
                
                label = item.get_text(strip=True).lower()
                value_tag = item.find_next_sibling("div")
                
                if "powierzchnia" in label: 
                    area = value_tag
                    
                    if area:
                        area = area.get_text(strip=True)
                
                elif "liczba pokoi" in label: 
                    rooms = value_tag
                    
                    if rooms:
                        rooms = rooms.get_text(strip=True)
                
                elif "czynsz" in label:
                    rent = value_tag
                    
                    if rent:
                        rent = rent.get_text(strip=True)

                        if rent.startswith('.css'): rent = "brak informacji"
                        elif rent.endswith('zł'): rent = rent.strip()

                elif "winda" in label: 
                    elevator = value_tag
                    
                    if elevator:
                        elevator = elevator.get_text(strip=True)
                
                elif "piętro" in label: 
                    floor = value_tag
                    
                    if floor:
                        floor = floor.get_text(strip=True).split('/')[0]    
            
            print(area, rooms, rent, elevator, floor)
            
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
        except Exception as e:
            if link:
                err.append(link)   
            else:
                print(e)
                err.append("ERROR")

    #listings = list(set(listings))

read_multiadvert_links()    
multi()
keys = ['ID', 'Cena', 'Powierzchnia', 'Cena za metr', 'Pokoje', 'Ulica', 'Dzielnica', 'Obszar administracyjny',  'Miasto', 'Województwo', 'Piętro', 'Winda', 'Czynsz', 'Tytuł', 'Link']

with open('multi.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=keys)
    writer.writeheader()
    writer.writerows(listings)

print("err's", len(err), err)