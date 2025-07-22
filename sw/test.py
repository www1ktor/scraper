from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://www.otodom.pl/pl/oferta/mieszkanie-w-atrakcyjnej-cenie-z-szybkim-dostepem-do-centrum-poznania-ID4x5va")
    page.wait_for_selector('[data-sentry-element="DescriptionWrapper"]')
    print(page.query_selector('[data-sentry-element="DescriptionWrapper"]').inner_text())
    browser.close()
