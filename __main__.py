from sys import exception
import undetected_chromedriver as uc
from config import config
import pandas as pd
import time
from undetected_chromedriver import By
from selenium.common.exceptions import NoSuchElementException,StaleElementReferenceException
import logging
import coloredlogs
from logging.config import DictConfigurator
logging_config = DictConfigurator(
    {
        "version": 1,
        "formatters": {"standard": {"format": "%(asctime)s - %(message)s"}},
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "standard",
                "level": "INFO",
            }
        },
        "root": {"handlers": ["console"], "level": "INFO"},
    }
)

def __init_driver(allow_options: bool = True):
    if allow_options:
        options = __init_options()
        driver = uc.Chrome(
            options=options,
            driver_executable_path=config.local.driver_dir,
            # headless=True,
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


def detect_saas_pbn(url: str, domain: str, driver: uc.Chrome, saas_words: list, pbn_words: list, result: dict, file_path: str):
    driver.get(url)

    saas_count = 0
    pbn_count = 0

    for word in saas_words:
        try:
            # Define an XPath expression to find elements containing the word
            xpath_expression = f"//*[contains(@href, '/') and contains(translate(@href, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{word}') and not(ancestor::script) and not(ancestor::style)]"
            # Find elements using the XPath expression
            matching_elements = driver.find_elements(By.XPATH, xpath_expression)
            if len(matching_elements) > 0:
                for i in matching_elements:
                    href = i.get_attribute("href")
                    if domain in href or "http" not in href:
                        if "image/base" not in href and len(href)<300:
                            logging.info(f"Saas: {word} Url: {href}")
                            print(f"Saas: {word} Url: {href}")
                            saas_count += 1
                            break
        except NoSuchElementException:
            continue

    for word in pbn_words:
        try:
            # Define an XPath expression to find elements containing the word
            xpath_expression = f"//*[contains(@href, '/') and contains(translate(@href, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{word}') and not(ancestor::script) and not(ancestor::style)]"
            # Find elements using the XPath expression
            matching_elements = driver.find_elements(By.XPATH, xpath_expression)
            if len(matching_elements) > 0:
                for i in matching_elements:
                    href = i.get_attribute("href")
                    if domain in href or "http" not in href:
                        if "image/base" not in href and len(href)<300:
                            logging.info(f"Pdb: {word} Url: {href}")
                            print(f"Pdb: {word} Url: {href}")
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
    print(f"Url: {domain} | Result: {result.get(jk)}")
    df = pd.read_csv(file_path)
    target_row = df[df['url'] == domain]
    if not target_row.empty:
        df.loc[df['url'] == domain, 'result'] = result.get(jk)
        df.loc[df['url'] == domain, 'checked'] = True
    df.to_csv(file_path, index=False)


def reformat_csv(file_path: str):
    fra = pd.read_csv(file_path)
    new_fra = pd.DataFrame({
        "url": list(fra['urls']),
        "result": '',
        "checked": False
    })
    new_fra.to_csv(config.local.csv_file_dir, index=False)


def main():
    # Configure the logging module
    log_file_path = "./logs.txt"
    
    logging.basicConfig(filename=log_file_path, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Log the start of the script
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
    driver = __init_driver()
    df = pd.read_csv(config.local.csv_file_dir)
    for index, row in df.iterrows():
        url = row['url']
        checked = row['checked']
        if not checked:
            time.sleep(1)
            logging.info(url)
            print(url)
            try:
                detect_saas_pbn(
                    url="https://"+str(url),
                    domain=str(url),
                    driver=driver,
                    saas_words=saas_words,
                    pbn_words=pbn_words,
                    result=result,
                    file_path=config.local.csv_file_dir)
            except Exception as e:
                print(e)


main()
