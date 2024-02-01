from src.new_saas_finder import GetPageLinks
import asyncio

if __name__ == "__main__":
    fd = GetPageLinks("saas_checker_input.csv")
    asyncio.run(fd.run_script())