# -*- coding: utf-8 -*-


import logging
import concurrent.futures
import requests
from bs4 import BeautifulSoup
import time
import threading

logging.basicConfig(level=logging.INFO)

titles = []
titles_lock = threading.Lock()

def download_site(url):
    global titles
    
    with requests.get(url) as response:
        html_content = response.content
        soup = BeautifulSoup(html_content, 'html.parser')
        event_titles = soup.find_all('h3', class_='tribe-events-calendar-list__event-title')
        titles_from_site = []
        for title_raw in event_titles:
            title = title_raw.text.strip()
            logging.info(f"Pobrano tytul: {title}")
            titles_from_site.append(title)
            
        with titles_lock:
            titles.extend(titles_from_site)

def download_all_sites(sites):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(download_site, sites)

if __name__ == "__main__":
    sites = [f"https://wsei.edu.pl/wydarzenia/lista/strona/{i}/?eventDisplay=past" for i in range(1,11)]
    start = time.time()
    download_all_sites(sites)
    logging.info(f"Pobrano {len(titles)} tytulow in {time.time() - start} seconds")
