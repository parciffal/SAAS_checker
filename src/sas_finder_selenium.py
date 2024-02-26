import re
import time
import pandas as pd
from linkedin_scraper import Company, actions
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver


class GetPageLinksSelenium:
    def __init__(self, file_name):
        self.__data = self.__read_csv(file_name)
        self.__driver = self.__init_driver()
        self.input_file = "data/input/" + file_name
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        self.saas_words = pd.read_csv("data/input/Saas.csv")['Keyword']
        self.pbn_words = pd.read_csv("data/input/PBN.csv")['Keyword']

    def __read_csv(self, file_name):
        data = pd.read_csv("data/input/"+file_name)
        return data
    
    def __init_driver(self):
        options = uc.ChromeOptions()
        options.headless = True  # Run in headless mode
        driver = uc.Chrome(driver_executable_path="./driver/chromedriver.exe", options=options)
        return driver
    
    def find_with_selenium(self,domain):
        df = pd.read_csv(self.input_file)
        try:
            saas_count = 0
            pbn_count = 0
            self.__driver.get("https://" + domain)
            all_a_tags = self.__driver.find_elements(By.TAG_NAME, "a")
            print(f"-----------------{domain}----------------")

            target_row = df[df["domain"] == domain]

            for a in all_a_tags:
                text = a.text.lower()
                for word in self.saas_words:
                    if word == text:
                        print(f"Saas: {word} Text: {text}")
                        saas_count += 1

                for word in self.pbn_words:
                    if word == text:
                        print(f"Pbn: {word} Text: {text}")
                        df.loc[df["domain"] == domain, word] = True
                        pbn_count += 1

            if not target_row.empty:
                df.loc[df["domain"] == domain, "saas"] = int(saas_count)
                df.loc[df["domain"] == domain, "pbn"] = int(pbn_count)
                df.loc[df["domain"] == domain, "checked"] = True
        except Exception as e:
            df.loc[df["domain"] == domain, "checked"] = "bratva"
        finally:            
            df.to_csv(self.input_file, index=False)

    def add_columns(self):
        df = pd.read_csv(self.input_file, low_memory=False)
        existing_columns = set(df.columns)
        for word in self.pbn_words:
            if word not in existing_columns:
                df[word] = False
        df.to_csv(self.input_file, index=False)
#
    def run_script(self):
        # print(self.pbn_words)
        links = self.__data["domain"].tolist()
        print(links)
        for link in links:
            self.find_with_selenium(link)  
        self.__driver.quit()