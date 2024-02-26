from src.new_saas_finder import GetPageLinks
from src.sas_finder_selenium import GetPageLinksSelenium
import asyncio

fd = GetPageLinks("input.csv")
asyncio.run(fd.run_script())


fd_sel = GetPageLinksSelenium("input.csv")
fd_sel.run_script()
