import requests
from bs4 import BeautifulSoup
import time

base_url = "https://www.otodom.pl/pl/wyniki/sprzedaz/mieszkanie/wielkopolskie/poznan/poznan/poznan?limit=36&ownerTypeSingleSelect=ALL&priceMax=355553&by=DEFAULT&direction=DESC"

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

    offers = soup.select('.e1wc8ahl1.css-1xi9t0b.e12fn6ie0')

    for offer in offers:
        title = offer.select_one('.css-16vl3c1.e17g0c820').get_text(strip=True)
        localisation = offer.select_one('.css-42r2ms.eejmx80').get_text(strip=True)

        dl_tags = offer.find_all("dl")

        for dl in dl_tags:
            dt_tags = dl.find_all("dt")

            rooms = None
            footage = None
            price_per_meter = None
            floor = None

            for dt in dt_tags:
                label = dt.get_text(strip=True) 
                
                     

        print([title, localisation])
        time.sleep(1)
    #print(offers)
#for result in results:
    #print(result)   
#print(len(results), len(set(results)))




