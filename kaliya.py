import os
import re
import sys
import math
import imghdr
import argparse
from pathlib import Path
from time import sleep, strftime, gmtime
from multiprocessing import Process, Queue, active_children

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.firefox.options import Options
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import ElementNotVisibleException
except ModuleNotFoundError:
    print_caution(
        "[WARNING] Selenium not found... you won't be able to use some kaliya features"
    )

try:
    from bs4 import BeautifulSoup
    import requests
except ModuleNotFoundError:
    print_caution("[WARNING] Not found beautiful_soup or requests package")


def print_caution(string):
    caution = list(
        map(lambda x: x.lower(), string.replace("[", "").replace("]", "").split(" "))
    )
    if "error" in caution:
        print(f"\033[0;31m {string} \033[0m")
    elif "warning" in caution:
        print(f"\033[0;33m {string} \033[0m")
    elif "succes" in caution:
        print(f"\033[92m {string} \033[0m")
    else:
        print(string)


class Kaliya:
    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "urls",
            nargs="*",
            help="Url of thread with images, Multiple urls in one command is posssible",
            default=[],
        )
        parser.add_argument(
            "-r",
            "--reload",
            action="store_true",
            help="Refresh script every 5 minutes to check for new images",
        )
        parser.add_argument(
            "-l",
            "--last",
            action="store_true",
            help="Show history information about downloading images",
        )
        parser.add_argument(
            "-s",
            "--selenium",
            action="store_true",
            help="Activate selenium mode to load site with healess mode (use for sites that load iamges later)",
        )
        parser.add_argument(
            "-i",
            "--ignore",
            action="store_true",
            help="Ignore title setup just use founded on site",
        )

        self.args = parser.parse_args()
        self.supported_files = {
            "jpeg": {"mn": "FFD8", "size": 4},
            "png": {"mn": "89504E470D0A1A0A", "size": 16},
            "gif89a": {"mn": "474946383961", "size": 12},
            "gif87a": {"mn": "474946383761", "size": 12},
        }
        self.database = f"{str(Path.home())}/.kaliya.list"
        self.workpath = os.path.realpath(os.getcwd())
        self.secondary_mode = False
        self.path = ""
        # self.pool = []
        # self.error_download = 0
        # self.que = Queue()
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

        # [job.join() for job in self.pool]
        # print(f"[Info] {self.que.qsize()} images has been downloaded number of error {self.error_download} occured")

    def check_value(self, value, error_line):
        if not value:
            print_caution(f"[Error] {error_line} \n {value}")
            sys.exit(2)
        return value

    def main(self):
        if isinstance(self.args.urls, list):
            for link_thread in self.args.urls:
                self.download_images(link_thread)
        else:
            self.download_images(self.args.urls)

    def access_to_db(self, sync_data, seq=""):
        with open(self.database, "a+") as stream:
            if sync_data:
                stream.seek(0)
                if not seq in list(
                    filter(lambda a: a, map(lambda x: x.strip(), stream.readlines()))
                ):
                    stream.seek(2)
                    stream.write(f"{seq}\n")
            else:
                stream.seek(0)
                for index, line in enumerate(
                    list(
                        filter(
                            lambda a: a, map(lambda x: x.strip(), stream.readlines())
                        )
                    )
                ):
                    print(f"{index}) {line}")

    def get_url_data(self, url, normal):
        """ normal stands for downloading bytes like images etc, normal true in
        to search images"""
        self.check_value(url, " Broken link")
        try:
            if (self.args.selenium and normal) or self.secondary_mode:
                print_caution(
                    "[WARNING] Using selenium to download content - this could take some time..."
                )
                options = Options()
                options.add_argument("--headless")
                driver = webdriver.Firefox(firefox_options=options)
                # driver.wait = WebDriverWait(driver, 5)
                # myElem = WebDriverWait(driver,3).until(EC.presence_of_element_located((By.CLASS_NAME,"overlay")))
                driver.get(url)
                page_source = driver.page_source
                driver.quit()
                return page_source
            else:
                response = requests.request("get", url)
                return response.text if normal else response.content
        except Exception as e:
            print_caution(f"[Error] Found url:{url} is not valid\n stderr: {e}")
            if driver:
                driver.quit()
            # self.error_download += 1

    def find_images(self, soup_):
        # for a in soup_.find_all('a',{"class": "overlay"}, href=True):
        #    print(a)
        data = [link.get("href") for link in soup_.find_all("a", href=True)]
        # print(list(filter(lambda x: "jpg" in x or "png" in x ,data)))
        if not list(filter(lambda x: "jpg" in x or "png" in x, data)):
            data = [link for link in soup_.find_all("img")]
        return list(
            map(
                lambda a: (a, a.split("/")[-1]),
                filter(
                    lambda l: any(
                        list(map(lambda t: t in l, ("jpeg", "jpg", "png", "gif")))
                    ),
                    data,
                ),
            )
        )

    def use_selenium(self, link):
        self.secondary_mode = True
        website_data = self.get_url_data(link, True)
        sp = BeautifulSoup(website_data, "html.parser")
        return self.find_images(sp)

    def load_models(self):
        pass

    def shut_down(self):
        for process in active_children():
            print_caution(f"Shutting down process {process}")
            process.terminate()
            process.join()

    def download_images(self, link):
        def loop(data):
            if data and self.path:
                [create_img(f"{self.path}", link, *spec) for spec in data]

        def create_img(direct, link, link_address, link_name):
            def supported_format(mag_num):
                return any(
                    list(
                        map(
                            lambda x: mag_num[: x["size"]] == x["mn"],
                            self.supported_files.values(),
                        )
                    )
                )

            def broken_link(site, link):
                return (
                    f"{site}/{link}"
                    if not link.startswith("http") or not link.count(".") > 1
                    else link
                )

            def fix_https(link):
                return f"https:{link}" if not link.startswith("http") else link

            def detect_real_url(site_link, file_url):
                original = requests.get(fix_https(file_url))
                if original.status_code != 200:
                    new = requests.get(broken_link(site_link, file_url))
                    if new.status_code != 200:
                        print_caution("[ERROR] site not found")
                    else:
                        return broken_link(site_link, file_url)
                else:
                    return fix_https(file_url)

            # sleep(1.4)
            if not os.path.isfile(f"{direct}/{link_name}"):
                image_dat = self.get_url_data(
                    detect_real_url(link, link_address), False
                )
                magic_number = "".join(["{:02X}".format(b) for b in image_dat[:8]][:8])
                if supported_format(magic_number):
                    with open(f"{direct}/{link_name}", "wb") as img:
                        img.write(image_dat)
                        # self.que.put(True)
                    print(f"[{strftime('%H:%M:%S', gmtime())}] {direct}/{link_name}")
                else:
                    print_caution("[ERROR] image not supported")

        def parse_title(soup_, data):
            try:
                return soup_.title.text
            except:
                print_caution("[Warning] page title not found")
                return ""

        def calculate_optimum(parsed_dat):
            try:
                process_num = math.ceil(len(parsed_data) / 10)
                process_field = [[] for pa in range(process_num)]
                PROC_NUM = len(parsed_dat) / process_num
                for index in range(process_num):
                    process_field[index] = parsed_dat[
                        int(index * PROC_NUM) : int((index * PROC_NUM) + PROC_NUM)
                    ]
                return process_field
            except Exception as e:
                print_caution(
                    f"Problem occurent when calculating correct process data separation: {e}"
                )
                return []

        # start
        website_data = self.get_url_data(link, True)
        cleaned_page_title = ""
        soup = BeautifulSoup(
            self.check_value(website_data, "Not found web data"), "html.parser"
        )
        page_title = parse_title(soup, website_data)
        if page_title:
            cleaned_page_title = " ".join(
                sorted(
                    list(
                        filter(
                            lambda x: "/" not in x,
                            map(lambda y: y.strip(), page_title.split("-")),
                        )
                    ),
                    key=lambda x: len(x),
                    reverse=False,
                )
            )
        else:
            page_title = print_caution(
                "[INFO] Sorry could not find page title.\nSet title: "
            )
        if cleaned_page_title:
            if not self.args.ignore:
                print_caution(f"[INFO] Found this title: {cleaned_page_title}")
                print("1) Continue\n2) Setup own title")
                try:
                    answer = int(input("Choice: "))
                except ValueError:
                    answer = int(input("Please input number to choose next step: "))
                if answer == 2:
                    cleaned_page_title = input("Folder name: ")
            print_caution("[INFO] Creating folder...")
            os.makedirs(f"{self.workpath}/{cleaned_page_title}", exist_ok=True)
            self.path = f"{self.workpath}/{cleaned_page_title}"
        else:
            os.makedirs(f"{self.workpath}/4chan{page_title}", exist_ok=True)
            self.path = f"{self.workpath}/4chan{page_title}"

        parsed_data = self.find_images(soup)
        if not parsed_data:
            print_caution(
                "[WARNING] No images found switching to secondary mode using selenium..."
            )
            parsed_data = self.use_selenium(link)
            if parsed_data:
                print_caution("[SUCCES] Images has been found")
                self.secondary_mode = False
        self.check_value(parsed_data, "Didn't find any supported images:")
        self.access_to_db(True, link)
        for pf in calculate_optimum(parsed_data):
            Process(target=loop, args=(pf,)).start()
            # self.pool.append(Process(target=loop, args=(pf,)))
            # self.pool[-1].start()

    def __exit__(self):
        self.shut_down()


if __name__ == "__main__":
    assert sys.version_info >= (3, 6)
    try:
        Kaliya()
    except KeyboardInterrupt:
        sys.exit(0)
