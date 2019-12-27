"""
a base class of downloader implemented by selenium
"""

from abc import ABC, abstractmethod
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class SeleniumDownloaderBase(ABC):
    def __init__(self, chrome_driver_path="/usr/local/bin/chromedriver", use_xvfb=False):
        self.chrome_driver_path = chrome_driver_path
        self.use_xvfb = use_xvfb

        options = Options()
        if self.use_xvfb:
            # xvfbの仮想ディスプレイに描画 
            from pyvirtualdisplay import Display

            display = Display(visible=0, size=(1280,1024))
            display.start()

            options.binary_location = "/usr/bin/google-chrome"
            options.add_argument("--window-size=1280,1024")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
        else:
            # headlessで実行 
            options.add_argument("--headless")
        self.driver = webdriver.Chrome(self.chrome_driver_path, options=options)
    
    @abstractmethod
    def download(self):
        return None
