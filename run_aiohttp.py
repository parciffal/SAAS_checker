import aiohttp
import asyncio
from bs4 import BeautifulSoup
import logging
import pandas as pd
import time
from config import config
from datetime import datetime


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

async def fetch(url, session):
    async with session.get(url) as response:
        return await response.text()

def parse_html(html, domain, saas_words, pbn_words, result, file_path):
    saas_count = 0
    pbn_count = 0

    soup = BeautifulSoup(html, 'html.parser')

    for word in saas_words:
        elements = soup.find_all(href=lambda x: x and word in x.lower() and '/' in x)
        for element in elements:
            href = element.get('href', '')
            if domain in href or "http" not in href:
                if "image/base" not in href and len(href) < 300:
                    logging.info(f"Saas: {word} Url: {href}")
                    saas_count += 1
                    break

    for word in pbn_words:
        elements = soup.find_all(href=lambda x: x and word in x.lower() and '/' in x)
        for element in elements:
            href = element.get('href', '')
            if domain in href or "http" not in href:
                if "image/base" not in href and len(href) < 300:
                    logging.info(f"Pdb: {word} Url: {href}")
                    pbn_count += 1
                    break

    if saas_count > 3:
        saas_count = 3
    if pbn_count > 3:
        pbn_count = 3
    jk = saas_count - pbn_count
    logging.info(f"Url: {domain} | Result: {result.get(jk)}")

    df = pd.read_csv(file_path)
    target_row = df[df['url'] == domain]
    if not target_row.empty:
        df.loc[df['url'] == domain, 'result'] = result.get(jk)
        df.loc[df['url'] == domain, 'checked'] = True
    df.to_csv(file_path, index=False)

async def process_url(url, domain, saas_words, pbn_words, result, file_path, session):
    try:
        await asyncio.sleep(2)
        html = await fetch(url, session)
        parse_html(html, domain, saas_words, pbn_words, result, file_path)
    except Exception as e:
        logging.error(f"Error processing URL {url}: {e}")

async def main():
    pbn_words = ['magazine', 'news', 'health', 'mum', 'fashion',
                 'casino', 'daily', 'lifestyle', 'cbd', 'gamb',
                 'food', 'gambling', 'review', 'legal', 'university',
                 'school', 'travel', 'medical']

    saas_words = ['software', 'platform', 'service', 'tool', 'pricing',
                  'solution', 'maker', 'generator', 'creator', 'product',
                  'price', 'builder', 'finder', 'tracker', 'agency',
                  'company']
    result = {
        0: "Esim",
        3: "100% Saas",
        -3: "100% Pbn",
        1: "25% Saas",
        -1: "25% Pbn",
        2: "50% Saas",
        -2: "50% Pbn"
    }

    csv_file_path = config.local.csv_file_dir
    df = pd.read_csv(csv_file_path)

    async with aiohttp.ClientSession() as session:
        tasks = []
        count = 0
        for index, row in df.iterrows():
            url = "https://" + str(row['url'])
            checked = row['checked']
            if not checked:
                logging.info(url)
                tasks.append(process_url(url, str(row['url']), saas_words, pbn_words, result, csv_file_path, session))
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    try:
        df = pd.read_csv(config.local.csv_file_dir)
        checked_count = df[df['checked'] == True].shape[0]
        logging.info("Start checking")
        now = datetime.now()        
        asyncio.run(main())
    except KeyboardInterrupt:
        end = datetime.now()
        time_dif = end - now
        df = pd.read_csv(config.local.csv_file_dir)
        last_checked_count = df[df['checked'] == True].shape[0]
        total_checked = last_checked_count - checked_count
        logging.info(f"End checking {time_dif} time | {total_checked} urls")
