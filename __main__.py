from src.new_saas_finder import GetPageLinks
import asyncio

if __name__ == "__main__":
    fd = GetPageLinks("input.csv")
    asyncio.run(fd.run_script())