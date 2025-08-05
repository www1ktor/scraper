import requests
from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import chromedriver_autoinstaller
import csv

# Automatyczna instalacja chromedrivera
chromedriver_autoinstaller.install()

# Konfiguracja opcji Chrome
options = Options()
options.add_argument("--headless")  # Nie pokazuj okna przeglądarki
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")


# Start przeglądarki
driver = webdriver.Chrome(options=options)

# Otwórz stronę
url = "https://www.otodom.pl/pl/inwestycja/rezydencja-san-petrus-ID4wZGn?priceMax=355553"
driver.get(url)

# Poczekaj na załadowanie (ważne przy SPA)
time.sleep(5)  # Można zastąpić WebDriverWait dla większej precyzji

# Pobierz HTML po załadowaniu JS
html = driver.page_source
soup = BeautifulSoup(html, 'lxml')
#print(soup.prettify())
# Przykład: znajdź wszystkie elementy, np. nagłówki
while True:
    for h in soup.find_all(attrs={'data-sentry-element':'StyledAnchor'}):
        print(h)
    try:
        next_btn = driver.find_element(By.XPATH, '//li[@aria-label="Go to next Page"]')
        driver.execute_script("arguments[0].click();", next_btn)
        time.sleep(3)  # poczekaj na załadowanie
    except:
        break

# Zamknij przeglądarkę
driver.quit()
