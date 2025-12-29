import sys
from seleniumbase import SB
from bs4 import BeautifulSoup
import json
import random
from pathlib import Path
import csv
import re


TEST = True

logger = None

all_tags = []
all_uris = set()
all_metadata = []

def get_source(driver, url):
    driver.open(url)
    wait_time = random.random() * 3 + 0.75
    driver.sleep(wait_time)
    src = driver.get_page_source()
    return src

def extract_game_uris(driver, tag):
    n = 0
    game_uris = []
    while True:
        n += 1
        url = f"https://itch.io/games/{tag}?page={n}&format=json"
        src = get_source(driver, url)
        uris = soup_game_uris(src)
        game_uris.extend(uris)
        if len(uris) < 36:
            break
        if TEST:
            break
    return game_uris

def soup_game_uris(page_source):
    try:
        soup = BeautifulSoup(page_source, features="lxml")
        text = soup.find("pre").text
        js = json.loads(text)
        content = BeautifulSoup(js["content"], features="lxml")
        uris = content.find_all(True, {"attr", "game_link"})
        for i, elem in enumerate(uris):
            uris[i] = elem["href"]
        uris = set(uris)
        return uris
    except Exception as err:
        print("ERR: Exception occurred while souping game URIs.", file=logger)
        return []

def soup_game_metadata(page_source, uri):
    soup = BeautifulSoup(page_source, features="lxml")
    metadata = {}
    metadata["title"] = soup_game_title(soup)
    metadata["uri"] = uri
    metadata["tags"] = ";".join(soup_game_tags(soup))
    metadata["author"] = ";".join(soup_game_authors(soup))
    return metadata

def soup_game_tags(soup):
    tags = []
    hrefs = soup.find_all(href=True)
    for elem in hrefs:
        if elem["href"].startswith("https://itch.io/games/tag-"):
            tags.append(elem["href"].split("/")[-1])
    return tags

def soup_game_title(soup):
    gametitle = soup.find(class_="game_title")
    try:
        title = gametitle.text
    except:
        print("ERR: Failed to soup for title.", file=logger)
        title = None
    return title

def soup_game_authors(soup):
    authors = []
    try:
        hrefs = soup.find(string=re.compile("Author*")).parent.parent.find_all("a")
        for elem in hrefs:
            authors.append(elem["href"].replace("https://", "").split(".")[0])
    except:
        print("ERR: Failed to soup for authors.", file=logger)
        authors = []
    return authors


# main

if len(sys.argv) < 2:
    exit("usage: etl-itch.py tags_file")

if TEST:
    print("LOG: TEST mode is enabled:", file=logger)
    print("---- Fewer items will be extracted to reduce server load.", file=logger)
    print("---- Local data in test/ directory will be used, if present.", file=logger)

tags_file = sys.argv[1]

print("LOG: Reading", tags_file, "for tags to find on itch.io...", file=logger)

with open(tags_file) as fin:
    all_tags = fin.read().splitlines()

print("LOG: Starting webdriver...", file=logger)

with SB(headed=True, uc=True) as sb:
    for elem in all_tags:
        fname = Path(elem + ".txt")

        uris = []

        testname = "test" / fname
        if TEST and testname.exists():
            print("LOG: Local copy", testname, "found.", file=logger)
            with open(testname) as fin:
                uris = fin.read().splitlines()
        else:
            print("LOG: Extracting URIs for", elem, "games...", file=logger)
            uris = extract_game_uris(sb, elem)
            print("LOG: Extracted", len(uris), "URIs.", file=logger)

            with open(fname, "w") as fout:
                for item in uris:
                    print(item, file=fout)
        all_uris.update(uris)

    print("LOG: Extracting metadata for", len(all_uris), "games...", file=logger)
    for elem in all_uris:
        src = get_source(sb, elem)
        metadata = soup_game_metadata(src, elem)
        all_metadata.append(metadata)


outfile = Path("itch-metadata.csv")
print("LOG: Creating file", outfile, "to output metadata for", len(all_metadata), "games...", file=logger)
headers = ["title", "uri", "author", "tags"]

with open(outfile, "w", newline="") as dataout:
    fout = csv.DictWriter(dataout, fieldnames=headers, dialect="unix", quoting=csv.QUOTE_MINIMAL)
    fout.writeheader()
    fout.writerows(all_metadata)

if logger:
    logger.close()
