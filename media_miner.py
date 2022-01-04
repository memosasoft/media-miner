import requests as r
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup as b
import colorama
from fake_useragent import UserAgent
import time

from requests.sessions import session

index = 0

http = ""
https = ""
    
list_proxies = []
list_of_working_proxies = []
total_links = 0

memory = []
ua = UserAgent()

# init the colorama module
colorama.init()

GREEN = colorama.Fore.GREEN
GRAY = colorama.Fore.LIGHTBLACK_EX
RESET = colorama.Fore.RESET
YELLOW = colorama.Fore.YELLOW

# initialize the set of links (unique links)
internal_urls = set()
external_urls = set()
total_urls_visited = 0

#!/usr/local/bin/python
import configparser
configuration = configparser.ConfigParser()
configuration.read('config.env')

MAX_CRAWL = int(configuration.get('CONFIG','MAX_CRAWL'))
RELAX_TIME = float(configuration.get('CONFIG','RELAX_TIME'))
DOWNLOAD_OPTION = int(configuration.get('CONFIG','DOWNLOAD_OPTION'))
EXTERNAL_LINKS= int(configuration.get('CONFIG','EXTERNAL_LINKS'))
PROXY_ON = int(configuration.get('CONFIG','PROXY_ON'))
ROAMING_MODE = int(configuration.get('CONFIG','ROAMING_MODE'))
STARTING_URL = str(configuration.get('CONFIG','STARTING_URL'))

url_stopword = str(configuration.get('CONFIG','URL_STOP_WORD'))
media_files = str(configuration.get('CONFIG','MEDIA_FILES'))

def is_valid(url): 

    relax(RELAX_TIME)
    check_media(url)

    if (url.find("mailto:")>=0):
        dump_data("email.txt", url)
    if url.find("html")>=0 or url.find("php")>=0 or url.find("asp")>=0:
        print("VALID URL : " + url)
        parsed = urlparse(url)
        return bool(parsed.netloc) and bool(parsed.scheme)
    
    # STOPLIST FOR URLS
    url = url.lower()
    
    for stopword in url_stopword.split(","):
        if url.find(stopword.strip())>=0:
            print("INVALID OR BANNED URL : " + url)
            return False 

    verification = url.split("/")[-1] 
    if (verification.find(".")<0):
        parsed = urlparse(url)
        print("VALID URL : " + url)
        return bool(parsed.netloc) and bool(parsed.scheme)
    
    print("Invalid url: " + url)
    return False

def get_all_website_links(url):
    """
    Returns all URLs that is found on `url` in which it belongs to the same website
    """
    # all URLs of `url`
    urls = set()
    
    print("Preparing for download")
    relax(RELAX_TIME)
    
    try:
        # domain name of the URL without the protocol
        domain_name = urlparse(url).netloc
        
        session = r.Session()
            
        if PROXY_ON == 1:
            relax(RELAX_TIME)
            session.proxies = {
            'http': http,
            'https': https,
            }
        else:
            pass
            # session.proxies = ""

        print("Starting the requests qith URL: "  + url) 
        page = session.get(str(url), headers={'User-Agent': ua.random},timeout=40)  
        relax(RELAX_TIME)
        soup = b(page.text, 'lxml')

        print("Just downloaded url: " + url)
        relax(RELAX_TIME)
        
        for a_tag in soup.findAll("a"):
            href = a_tag.attrs.get("href")
            if href == "" or href is None:
                # href empty tag
                continue
            # join the URL if it's relative (not absolute link)
            href = urljoin(url, href)
            parsed_href = urlparse(href)
            # remove URL GET parameters, URL fragments, etc.
            href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path
            
            relax(RELAX_TIME)        
            
            if not is_valid(href):
                # not a valid URL
                check_media(href)
                continue
            if href in internal_urls:
                # already in the set
                print("Link all ready spidered")
                continue
            if domain_name not in href:
                # external link
                if href not in external_urls:
                    print(f"{GRAY}[!] External link: {href}{RESET}")
                    external_urls.add(href)
                    if ROAMING_MODE == 1:
                        urls.add(href)
                continue
            print(f"{GREEN}[*] Internal link: {href}{RESET}")
            urls.add(href)
            internal_urls.add(href)
            
            check_media(href)
    except Exception as e:
        print("MAJOR WITH REQUESTS ERROR")
        print(e)
        
    print("Spider found: " + str(len(urls)) + " links to spider")
    
    global total_links
    total_links = int(total_links) + int(len(urls))
    print("Total links in memory: " + str(total_links))
    
    return urls
        
