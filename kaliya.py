"""Kalia image web scraper

Uses multiple methods to download images from specific source
"""

__version__ = '0.7'
__author__ = 'axell'

import math
import os
import re
import sys

from multiprocessing import Process, active_children
from pathlib import Path
from time import gmtime, sleep, strftime

import click
import requests
from bs4 import BeautifulSoup


def echo(string):
    """Later on this could be set to point to file
    instead of stdout
    """
    action = {
        "warning": f"\033[0;33m {string} \033[0m",
        "error":   f"\033[0;31m {string} \033[0m",
        "succes":  f"\033[92m {string} \033[0m",
    }

    print(action.get(re.search(r"\w+", string).group().lower(), string))

def check_value(value, error_line):
    if not value:
        #FIXME: print rather varibable than value
        echo(f"[Error] {error_line} \n {value or ''}")
        raise ValueError(f"Missing value, {error_line}")

    return value

def write_to_db(data):
    with open(f"{Path.home()}/.kaliya.list", "a+") as stream:
        stream.seek(0)
        current_data = [val.strip() for val in stream.readlines() if val]

        if not data or data in current_data:
            return

        stream.seek(2)
        stream.write(f"{data}\n")

def print_from_db():
    """
    TODO: setup sqlite3 database https://docs.python.org/3.8/library/sqlite3.html
    TODO: DRY can I fix this?
    """
    with open("f{str(Path.home())}/.kaliya.list", "a+") as stream:
        current_data = [x.strip() for x in stream.readlines() if x]

        stream.seek(0)
        for index, line in enumerate(current_data):
            echo(f"{index}): {line}")

def get_data_from_url_advanced(link):
    echo(
            "[WARNING] Using tools to download content - this will take some time..."
            )
    if True:
        echo("[SUCCES] Images had been found")
    #TODO: Here goes pypeteer data
    return None


def get_data_from_url_simple(url, secondary_mode=False):
    """
    Normal stands for downloading bytes like images etc, normal true in
    to search images
    """
    try:
        check_value(url, "Bad link")
        url = f"http://{url.split('//')[1]}"
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        return requests.get(url, headers=headers)
    except Exception as err:
        echo(f"[Error] {err}")


def find_images_in_website_data(soup, website_data, website_url):
    parsed_link_data = [link.get("href") for link in soup.find_all("a", href=True)]
    parsed_img_data  = [link.get("src") for link in soup.find_all("img")]
    found_url_images = []

    for data in (parsed_link_data + parsed_img_data):
        if re.match(r"[https?:]?\/\/[\w\.\/\d-]*\.(jpe?g|png|gif)", data):
            found_url_images.append(data)
        elif re.match(r"[-a-zA-Z\d]+\.(jpe?g|png|gif)", data):
            found_url_images.append(f"{website_url}/{data}") 
        else:
            continue
    return found_url_images

def shut_down():
   for process in active_children():
        echo(f"Shutting down process {process}")
        process.terminate()
        process.join()

def supported_format(magic_num):
    supported_files = {
            "jpeg": {"magic_number": "FFD8", "size": 4},
            "png": {"magic_number": "89504E470D0A1A0A", "size": 16},
            "gif89a": {"magic_number": "474946383961", "size": 12},
            "gif87a": {"magic_number": "474946383761", "size": 12},
            }

    for key, value in supported_files.items():
        if magic_num[:value["size"]] == value["magic_number"]:
            return key

    return None

def separate_data_into_proceses(parsed_data):
    proc_num = math.ceil(len(parsed_data) / 10)
    number = int(len(parsed_data) / proc_num)

    for i in range(proc_num):
        index = int(i * number)
        yield parsed_data[index:(index + number)]

def create_image_file(directory, url):

    def detect_and_fix(link):
        #Should I really need to fix link here?
        return link

    def get_magic_num(data):
        return "".join(["{:02X}".format(b) for b in data[:8]][:8])

    file_name = url.split('/')[-1]
    full_path = f"{directory}/{file_name}"

    if os.path.isfile(full_path):
        return

    image_data = get_data_from_url_simple(detect_and_fix(url)).content
    if supported_format(get_magic_num(image_data)):
        with open(full_path, "wb") as image_file:
            image_file.write(image_data)
        echo(f"[{strftime('%H:%M:%S', gmtime())}] {full_path}")
    else:
        echo("[ERROR] Image not supported")


def download_images_from_url(url, workpath):

    def parse_title(soup):
        try:
            title = soup.title.text
            clean_data = [data.strip() for data in title.split('-') if not '/' in data]
            title = " ".join(sorted(clean_data, key=lambda x: len(x), reverse=False))
        except AttributeError:
            echo(
                    "[WARNING] Sorry could not find page title.\nSet title: "
                    )
            title = input("Set new title: ")
        return title


    website_data = get_data_from_url_simple(url)
    soup = BeautifulSoup(
            check_value(website_data, "Not found web data").text, 
            "html.parser"
        )

    workpath = f"{workpath}/{parse_title(soup)}"
    os.makedirs(workpath, exist_ok=True)
    echo("[SUCCES] Creating folder")

    found_parsed_img = find_images_in_website_data(soup, website_data, url)
    if not found_parsed_img:
        echo(
            "[WARNING] No images found using advanced search"
        )
        found_parsed_img = get_data_from_url_advanced(url)
        check_value(found_parsed_img, "Didn't find any supported images:")

    write_to_db(url)
    for values in separate_data_into_proceses(found_parsed_img):
        try:
            Process(target=loop, args=(workpath,values)).start()
        except ValueError:
            continue

def loop(path, values):
    check_value(values, "Bad input for process")
    for link in values:
        create_image_file(path, link)

@click.command()
@click.argument("urls", nargs=-1)
@click.option("-r", "--refresh", is_flag=True, help="Refresh script every 5 minutes to check for new images")
@click.option("-l", "--last", is_flag=True, help="Show history information about downloading images")
@click.option("-i", "--ignore", is_flag=True, help="Ignore title setup just use founded on site")
def main(urls, refresh, last, ignore):
    def process_all_data(input_links):
        """
        If this goes second time for same data it will
        skip already data that exist locally
        """
        for link in input_links:
            try:
                download_images_from_url(link, Path.cwd())
            except ValueError:
                continue

    if last:
        print_from_db()
        return

    while True:
        process_all_data(urls)
        if not refresh:
            break
        sleep(300)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        shut_down()
        sys.exit()
