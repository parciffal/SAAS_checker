import asyncio
import logging
import pandas as pd
from aiohttp import ClientSession
from bs4 import BeautifulSoup


class GetPageLinks:
    def __init__(self, input_file):
        self.input_file =r"data/input/" +  input_file
        self.__data = self.__get_data(self.input_file)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        self.saas_words = pd.read_csv("data/input/Saas.csv")['Keyword']
        self.pbn_words = pd.read_csv("data/input/PBN.csv")['Keyword']

    #
    def __get_data(self, file_name):
        df = pd.read_csv(file_name, low_memory=False)

        return df

    @staticmethod
    async def fetch(url, session):
        async with session.get(url, timeout=10) as response:
            return await response.text()

    #
    async def parse_html(self, html, domain):
        saas_count = 0
        pbn_count = 0
        soup = BeautifulSoup(html, "html.parser")
        found_saas = []
        found_pbn = []
        find_all_a_tags = soup.find_all("a")
        print(f"-----------------{domain}----------------")

        df = pd.read_csv(self.input_file)
        target_row = df[df["domain"] == domain]
        for a in find_all_a_tags:
            text = a.text.lower()
            for word in self.saas_words:
                if word == text:
                    if word not in found_saas:
                        print(f"Saas: {word} Text: {text}")
                        found_saas.append(word)
                        saas_count += 1
                        break

            for word in self.pbn_words:
                if word == text:
                    if word not in found_pbn:
                        found_pbn.append(word)
                        df.loc[df["domain"] == domain, word] = True
                        print(f"Pbn: {word} Text: {text}")
                        pbn_count += 1
                        break
        if not target_row.empty:
            df.loc[df["domain"] == domain, "saas"] = int(saas_count)
            df.loc[df["domain"] == domain, "pbn"] = int(pbn_count)
            df.loc[df["domain"] == domain, "checked"] = True

        df.to_csv(self.input_file, index=False)

    async def create_tasks(self, link):
        if pd.isna(self.__data.loc[self.__data["domain"] == link, "checked"].values[0]) or self.__data.loc[self.__data["domain"] == link, "checked"].values[0] == "bratva":
            async with ClientSession(headers=self.headers) as session:
                print(f"Link: {link}")
                try:
                    url = link if link.startswith("https://") else "https://" + link
                    html = await self.fetch(url, session)
                    await self.parse_html(html, link)
                except Exception as e:
                    print(e)
                    pass

    #
    async def process_chunk(self, chunk):
        tasks = []
        for i in range(0, len(chunk)):
            tasks.append(
                self.create_tasks(chunk[i])
            )
        await asyncio.gather(*tasks)

    async def run_script(self):
        step = 2
        links = self.__data["domain"].tolist()
        for i in range(0, len(links), step):
            await self.process_chunk(
                    links[i: i + step]
                )
