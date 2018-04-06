import os
import re
import sys
import math
import imghdr
import argparse
from pathlib import Path
from time import sleep, strftime, gmtime
from multiprocessing import Process, Queue, active_children

def printerr(string):
    print(f"\033[0;31m {string} \033[0m")

def printinfo(string):
    print(f"\033[0;33m {string} \033[0m")

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.firefox.options import Options
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import (
        ElementNotVisibleException
    )
except ModuleNotFoundError:
    printinfo("Selenium not found... you won't be able to use some kaliya features")

try:
    from bs4 import BeautifulSoup
    import requests
except ModuleNotFoundError:
    printerr("Not found beautiful_soup or requests  package")


class Fourchan:

    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument(
                'urls', nargs='*', help='Url of thread with images, Multiple urls in one command is posssible', default =[]
                )
        parser.add_argument('-n', '--name', action='store_true', help='Option to set own name')
        parser.add_argument('-r', '--reload', action='store_true', help='Refresh script every 5 minutes to check for new images')
        parser.add_argument('-l', '--last', action='store_true', help='Show history information about downloading images')
        parser.add_argument('-f', '--forum', action='store_true', help='Search data not from FORUM web pages e.g. normal site')
        parser.add_argument('-i', '--ignore', action='store_true', help='Ignore title setup just use founded on site')
        parser.add_argument('-s', '--selenium', action='store_true', help='Activate selenium mode to load site with healess mode (use for sites that load iamges later)')

        self.args = parser.parse_args()
        self.supported_files = {
                    "jpeg"   : {"mn": "FFD8", "size": 4},
                    "png"    : {"mn": "89504E470D0A1A0A", "size": 16},
                    "gif89a" : {"mn": "474946383961", "size": 12},
                    "gif87a" : {"mn": "474946383761", "size": 12},
                    }
        self.database = f"{str(Path.home())}/.kaliya.list"
        self.workpath = os.path.realpath(os.getcwd())
        self.path = ""
        #self.pool = []
        #self.error_download = 0
        #self.que = Queue()
        if not any(vars(self.args).values()):
            parser.print_help()
            sys.exit(0)

        if self.args.last:
            self.access_to_db(False)
            sys.exit(0)

        self.main()
        while self.args.reload:
            sleep(300)
            self.main()

        #[job.join() for job in self.pool]
        #print(f"[Info] {self.que.qsize()} images has been downloaded number of error {self.error_download} occured")

    def check_value(self, value, error_line):
        if not value:
            printerr(f"[Error] {error_line} : {value}")
            sys.exit(2)
        return value

    def main(self):
        if isinstance(self.args.urls,list):
            for link_thread in self.args.urls:
                    self.download_images(link_thread)
        else:
            self.download_images(self.args.urls)

    def access_to_db(self, sync_data, seq=""):
        with open(self.database, "a+") as stream:
            if sync_data:
                stream.seek(0)
                if not seq in list(filter(lambda a: a,map(lambda x: x.strip(),stream.readlines()))):
                    stream.seek(2)
                    stream.write(f"{seq}\n")
            else:
                stream.seek(0)
                for index, line in enumerate(list(filter(lambda a: a,map(lambda x:x.strip(),stream.readlines())))):
                    print(f"{index}) {line}")

    def get_url_data(self, url, normal):
        try:
            if self.args.selenium and normal:
                options = Options()
                options.add_argument("--headless")
                driver = webdriver.Firefox(firefox_options=options)
                driver.wait = WebDriverWait(driver, 5)
                driver.get(url)
                try:
                    myElem = WebDriverWait(
                        driver,
                        3
                    ).until(EC.presence_of_element_located((By.CLASS_NAME,"overlay")))
                    driver.execute_script("window.scrollBy(0,250)", "")
                    return driver.page_source
                except ElementNotVisibleException:
                    printerr("Loading took too much time!")
            else:
                response = requests.request('get', url)
                return response.text if normal else response.content
        except Exception as e:
            printerr(f"[Error] Found url:{url} is not valid\n stderr: {e}")
            #self.error_download += 1

    def find_images(self, soup_):
        for a in soup_.find_all('a',{"class": "overlay"}, href=True):
            print(a)
        if not self.args.forum:
            data = [link.get("href") for link in soup_.find_all('a', href=True)]
        else:
            data = [link.get("src") for link in soup_.find_all("img")]
        return list(
                map(lambda a: (a,a.split('/')[-1]),
                    filter(lambda l: any(list(
                        map(lambda t: t in l, ("jpeg","jpg","png", "gif")
                            ))), data
                        )
                    )
                )

    def shut_down(self):
        for process in active_children():
                printinfo(f"Shutting down process {process}")
                process.terminate()
                process.join()

    def download_images(self, link):

        def loop(data):
            if data and self.path:
                [create_img(f"{self.path}", link, *spec) for spec in data]

        def create_img(direct, link, link_address, link_name):

            def supported_format(mag_num):
                return any(list(map(lambda x: mag_num[:x["size"]] == x["mn"],
                    self.supported_files.values())))

            def broken_link(site, link):
                return f"{site}/{link}" if not link.startswith("http") or not link.count('.') > 1 else link

            def fix_https(link):
                return f"https:{link}" if not link.startswith("http") else link

            if self.args.forum:
                sleep(2.0)
            if not os.path.isfile(f"{direct}/{link_name}"):
                if self.args.forum:
                    image_dat = self.get_url_data(fix_https(broken_link(link,link_address)), False)
                else:
                    image_dat = self.get_url_data(fix_https(link_address), False)
                if image_dat:
                    magic_number = "".join(['{:02X}'.format(b) for b in image_dat[:8]][:8])
                    if supported_format(magic_number):
                        with open(f"{direct}/{link_name}",'wb') as img:
                            img.write(image_dat)
                            #self.que.put(True)
                        print(f"[{strftime('%H:%M:%S', gmtime())}] {direct}/{link_name}")

        def parse_title(soup_, data):
            try:
                return soup_.title.text
            except:
                printinfo("[Warning] page title not found")
                return ""

        def calculate_optimum(parsed_dat):
            try:
                process_num = math.ceil(len(parsed_data)/10)
                process_field = [[] for pa in range(process_num)]
                PROC_NUM = len(parsed_dat)/process_num
                for index in range(process_num):
                    process_field[indx] = parsed_dat[
                            int(index*PROC_NUM):int((index*PROC_NUM)+PROC_NUM)
                            ]
                return process_field
            except Exception as e:
                printerr(f"Problem occurent when calculating correct process data separation: {e}")
                return []

        website_data = self.get_url_data(link, True)
        cleaned_page_title = ""
        soup = BeautifulSoup(
                self.check_value(website_data, "Not found web data"),
                "html.parser")
        page_title = parse_title(soup, website_data)
        if page_title:
            cleaned_page_title = " ".join(sorted(
                    list(filter(lambda x: '/' not in x,
                        map(lambda y: y.strip(), page_title.split('-')))),
                    key=lambda x: len(x), reverse=False))
        else:
            page_title = printinfo("[INFO] Sorry could not find page title.\nSet title: ")
        if cleaned_page_title:
            if not self.args.ignore:
                printinfo(f"[INFO] Found this title: {cleaned_page_title}")
                print("1) Continue\n2) Setup own title")
                try:
                    answer = int(input("Choice: "))
                except ValueError:
                    answer = int(input("Please input number to choose next step: "))
                if answer == 2:
                    cleaned_page_title = input("Folder name: ")
            os.makedirs(f"{self.workpath}/{cleaned_page_title}", exist_ok=True)
            self.path = f"{self.workpath}/{cleaned_page_title}"
        else:
            os.makedirs(f"{self.workpath}/4chan{page_title}", exist_ok=True)
            self.path = f"{self.workpath}/4chan{page_title}"

        parsed_data = self.check_value(
                self.find_images(soup),
                "Didn't find any supported images, try -f switch"
                )
        self.access_to_db(True, link)
        for pf in calculate_optimum(parsed_data):
            Process(target=loop, args=(pf,)).start()
            #self.pool.append(Process(target=loop, args=(pf,)))
            #self.pool[-1].start()

if __name__ == "__main__":
    try:
        fChan = Fourchan()
    except KeyboardInterrupt:
        if fChan:
            fChan.shut_down()
