import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium import webdriver
import undetected_chromedriver as uc
from undetected_chromedriver import By
from selenium.common.exceptions import NoSuchElementException
import pandas as pd
import time
from config import config

def __init_driver(allow_options: bool = True):
    if allow_options:
        options = __init_options()
        driver = uc.Chrome(
            options=options,
            driver_executable_path=config.local.driver_dir,
            #headless=True,
            version_main=109)
    else:
        driver = uc.Chrome(
            driver_executable_path=config.local.driver_dir)
    return driver

def __init_options() -> uc.ChromeOptions:
    chrome_options = uc.ChromeOptions()
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-popup-blocking")
    return chrome_options

def detect_saas_pbn_parallel(args):
    url, domain, driver, saas_words, pbn_words, result, file_path = args
    driver.get("https://"+url)
    time.sleep(1)
    saas_count = 0
    pbn_count = 0

    for word in saas_words:
        try:
            xpath_expression = f"//*[contains(@href, '/') and contains(translate(@href, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{word}') and not(ancestor::script) and not(ancestor::style)]"
            matching_elements = driver.find_elements(By.XPATH, xpath_expression)
            if len(matching_elements) > 0:
                for i in matching_elements:
                    href = i.get_attribute("href")
                    if domain in href or "http" not in href:
                        if "image/base" not in href and len(href) < 300:
                            logging.info(f"Saas: {word} Url: {href}")
                            saas_count += 1
                            break
        except NoSuchElementException:
            continue

    for word in pbn_words:
        try:
            xpath_expression = f"//*[contains(@href, '/') and contains(translate(@href, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{word}') and not(ancestor::script) and not(ancestor::style)]"
            matching_elements = driver.find_elements(By.XPATH, xpath_expression)
            if len(matching_elements) > 0:
                for i in matching_elements:
                    href = i.get_attribute("href")
                    if domain in href or "http" not in href:
                        if "image/base" not in href and len(href) < 300:
                            logging.info(f"Pdb: {word} Url: {href}")
                            pbn_count += 1
                            break
        except NoSuchElementException:
            continue

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

def split_csv_file(file_path, num_splits):
    df = pd.read_csv(file_path)
    total_rows = len(df)
    split_size = total_rows // num_splits

    for i in range(num_splits):
        start_index = i * split_size
        end_index = (i + 1) * split_size if i < num_splits - 1 else total_rows
        df_part = df.iloc[start_index:end_index]
        df_part.to_csv(f"{file_path}_part{i + 1}.csv", index=False)

def main():
    log_file_path = "./logs.txt"
    logging.basicConfig(filename=log_file_path, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    logging.info("Script started.")

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
    split_csv_file(csv_file_path, 4)  # Split the CSV file into 4 parts

    drivers = [__init_driver() for _ in range(4)]

    for i in range(4):
        df_part = pd.read_csv(f"{csv_file_path}_part{i + 1}.csv")
        urls_to_process = [(row['url'], row['url'], drivers[i], saas_words, pbn_words, result, f"{csv_file_path}_part{i + 1}.csv") for _, row in df_part.iterrows() if not row['checked']]

        with ThreadPoolExecutor(max_workers=1) as executor:
            futures = [executor.submit(detect_saas_pbn_parallel, args) for args in urls_to_process]

            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(f"An error occurred: {e}")

    for driver in drivers:
        driver.quit()

if __name__ == "__main__":
    main()
