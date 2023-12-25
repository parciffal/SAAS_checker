import asyncio
from src.saas_finder import SaasFinder
import pandas as pd
import aiohttp

MAX_CONCURRENT_TASKS = 10  # Maximum number of concurrent tasks
PBD_WORDS = [
    "magazine",
    "news",
    "health",
    "fashion",
    "lifestyle",
    "cbd",
    "gambling",
    "food",
    "review",
    "reviews",
    "legal",
    "university",
    "school",
    "travel",
    "medical",
    "casino",
    "business",
    "education",
    "entertainment",
    "technology",
    "technologies",
    "biography",
    "fashion",
    "automotive",
    "celebrity",
    "celebrities",
    "music",
    "finance",
    "finances",
    "net worth",
    "stories",
    "law",
    "real estate",
    "kitchen",
    "construction",
    "life style",
    "tech",
    "daily",
    "shop",
    "store",
]

SAAS_WORDS = [
    "software",
    "platform",
    "service",
    "services",
    "tool",
    "tools",
    "solution",
    "solutions",
    "maker",
    "generator",
    "creator",
    "builder",
    "finder",
    "tracker",
    "agency",
    "company",
    "pricing",
    "what we do",
]


async def collect_data(file_path: str, batch_size: int):
    df = pd.read_csv(
        "./data/input/saas_checker_input.csv", index_col=False, encoding="utf-8"
    )
    urls_stack = [
        row.get("domain")
        for _, row in df.iterrows()
        if pd.isna(row.get("checked"))
        or row.get("checked") == ""
        or row.get("checked") != True
    ]

    semaphore = asyncio.Semaphore(MAX_CONCURRENT_TASKS)
    # Process URLs in batches
    for i in range(0, len(urls_stack), batch_size):
        print(i, i + batch_size)
        batch = urls_stack[i : i + batch_size]
        await run(batch, file_path, semaphore)


async def process_single_url(domain, file_path: str, semaphore: asyncio.Semaphore):
    async with semaphore:
        try:
            async with aiohttp.ClientSession() as session:
                saas_cheaker = SaasFinder(
                    domain=domain,
                    saas_words=SAAS_WORDS,
                    pbn_words=PBD_WORDS,
                    file_path=file_path,
                    session=session,
                )
                await saas_cheaker.run()
        except Exception as e:
            print(e)
        finally:
            return True


async def run(url_list, file_path, semaphore):
    tasks = []
    for url in url_list:
        task = process_single_url(url, file_path, semaphore)
        tasks.append(task)
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    # file_dir = get_latest_file()
    file_dir = "./data/input/saas_checker_input.csv"
    if file_dir:
        asyncio.run(collect_data(file_dir, batch_size=10))
    else:
        print("Check Files")
