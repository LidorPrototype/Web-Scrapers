# Web Scraping

### Developer: L-ES

The web scrapers are:

    1) Selenium scraper of 30 websites
        - selenium_scraper.py: The selenium scraper, it will download from 30 different (some are similar) websited, it downloads into csv files all of the prices, its meant to 
                                run every day and download the final results of yesterday for each store or market in Israel.
        - apply_exe.py: This file takes 2-3 types of files from each store that we downloaded and it apply some simple math on it to calculate and see all the discounts
        - upload_azure_blob_containers.py: This file will upload the final parquet files that we got back from the .exe file on every store to Azure Blob Containers
    2) Amazon Scraper: Search for a term and scrape all the listings of it
    3) IMDb Scrapers:   (1,000 best movies)
        - One page scraper, takes a page and gather all the data from it  
        - Multi page scraper, same as the one page but also moves on all the pages of the list
    4) Israel Bank Scrapers:
        - About Section
        - Research Section
        - Statistics Section
        - Term Dictionary Section
        - Careers Section
    5) Twitter Scraper: Logs into a given account ( need to provide credentials ) search for a term and gather all the tweets data
    6) Yahoo Scraper: Go into 'Yahoo! Finance' a grab:
        - Financials tab data
        - Profile tab data
        - Statistic tab data
        - Historical Stock tab data


