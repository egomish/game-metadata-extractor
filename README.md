# Game Metadata Extractor

This web scraper pulls publicly available data from [itch.io](https://itch.io/) using [SeleniumBase](https://seleniumbase.io/). It does this in two passes. In the first pass, game URIs are extracted based on tags. In the second pass, relevant metadata is extracted to CSV based on game URIs.

## Required Packages

- [seleniumbase](https://seleniumbase.io/help_docs/install/)
- [lxml](https://lxml.de/installation.html)

## Usage

The scraper takes two positional arguments: an input file and an output file.  

The input file must be a plaintext file of valid itch.io tags separated by line breaks.  

The output will be a CSV file of relevant game metadata, including the game's URI, title, and tags.  

## Options

When the `use_cache` flag is raised, the scraper will check for existing output files before fetching data from itch.io.  

If local data is found in the first scraping pass (game URIs by tag), new requests will not be made for that tag.  

If local data is found for the second pass of scraping (game metadata by URI), local data will be loaded and then metadata for any new URIs found in the first pass will be extracted and appended to the existing CSV file.  

> [!NOTE]
> There is an issue with SeleniumBase that can result in the web driver hanging without the underlying web socket being properly closed. When this happens, it's safe to terminate the script on the command line (using [Control-C](https://en.wikipedia.org/wiki/Control-C)) and start it again with the same parameters (provided `use_cache` is enabled). The second pass of scraping, where this issue occurs, has a checkpointing system so that data is saved to the output file in incremental batches.  

When the `TEST` flag is raised, the scraper will only make one server request per scraping pass. This is to minimize burden on the itch.io servers while testing.  

> [!NOTE]
> This scraper can take a long time to run. This is by design--delays are included to avoid hammering the itch.io servers with requests. Do not reduce the wait time to make this script run faster unless you're certain you won't overburden the servers!  


# About

This web scraper was originally created as an internship project for the University of Michigan [Computer and Video Game Archive](https://www.lib.umich.edu/locations-and-hours/computer-and-video-game-archive) by [Evan Gomish](https://www.linkedin.com/in/evan-gomish), who at the time was pursuing their Master's of Science in Information at the University of Michigan School of Information.  
