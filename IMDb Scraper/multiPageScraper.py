from random import randint
from time import sleep
import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup

# Let the scraper know we want only english bases results
headers = {"Accept-Language": "en-US,en;q=0.5"}
# Initialize empty lists in order to store the data in them
titles = []
years = []
time = []
imdbRatings = []
metaScores = []
votes = []
usGross = []
# In order to scrape few pages we make a list of indexes according to imdb filing system
pages = np.arange(1, 1001, 100)
# For loop to iterate through all the pages
for page in pages:
    # Get current page html DOM elements
    page = requests.get("https://www.imdb.com/search/title/?groups=top_1000&sort=user_rating,desc&count=100&start="
                        + str(page) + "&ref_=adv_nxt",
                        headers=headers)
    # Using BeautifulSoup in order to parse the html data we got
    soup = BeautifulSoup(page.text, 'html.parser')
    movieDiv = soup.find_all('div', class_='lister-item mode-advanced')
    # Create a delay in order for the scraper to scrape all the data we need
    sleep(randint(2, 10))
    # Initialize a for loop in order to make sure te scraper is iterating through every
    # div container that is stored in the movieDiv variable
    for container in movieDiv:
        # After inspecting the url page we found out each element we want tags tree,
        # with that knowledge we know which way to search for that specific data
        title = container.h3.a.text
        titles.append(title)
        year = container.h3.find('span', class_='lister-item-year').text
        years.append(year)
        runtime = container.p.find('span', class_='runtime') if container.p.find('span', class_='runtime') else ''
        time.append(runtime)
        ratings = float(container.strong.text)
        imdbRatings.append(ratings)
        mScore = container.find('span', class_='metascore').text if container.find('span', class_='metascore') else ''
        metaScores.append(mScore)
        nv = container.find_all('span', attrs={'name': 'nv'})
        vote = nv[0].text
        votes.append(vote)
        grosses = nv[1].text if len(nv) > 1 else ''
        usGross.append(grosses)
# A dataframe to organize all the data we collected inside
movies = pd.DataFrame({
    'movie': titles,
    'year': years,
    'imdb': imdbRatings,
    'metaScore': metaScores,
    'votes': votes,
    'usGrossMillions': usGross,
    'timeMin': time
})
# Cleaning the data from whitespaces, unwanted symbols and everything that we do not need
movies['votes'] = movies['votes'].str.replace(',', '').astype(int)
movies.loc[:, 'year'] = movies['year'].str[-5:-1].astype(int)
movies['timeMin'] = movies['timeMin'].astype(str)
movies['timeMin'] = movies['timeMin'].str.extract('(\\d+)').astype(int)
movies['metaScore'] = movies['metaScore'].str.extract('(\\d+)')
movies['metaScore'] = pd.to_numeric(movies['metaScore'], errors='coerce')
movies['usGrossMillions'] = movies['usGrossMillions'].map(lambda x: x.lstrip('$').rstrip('M'))
movies['usGrossMillions'] = pd.to_numeric(movies['usGrossMillions'], errors='coerce')

print(movies)
print(movies.dtypes)
# to see where there are missing data and how much data is missing
print(movies.isnull().sum())

movies.to_csv('1000_movies.csv')
