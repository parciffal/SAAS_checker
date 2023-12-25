import aiohttp
import asyncio
from bs4 import BeautifulSoup
import logging
import pandas as pd
import random


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class SaasFinder:
    def __init__(
        self,
        domain: str,
        file_path: str,
        session: aiohttp.ClientSession,
        saas_words: list[str],
        pbn_words: list[str],
    ) -> None:
        self.domain = domain
        self.file_path = file_path
        self.session = session
        self.saas_words = saas_words
        self.pbn_words = pbn_words

    @staticmethod
    async def fetch(url, session):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        await asyncio.sleep(random.uniform(0, 2))
        async with session.get(url, headers=headers) as response:
            return await response.text()

    def parse_html(self, html):
        saas_count = 0
        pbn_count = 0
        soup = BeautifulSoup(html, "html.parser")
        found_saas = []
        found_pbn = []
        find_all_a_tags = soup.find_all("a")
        logging.info(f"-----------------{self.domain}----------------")
        for a in find_all_a_tags:
            text = a.text.lower()
            for word in self.saas_words:
                if word == text:
                    if word not in found_saas:
                        logging.info(f"Saas: {word} Text: {text}")
                        found_saas.append(word)
                        saas_count += 1
                        break

            for word in self.pbn_words:
                if word == text:
                    if word not in found_pbn:
                        found_pbn.append(word)
                        logging.info(f"Pbn: {word} Text: {text}")
                        pbn_count += 1
                        break

        df = pd.read_csv(self.file_path)
        target_row = df[df["domain"] == self.domain]
        if not target_row.empty:
            df.loc[df["domain"] == self.domain, "saas"] = int(saas_count)
            df.loc[df["domain"] == self.domain, "pbn"] = int(pbn_count)
            df.loc[df["domain"] == self.domain, "checked"] = True
        df.to_csv(self.file_path, index=False)

    async def run(self):
        try:
            await asyncio.sleep(2)
            url = "https://" + self.domain
            html = await self.fetch(url, self.session)
            self.parse_html(html)
        except Exception as e:
            logging.error(f"Error processing URL {self.domain}: {e}")
