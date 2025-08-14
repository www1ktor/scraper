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
errors = []
was_id = []

OTODOM_PL = "https://www.otodom.pl"
base_url = OTODOM_PL + "/pl/wyniki/sprzedaz/mieszkanie/wielkopolskie/poznan/poznan/poznan?limit=36&ownerTypeSingleSelect=ALL&priceMax=355553&by=DEFAULT&direction=DESC"
PRICE_FILTER = "?priceMax=355553"

def setup_driver():
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
    return webdriver.Chrome(options=options)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/119.0 Safari/537.36'
}

def scrape_single_listings():
    print("Scraping single listings...")
    driver = setup_driver()
    try:
        response = requests.get(base_url + '/1', headers=headers)
        soup = BeautifulSoup(response.content, 'lxml')

        pages_text = soup.find(attrs={'data-sentry-component':'ItemsCounter'}).get_text(strip=True)[2:]
        pages_parts = pages_text.split()
        pages_start = int(pages_parts[0])
        pages_stop = int(pages_parts[-1])
        n_pages = (pages_stop // pages_start) + (1 if pages_stop % pages_start != 0 else 0)

        for page in range(1, n_pages + 1):
            print(f"Processing page {page} of {n_pages}...")
            response = requests.get(base_url + f"&page={str(page)}", headers=headers)
            soup = BeautifulSoup(response.content, 'lxml')
            
            for thumbnail in soup.find_all(attrs={'data-sentry-component':'AdvertCard'}):
                try:
                    process_single_listing(thumbnail)
                except Exception as e:
                    link = OTODOM_PL + thumbnail.find(attrs={'data-cy': 'listing-item-link'}).get("href", "Unknown link")
                    errors.append(f"Error processing single listing {link}: {str(e)}")
            
            for thumbnail in soup.find_all(attrs={'data-sentry-component':'CombinedInvestmentCard'}):
                try:
                    link = OTODOM_PL + thumbnail.find(attrs={'data-cy': 'listing-item-link'}).get("href")
                    if link:
                        process_combined_listing(link, driver)
                except Exception as e:
                    errors.append(f"Error processing combined listing card: {str(e)}")
                
            time.sleep(1)
    finally:
        driver.quit()

def process_single_listing(thumbnail):
    title = thumbnail.find(attrs={'data-cy': 'listing-item-title'}).get_text(strip=True)
    localisation = thumbnail.find(attrs={'data-sentry-component':'Address'}).get_text(strip=True)
    link = OTODOM_PL + thumbnail.find(attrs={'data-cy': 'listing-item-link'}).get("href")
    
    keys = ['Ulica', 'Dzielnica', 'Obszar administracyjny', 'Miasto', 'Województwo'][::-1]
    localisation_parts = localisation.split(',')[::-1]
    address = {key: val.strip() for key, val in zip(keys, localisation_parts) if val}

    floor = None
    for dt in thumbnail.find_all("dt"):
        if "Piętro" in dt.get_text(strip=True):
            dd = dt.find_next_sibling("dd")
            if dd:
                floor = dd.get_text(strip=True)

    listing_response = requests.get(link, headers=headers)
    offer = BeautifulSoup(listing_response.content, 'lxml')

    id = offer.find(attrs={'data-sentry-element':'DetailsContainer'}).get_text(strip=True)[3:].lstrip(' ')
    price = offer.find(attrs={'data-sentry-element':'Price'}).get_text(strip=True)
    price_per_meter = offer.find(attrs={'aria-label':'Cena za metr kwadratowy'}).get_text(strip=True)
    
    details = {
        'ID': id,
        'Cena': price,
        'Powierzchnia': None,
        'Cena za metr': price_per_meter,
        'Pokoje': None,
        'Ulica': address.get('Ulica', ''),
        'Dzielnica': address.get('Dzielnica', ''),
        'Obszar administracyjny': address.get('Obszar administracyjny', ''),
        'Miasto': address.get('Miasto', ''),
        'Województwo': address.get('Województwo', ''),
        'Piętro': floor,
        'Winda': None,
        'Czynsz': None,
        'Tytuł': title,
        'Link': link
    }

    for p in offer.find_all(attrs={'data-sentry-element':"Item"}):
        label = p.get_text(strip=True).replace(":", "").lower()
        sibling = p.find_next_sibling()
        value = sibling.get_text(strip=True) if sibling else None

        if 'powierzchnia' in label:
            details['Powierzchnia'] = value
        elif 'liczba pokoi' in label:
            details['Pokoje'] = value
        elif 'czynsz' in label:
            details['Czynsz'] = "brak informacji" if value and value.startswith('.css') else value
        elif 'winda' in label:
            details['Winda'] = value

    listings.append(details)
    print(f"Processed single listing: {title}")

def process_combined_listing(main_link, driver):
    print(f"Processing combined listing: {main_link}")
    driver.get(main_link + PRICE_FILTER)
    time.sleep(3)
    
    listing_links = set()
    
    while True:
        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')
        
        # Find all listing links on the page
        for a in soup.find_all('a', href=True):
            href = a['href']
            if '/pl/oferta/' in href and not any(x in href for x in ['#', '?']):
                listing_links.add(href)
        
        # Try to find and click next page button
        try:
            next_btn = driver.find_element(By.XPATH, '//li[@aria-label="Go to next Page"]')
            if next_btn.get_attribute("aria-disabled") == 'true':
                break
                
            driver.execute_script("arguments[0].click();", next_btn)
            time.sleep(3)
        except:
            break
    
    # Process each listing
    for link in listing_links:
        full_link = OTODOM_PL + link if not link.startswith('http') else link
        scrape_individual_listing(full_link, driver)

def scrape_individual_listing(link, driver):
    print(f"Scraping individual listing: {link}")
    try:
        driver.get(link)
        time.sleep(2)
        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')
        
        try:
            id = soup.find(attrs={'data-sentry-element':'DetailsProperty'}).get_text(strip=True)[3:]
        
            if id in was_id:
                return
            
            was_id.append(was_id)
        except:
            id = "Unknown"
            
        try:
            price = soup.find(attrs={'aria-label':'Cena'}).get_text(strip=True)
        except:
            price = "Unknown"
            
        try:
            price_per_meter = soup.find(attrs={'aria-label':'Cena za metr kwadratowy'}).get_text(strip=True)
        except:
            price_per_meter = "Unknown"
            
        try:
            title = soup.find(attrs={'data-cy':'adPageAdTitle'}).get_text(strip=True)
        except:
            title = "Unknown"
            
        try:
            localisation = soup.find(attrs={'data-sentry-component':'MapLink'}).get_text(strip=True)
            keys = ['Ulica', 'Dzielnica', 'Obszar administracyjny', 'Miasto', 'Województwo'][::-1]
            localisation_parts = localisation.split(',')[::-1]
            address = {key: val.strip() for key, val in zip(keys, localisation_parts) if val}
        except:
            address = {}
            
        details = {
            'ID': id,
            'Cena': price,
            'Powierzchnia': None,
            'Cena za metr': price_per_meter,
            'Pokoje': None,
            'Ulica': address.get('Ulica', ''),
            'Dzielnica': address.get('Dzielnica', ''),
            'Obszar administracyjny': address.get('Obszar administracyjny', ''),
            'Miasto': address.get('Miasto', ''),
            'Województwo': address.get('Województwo', ''),
            'Piętro': None,
            'Winda': None,
            'Czynsz': None,
            'Tytuł': title,
            'Link': link
        }
        
        for item in soup.find_all(attrs={"data-sentry-element": "Item"}):
            label = item.get_text(strip=True).lower()
            value_tag = item.find_next_sibling("p") or item.find_next_sibling("div")
            
            if not value_tag:
                continue
                
            value = value_tag.get_text(strip=True)
            
            if "powierzchnia" in label: 
                details['Powierzchnia'] = value
            elif "liczba pokoi" in label: 
                details['Pokoje'] = value
            elif "czynsz" in label:
                details['Czynsz'] = "brak informacji" if value.startswith('.css') else value
            elif "winda" in label: 
                details['Winda'] = value
            elif "piętro" in label: 
                details['Piętro'] = value.split('/')[0] if '/' in value else value
        
        listings.append(details)
        print(f"Processed listing: {title}")
    except Exception as e:
        errors.append(f"Error processing listing {link}: {str(e)}")

def save_to_csv():
    if not listings:
        print("No data to save!")
        return
        
    fieldnames = listings[0].keys()
    with open('data.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(listings)
    print(f"Data saved to data.csv, total listings: {len(listings)}")

def main():
    scrape_single_listings()
    save_to_csv()
    
    if errors:
        print("\nErrors encountered:")
        for error in errors:
            print(error)

if __name__ == "__main__":
    main()