
import os
import re
import sys
import math
import imghdr
import argparse
import http.client
from time import gmtime, strftime, sleep
from multiprocessing import Process, Queue
from urllib.request import Request, urlopen, HTTPError, URLError

try:
    from bs4 import BeautifulSoup
except ModuleNotFoundError:
    print("[Warning] Not found beautiful soup package - install it for better perfomace")

class Fourchan:

    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('urls', nargs=1, help='Url of thread with images, Multiple urls in one command is posssible')
        parser.add_argument('-n', '--name', action='store_true', help='Option to set own name')
        parser.add_argument('-r', '--reload', action='store_true', help='Refresh script every 5 minutes to check for new images')
        parser.add_argument('-m', '--more', action='store_true', help='Show more information about downloading images')

        self.args = parser.parse_args()
        self.workpath = os.path.realpath(os.getcwd())
        #self.pool = []
        #self.error_download = 0
        self.path = ""
        #self.que = Queue()

        self.main()
        while self.args.reload:
            sleep(300)
            self.main()

        #[job.join() for job in self.pool]
        #print(f"[Info] {self.que.qsize()} images has been downloaded number of error {self.error_download} occured")

    def main(self):
        for link_thread in self.args.urls:
                self.download_images(link_thread)

    def get_url_data(self, url, normal):
        try:
            req = Request(url, headers={"User-Agent": "4chan Browser"})
        except ValueError:
            print(f"[Error] Founded url:{url} is not valid")
            sys.exit(1)
        try:
            if normal:
                return urlopen(req).read().decode("utf-8")
            else:
                return urlopen(req).read()
        except HTTPError as e:
            print(f"[Error] -> {e}")
            #self.error_download += 1

    def find_images(self, soup_, webpage_data):
        if soup_:
            return list(map(lambda a: (a,a.split('/')[-1]),filter(lambda l: any(list(map(lambda t: t in l,
                ("jpeg","jpg","png")))), [link.get("href") for link in
                    soup_.find_all('a',href=True)])))
        else:
            regex = '(\/\/i(?:s|)\d*\.(?:4cdn|4chan)\.org\/\w+\/(\d+\.(?:jpg|png|jpeg)))'
            return [(link,img) for link, img in list(set(re.findall(regex, webpage_data)))]

    def download_images(self, link):

        def loop(data):
            if data and self.path:
                for dat in data:
                    create_img(f"{self.workpath}/{self.path}", *dat)

        def create_img(direct, link, name):
            sleep(1.0)
            if not os.path.isfile(f"{direct}/{name}"):
                if not link.startswith("http"):
                    link = f"https:{link}"
                data = self.get_url_data(link, False)
                magic_number = "".join(['{:02X}'.format(b) for b in data[:8]][:8])
                if magic_number == "89504E470D0A1A0A" or\
                        magic_number[:4] == "FFD8":
                    with open(f"{direct}/{name}",'wb') as img:
                        img.write(data)
                        #self.que.put(True)

                    print(f"[{strftime('%H:%M:%S', gmtime())}] {direct}/{name}")

        def parse_title(soup_, data):
            if soup_:
                return soup_.title.text
            else:
                return website_data[website_data.find("<title>")+len("<title>"):website_data.find("</title>")]

        website_data = self.get_url_data(link, True)
        soup = BeautifulSoup(website_data,"html.parser")
        page_title = parse_title(soup, website_data)
        if page_title:
            #give user chance to choose?
            cleaned_page_title = max(
                    list(filter(lambda x: '/' not in x,
                        map(lambda y: y.strip(),page_title.split('-'))))
                    )
        else:
            page_title = input("Sorry Could not find title.\nSet title: ")
        if cleaned_page_title:
            os.makedirs(f"{self.workpath}/{cleaned_page_title}", exist_ok=True)
            self.path = cleaned_page_title
        else:
            os.makedirs(f"{self.workpath}/4chan{page_title}", exist_ok=True)
            self.path = page_title

        parsed_data = self.find_images(soup, website_data)

        """split data into arrays for multiprocessing"""
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
        pass
