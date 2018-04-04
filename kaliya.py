import os
import re
import sys
import math
import imghdr
import argparse
import requests
from pathlib import Path
from time import sleep, strftime, gmtime
from multiprocessing import Process, Queue, active_children

try:
    from bs4 import BeautifulSoup
except ModuleNotFoundError:
    print("[Warning] Not found beautiful soup package - install it for better perfomace")

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

        self.args = parser.parse_args()
        self.workpath = os.path.realpath(os.getcwd())
        self.database = f"{str(Path.home())}/.kaliya.list"
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
            print(f"[Error] {error_line} : {value}")
            sys.exit(2)
        return value

    def main(self):
        if isinstance(self.args.urls,list):
            for link_thread in self.args.urls:
                    self.download_images(link_thread)
        else:
            print(self.args.urls)
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
            response = requests.request('get', url)
            return response.text if normal else response.content
        except:
            print(f"[Error] Founded url:{url} is not valid")
            return False
            #self.error_download += 1

    def find_images(self, soup_, webpage_data):
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
                self.log.info(f"Shutting down process {process}")
                process.terminate()
                process.join()

    def download_images(self, link):

        def loop(data):
            if data and self.path:
                for dat in data:
                    create_img(f"{self.workpath}/{self.path}", *dat)

        def create_img(direct, link, name, data=""):
            #refactoring req
            #sleep(3.0)
            if not os.path.isfile(f"{direct}/{name}"):
                if not link.startswith("http"):
                    link = f"https:{link}"
                data = self.get_url_data(link, False)
                if data:
                    magic_number = "".join(['{:02X}'.format(b) for b in data[:8]][:8])
                    if magic_number == "89504E470D0A1A0A" or magic_number[:4] == "FFD8" or magic_number[:12] == "474946383961" or magic_number[:12] == "474946383761":
                        with open(f"{direct}/{name}",'wb') as img:
                            img.write(data)
                            #self.que.put(True)

                        print(f"[{strftime('%H:%M:%S', gmtime())}] {direct}/{name}")

        def parse_title(soup_, data):
            #refacotring req
            if soup_:
                return soup_.title.text
            else:
                return website_data[website_data.find("<title>")+len("<title>"):website_data.find("</title>")]

        website_data = self.get_url_data(link, True)
        soup = BeautifulSoup(
                self.check_value(website_data, "Not found web data"),
                "html.parser")
        page_title = parse_title(soup, website_data)
        print(page_title)
        if page_title:
            #give user chance to choose?
            cleaned_page_title = " ".join(sorted(
                    list(filter(lambda x: '/' not in x,
                        map(lambda y: y.strip(), page_title.split('-')))),
                    key=lambda x: len(x), reverse=False))
        else:
            page_title = input("Sorry Could not find title.\nSet title: ")
        if cleaned_page_title:
            os.makedirs(f"{self.workpath}/{cleaned_page_title}", exist_ok=True)
            self.path = cleaned_page_title
        else:
            os.makedirs(f"{self.workpath}/4chan{page_title}", exist_ok=True)
            self.path = page_title

        parsed_data = self.check_value(
                self.find_images(soup, website_data),
                "Didn't find any supported images"
                )
        #print(parsed_data); return
        #refacotring req - put into fucntion
        self.access_to_db(True, link)
        process_num = math.ceil(len(parsed_data)/10)
        process_field = [[] for pa in range(process_num)]
        theta = len(parsed_data)/process_num
        for i in range(process_num):
            process_field[i] = parsed_data[int(i*theta):int((i*theta)+theta)]
        for pf in process_field:
            Process(target=loop, args=(pf,)).start()
            #self.pool.append(Process(target=loop, args=(pf,)))
            #self.pool[-1].start()

if __name__ == "__main__":
    try:
        fChan = Fourchan()
    except KeyboardInterrupt:
        fChan.shut_down()
