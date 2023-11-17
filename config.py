import platform

from pydantic import BaseModel


class Local(BaseModel):
    driver_dir_lin: str = "./chromedriver"
    driver_dir_win: str = "./chromedriver.exe"
    csv_file_dir: str = "links.csv"

    @property
    def driver_dir(self) -> str:
        if platform.system() == "Windows":
            return self.driver_dir_win
        return self.driver_dir_lin


class Config(BaseModel):
    local: Local = Local()


config = Config()
