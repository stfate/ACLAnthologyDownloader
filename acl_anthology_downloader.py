#!/usr/bin/env python

"""
ACL Anthology Downloader
"""

import argparse
import json
from pathlib import Path
import re
import time
import traceback
import unicodedata
import urllib.request

from selenium_downloader_base import SeleniumDownloaderBase


class ACLAnthologyDownloader(SeleniumDownloaderBase):
    def __init__(self, chrome_driver_path="/usr/local/bin/chromedriver", use_xvfb=False):
        super().__init__(chrome_driver_path=chrome_driver_path, use_xvfb=use_xvfb)

    def download(self, event_name, year, output_dir, verbose=False):
        output_dir_path = Path(output_dir)
        if not output_dir_path.exists():
            output_dir_path.mkdir(parents=True)
        
        try:
            url = self.generate_url(event_name, year)
            self.driver.get(url)

            p_elem_list = self.driver.find_elements_by_xpath("//p[@class='d-sm-flex align-items-stretch']")
            meta = {}
            for p_elem in p_elem_list:
                title_elem_list = p_elem.find_elements_by_xpath("span[@class='d-block']/strong/a[@class='align-middle']")
                for title_elem in title_elem_list:
                    title = title_elem.text

                pdf_elem_list = p_elem.find_elements_by_xpath("span[@class='d-block mr-2 text-nowrap list-button-row']/a[@class='badge badge-primary align-middle mr-1']")
                for pdf_elem in pdf_elem_list:
                    if pdf_elem.text == "pdf":
                        url = pdf_elem.get_attribute("href")
                        if verbose:
                            print(f"download {url}...")
                        fid = Path(url).stem
                        title_formatted = self.format_title(title)
                        output_fn = output_dir_path / f"{fid}-{title_formatted}.pdf"
                        if not output_fn.exists():
                            try:
                                urllib.request.urlretrieve(url, output_fn)
                            except urllib.error.HTTPError as e:
                                print(e.reason)

                meta[fid] = title
                time.sleep(0.1)

            json.dump(meta, open(output_dir_path / "meta.json", "w"), ensure_ascii=False, indent=2, sort_keys=True)
        except:
            traceback.print_exc()
        finally:
            self.driver.quit()

    def generate_url(self, event_name, year):
        url = f"https://aclweb.org/anthology/events/{event_name.lower()}-{year}/"
        return url

    def format_title(self, title):
        title_formatted = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode()
        title_formatted = re.sub("[^\w\s-]", "", title_formatted).strip().lower()
        title_formatted = re.sub("[-\s]+", "-", title_formatted)

        return title_formatted


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--event", "-e", type=str, required=True, help="event name(specify an event name listed in https://aclweb.org/anthology/)")
    parser.add_argument("--year", "-y", type=str, required=True, help="year (yyyy)")
    parser.add_argument("--output", "-o", type=str, required=True, help="path to output directory")
    parser.add_argument("--verbose", "-v", action="store_true", default=False, help="show download progress")
    parser.add_argument("--chrome-driver", "-d", type=str, default="/usr/local/bin/chromedriver", help="path to chromedriver")
    parser.add_argument("--xvfb", "-x", action="store_true", help="use xvfb virtual display for chromedriver")
    args = parser.parse_args()

    downloader = ACLAnthologyDownloader(chrome_driver_path=args.chrome_driver, use_xvfb=args.xvfb)
    downloader.download(args.event, args.year, args.output, verbose=args.verbose)