def dump_data(file_name, data):
    if not data in memory:
        relax(RELAX_TIME)
        with open(file_name, "a") as file:    
            print("filename: " + file_name)
            print("data: " + data)
            file.write(data + "\n")
            file.close()   
    memory.append(data)

def remove_url_double(list, item):

    for url in list:
        if (url==item):
            list.remove(url)
            print("Urls double found in list : " + url)
    return list
    
# This function cleans urls liste from doubles and visited links
def endode_url(url):
    # Clean the url string
    url = str(url.strip())
    return url

def relax(s):
    time.sleep(s)

def check_media(url_extracted):

    print("Checking Media...")
    relax(RELAX_TIME)
    
    # Most common media files
    for media_ext in media_files.split(","):
        relax(RELAX_TIME)
        if url_extracted.find(str("."+media_ext.strip()))>=0:
            print("Hit media found in : " + url_extracted)
            downloadFile(url_extracted)
    
def downloadFile(url_extracted):
    
    global memory
    
    print("MEDIA FOUND starting PROCESS")
    print("MEDIA FOUND : " + url_extracted)

    import uuid
    filename = str(uuid.uuid4())
    file = url_extracted.split("/")[-1] 
    
    # Dump invalid urls
    # Request the profile picture of the OP:
    
    # Now use this like below,
    save_path = './media/'
   
    if (DOWNLOAD_OPTION==1):
        if url_extracted not in memory:
            import wget
            relax(RELAX_TIME)
            wget.download(url_extracted, save_path + file)
            relax(RELAX_TIME)
            memory.append(url_extracted)

    title = url_extracted
    ext = url_extracted.split(".")[-1] 
    file = url_extracted.split("/")[-1] 
    
    title = format_title(str(file), str(ext))

    # Dump invalid urls
    if(url_extracted.find(".mp4")<=1 and url_extracted.find("mp3")<=1):
        archive_filename = "ARCHIVE_MEDIA.M3U"

    # Dump invalid urls
    if(url_extracted.find(".mp3")>0):
        archive_filename = "ARCHIVE_MP3.M3U"

    # Dump invalid urls
    if(url_extracted.find(".mp4")>0):
        archive_filename = "ARCHIVE_MP4.M3U"

    if title not in memory: 
        with open(archive_filename, "a") as file:    
            relax(RELAX_TIME)
            print("VOD url: " + url_extracted)
            EXTINF_text = "#EXTINF:-1, " + title 
            file.write(EXTINF_text + "\n")
            relax(RELAX_TIME)
            file.write(url_extracted + "\n")
            relax(RELAX_TIME)
            file.close()   
            memory.append(title)
    else:
        print("VIDEO ALL READY EXTRACTED")
        with open(archive_filename, "a") as file:    
            relax(RELAX_TIME)
            print("VOD url: " + url_extracted)
            EXTINF_text = "#EXTINF:-1, " + title 
            file.write(EXTINF_text + "\n")
            relax(RELAX_TIME)
            file.write(url_extracted + "\n")
            relax(RELAX_TIME)
            file.close()   
            memory.append(title)

    return True

def format_title(title, ext):
    title = title.replace("", "")
    title = title.replace(ext, "")
    title = title.replace(".", "")
    title = title.replace(",", "")
    title = title.replace("(", "")
    title = title.replace(")", "")
    title = title.replace("+", " ")
    title = title.replace("_", " ")
    title = title.replace("-", " ")
    title = title.replace(")", "")
    title = title.replace("%20", "")
    title = title.replace("%5B", "")
    title = title.replace("%5D", "")
    title = title.replace("14%", "")
    title = title.replace("%28", "")
    title = title.replace("%29", "")
    title = title.replace("%20", "")
    
    # Separate term that have capital letter
    full_title = ""
    for i in title:
        if (i.isupper()):
            full_title = full_title + " " + i.capitalize()
        else:
            full_title = full_title + i

    full_title = full_title.replace("  ", " ")
    cap_next = False
    full_title_final = ""
    for i in full_title:
        if (cap_next == True):
            full_title_final = full_title_final + i.capitalize()
            cap_next = False
            continue
        if (i == " "):
            full_title_final = full_title_final + i
            cap_next = True
        else:
            full_title_final = full_title_final + i
            cap_next = False
    
    full_title_final = full_title_final.replace("  ", " ")
    full_title_final = full_title_final.lstrip()
    full_title_final = full_title_final.strip()

    print("FINISHID FORMAT TITLE: " + str(full_title_final))
    title = full_title_final

    return title

