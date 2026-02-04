# data/

This directory contains the output of the web scraper.

## Output of first scrape: URLs by tag
The name of each output file corresponds to the tags in the input file, e.g., "tag-desktop-pet.txt" These plaintext files contain URLs for all the games with that tag, separated with line breaks.  

A game can have multiple tags, so the same URL may be present in multiple files.

## Output of second scrape: metadata by URL
The name of the file is specified when running the scraper, e.g., "itch-metadata.csv". This CSV file is generated cumulatively as the scraper runs to mitigate data loss if the webdriver hangs.
