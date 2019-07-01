#!/usr/bin/env python

"""
ACL Anthology Downloader

a script for downloading papers on ACL Anthology (https://aclweb.org/anthology/)
"""

import argparse
import json
from pathlib import Path
import time
import traceback
import urllib.request

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import chromedriver_binary


class ACLAnthologyDownloader(object):
    def __init__(self, chrome_driver_path="/usr/local/bin/chromedriver", use_xvfb=False):
        """
        Parameters
        ----------
        chrome_driver_path : str
            path to chromedriver
        use_xvfb : bool
            using X virtual frame buffer for chromedriver or not
        
        Returns
        -------
        None
        """
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

    def download(self, event_name, year, output_dir, verbose=False):
        """
        download papers
        
        Parameters
        ----------
        event_name : str
            an event name of ACL Anthology
        year : str
            year (yyyy)
        output_dir : str
            path to output directory
        verbose : bool
            show progress of downloading
        
        Returns
        -------
        None
        """
        output_dir_path = Path(output_dir)
        if not output_dir_path.exists():
            output_dir_path.mkdir(parents=True)
        
        try:
            url = self._generate_url(event_name, year)
            self.driver.get(url)
            time.sleep(0.1)

            elem_list = self.driver.find_elements_by_xpath("//a[@class='badge badge-primary align-middle mr-1']")
            for elem in elem_list:
                if elem.text == "pdf":
                    url = elem.get_attribute("href")
                    if verbose:
                        print(f"download {url}...")
                    fid = Path(url).stem
                    output_fn = output_dir_path / f"{fid}.pdf"
                    urllib.request.urlretrieve(url, output_fn)
                    time.sleep(0.1)
        except:
            traceback.print_exc()
        finally:
            self.driver.quit()

    def _generate_url(self, event_name, year):
        url = f"https://aclweb.org/anthology/events/{event_name.lower()}-{year}/"
        return url


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--event", "-e", type=str, required=True, help="event name(specify an event name listed in https://aclweb.org/anthology/)")
    parser.add_argument("--year", "-y", type=str, required=True, help="year (yyyy)")
    parser.add_argument("--output", "-o", type=str, required=True, help="path to output directory")
    parser.add_argument("--verbose", "-v", action="store_true", default=False, help="show progress of downloading")
    parser.add_argument("--chrome-driver", "-d", type=str, default="/usr/local/bin/chromedriver", help="path to chromedriver")
    parser.add_argument("--xvfb", "-x", action="store_true", help="use xvfb virtual display for chromedriver")
    args = parser.parse_args()

    downloader = ACLAnthologyDownloader(chrome_driver_path=args.chrome_driver, use_xvfb=args.xvfb)
    downloader.download(args.event, args.year, args.output, verbose=args.verbose)