def crawl(url):
    global total_urls_visited
    total_urls_visited += 1
    print(f"{YELLOW}[*] Crawling: {url}{RESET}")

    links = get_all_website_links(url)
    
    for link in links:
        crawl(link)

        if (total_urls_visited > MAX_CRAWL):
            total_urls_visited = 0
            exit(0)

def load_proxies():
    print("Preparing proxy connexion for session")

    with open("proxies", "r") as file:
        lines = file.readlines()
        for i in lines:    
            print("Adding proxy: " + str(i))
            list_proxies.append(i) 
    file.close()

    # find a working proxy
    for i in list_proxies:
        
        print("TESTING PROXY: " + i)

        print("I have integrated a basic and random proxy...")
        print("Get your http proxies list at:\n")
        print("https://openproxy.space/list\n")
        print("The system needs to test all proxies before starting...")
        print("proxies_working file will contain \"working proxies\'")
        print("once you have 20 proxies working dump them in \"proxies\" file")
        print("Next run the system will start much faster...")
        
        import requests as s
        
        s = r.Session()
        s.proxies = {
        'http': "http://" +i,
        'https': "https://" +i,
        }

        url = "https://www.google.com"
        try:
            page = s.get(url, headers={'User-Agent': ua.random},timeout=100)
            print(page)
            #and then check the response...
            if page.status_code == 200:
                print(i, 'is up!')

                print(i, 'Adding it to the proxy list')
                list_of_working_proxies.append(i)
                dump_data("Adding " + i + " to proxies_working file...", i)
            else:
                print(i, 'is down!')
        except:
            print(i, 'is down! Major TIMEOUT')

    print("Picking a random session proxy")
    import random 
    random_proxy = random.choice(list_of_working_proxies)
    print("proxy is: " + random_proxy)

    # Set the global values
    global http
    global https
    http = 'http://' + str(random_proxy)
    https = 'https://' + str(random_proxy)

def recursive_main(): 
    global index
    url = ""

    if (index<len(urls_to_spider)):
        url = urls_to_spider[index]
    
    if (index>=len(urls_to_spider)):
        print("[+] Total Internal links:", len(internal_urls))
        print("[+] Total External links:", len(external_urls))
        print("[+] Total URLs:", len(external_urls) + len(internal_urls))
        print("[+] Total crawled URLs:")

        domain_name = urlparse(url).netloc
    
        # save the internal links to a file
        with open(f"{domain_name}_internal_links.txt", "w") as f:
            for internal_link in internal_urls:
                print(internal_link.strip(), file=f)
                f.write(internal_link.strip())

        # save the external links to a file
        with open(f"{domain_name}_external_links.txt", "w") as f:
            for external_link in external_urls:
                print(external_link.strip(), file=f)
                f.write(external_link.strip())
                
                # this is crazy
                crawl(external_link) 
                recursive_main() 
        exit(0)
    
    index = index + 1
    crawl(url) 
    recursive_main() 

urls_to_spider = []
urls_to_spider.append(STARTING_URL)

if PROXY_ON == 1:          
    # urls to scrape
    urls_to_spider = ["https://archive.org/details/moviesandfilms","https://archive.org/details/movie_trailers","https://archive.org/details/moviesandfilms?and[]=mediatype%3A%22movies%22","https://archive.org/details/feature_films"]

    # loading more urls from urls.txt file
    with open("urls.txt", "r") as file:
        lines = file.readlines()
        for i in lines:    
            print("Adding urls to spider memory: " + str(i))
            urls_to_spider.append(i) 
        file.close()
else:
    # Archives.org urls to get media
    # urls_to_spider = ["https://archive.org/details/moviesandfilms","https://archive.org/details/movie_trailers","https://archive.org/details/moviesandfilms?and[]=mediatype%3A%22movies%22","https://archive.org/details/feature_films"]
        
    urls_to_spider = []
    urls_to_spider.append(STARTING_URL)
    

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Link Extractor Tool with Python")
    parser.add_argument("url", help="The URL to extract links from.")
    parser.add_argument("-m", "--max-urls", help="Number of max URLs to crawl, default is 30.", default=30, type=int)
    
    # args = parser.parse_args()
    # url = args.url
    
    # To protect you identity you should :

    # OPTION 1
    #
    # go get a list of free proxies 
    # dump some in the proxies file
    # The system will test and select one
    # for the spider run. It slows down 
    # the spider process but you are more 
    # protected
    #
    # https://openproxy.space/list

    # OPTION 2
    #
    # Get a vpn, You can get a free one
    # at https://protonvpn.com/
    # 
    # Don't forget to turn off the proxy

    # Load proxies from proxies file
    if (PROXY_ON==1):  
        list_proxies = load_proxies()
  
    recursive_main()

  