import sys
from seleniumbase import SB
from bs4 import BeautifulSoup
import json
import random
from pathlib import Path


TEST = True

logger = None

all_tags = []

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


# main

if len(sys.argv) < 2:
    exit("usage: etl-itch.py tags_file")

if TEST:
    print("LOG: TEST mode is enabled:", file=logger)
    print("---- Fewer items will be extracted to reduce server load.", file=logger)
    print("---- Local data in test/ directory will be used, if present.", file=logger)

with open(sys.argv[1]) as fin:
    all_tags = fin.read().splitlines()

with SB(headed=True, uc=True) as sb:
    for elem in all_tags:
        fname = Path(elem + ".txt")

        uris = []

        if TEST:
            fname = "test" / fname
            if fname.exists():
                print("LOG: Local copy", fname, "found.", file=logger)
                with open(fname) as fin:
                    uris = fin.read().splitlines()
                continue

        print("LOG: Extracting URIs for", elem, "games...", file=logger)
        uris = extract_game_uris(sb, elem)
        print("LOG: Extracted", len(uris), "URIs.", file=logger)

        with open(fname, "w") as fout:
            for item in uris:
                print(item, file=fout)

if logger:
    logger.close()
