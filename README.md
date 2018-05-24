# Kaliya
### Image downloader

Kaliya is image downloader. What that means? Well sometimes I search for new images everywhere and found some cool ones on 4chan. However could not find good script that would do the thign I wanted to do, so I wroted my own.

### What it does?

Exactly what would you expect to do. Imagine you are on specific site like 4chan wallpapers where are many many cool wallapers but you wanna donwload them all once and easily (whell until you stop script via `ctr-c`)

Just hit: `kaliya http://boards.4chan.org/wg/thread/7176937` and to your current directory downdloades or founded supported image like `jpeg`, `png`, `gif`. Program searches for page title, a that names the folder for the images. You can also use `-r` swich to let kaliya run for infinitive time. Kaliya also checks for current directory to not download same image again. 

At last kailya also saves all sites that you used it for downloading iamges. Hisory can be display via `kaliya -l`. 

Currently supports:
* 4chan and similar
* imgur 
* most sites even if they have later image loading

### Installation

To install script just enter `make` or `make install` that will install script and application. To uninstall hit `make uninstall`. Kaliya is currently python3 only.

#### Dependencies
To be better kaliya uses two non default libraries - beautiful soup, request... etc . All of them should be installed via makefile.Kaliya currently support firefox only. But is needed for sites with later image loading.

* requests
* bs4 (beautifulSoup4)
* selenium
* firefox (optional)

### TO DO
* add support for flicker
* make kaliya open to pull request for anohter sites

```text
usage: kaliya.py [-h] [-n] [-r] [-l] [-f] [-i] [-s] [urls [urls ...]]

positional arguments:
  urls            Url of thread with images, Multiple urls in one command is
                  posssible

optional arguments:
  -h, --help      show this help message and exit
  -n, --name      Option to set own name
  -r, --reload    Refresh script every 5 minutes to check for new images
  -l, --last      Show history information about downloading images
  -f, --forum     Search data not from FORUM web pages e.g. normal site
  -i, --ignore    Ignore title setup just use founded on site
  -s, --selenium  Activate selenium mode to load site with healess mode (use
                  for sites that load iamges later)
```
