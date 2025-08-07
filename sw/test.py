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
        
    print(link, len(links), len(set(links)))

for adv_link in links:
    id, price, area, price_per_meter, rooms, address, district, administrative_area, city, voivodeship, floor, elevator, rent, title, link = None, None, None, None, None, None, None, None, None, None, None, None, None, None, None
    #print(OTODOM_PL + adv_link)
    driver.get(OTODOM_PL + adv_link)
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')
    
    
    
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
