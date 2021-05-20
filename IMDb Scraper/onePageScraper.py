import pandas as pd
import requests
from bs4 import BeautifulSoup

# Let the scraper know we want only english bases results
headers = {"Accept-Language": "en-US, en;q=0.5"}
# The url we want to scrape from
url = "https://www.imdb.com/search/title/?count=100&groups=top_1000&sort=user_rating"
# Getting the html data
results = requests.get(url, headers=headers)
# Using BeautifulSoup in order to parse the html data we got
soup = BeautifulSoup(results.text, "html.parser")
# Initialize empty lists in order to store the data in them
titles = []
years = []
time = []
imdbRatings = []
metaScores = []
votes = []
usGross = []
# Using BeautifulSoup variable in order to make sure to look just for the movies divs which is with the class:
#   "lister-item mode-advanced"
movieClassName = 'lister-item mode-advanced'
movieDiv = soup.find_all('div', class_=movieClassName)
# Initialize a for loop in order to make sure te scraper is iterating through every
# div container that is stored in the movieDiv variable
for container in movieDiv:
    # After inspecting the url page we found out each element we want tags tree,
    # with that knowledge we know which way to search for that specific data
    title = container.h3.a.text
    titles.append(title)
    year = container.h3.find('span', class_='lister-item-year').text
    years.append(year)
    runtime = container.find('span', class_='runtime').text if container.p.find('span', class_='runtime') else '-'
    time.append(runtime)
    ratings = float(container.strong.text)
    imdbRatings.append(ratings)
    mScore = container.find('span', class_='metascore').text if container.find('span', class_='metascore') else '-'
    metaScores.append(mScore)
    nv = container.find_all('span', attrs={'name': 'nv'})
    vote = nv[0].text
    votes.append(vote)
    grosses = nv[1].text if len(nv) > 1 else '-'
    usGross.append(grosses)
# A dataframe to organize all the data we collected inside
movies = pd.DataFrame({
    'movie': titles,
    'year': years,
    'timeMin': time,
    'imdb': imdbRatings,
    'metaScore': metaScores,
    'votes': votes,
    'usGrossMillions': usGross,
})
# Cleaning the data from whitespaces, unwanted symbols and everything that we do not need
movies['year'] = movies['year'].str.extract('(\\d+)').astype(int)
movies['timeMin'] = movies['timeMin'].str.extract('(\\d+)').astype(int)
movies['metaScore'] = pd.to_numeric(movies['metaScore'], errors='coerce')
movies['votes'] = movies['votes'].str.replace(',', '').astype(int)
movies['usGrossMillions'] = movies['usGrossMillions'].map(lambda x: x.lstrip('$').rstrip('M'))
movies['usGrossMillions'] = pd.to_numeric(movies['usGrossMillions'], errors='coerce')

# print(movies)
# print(movies.dtypes)
# to see where there are missing data and how much data is missing
# print(movies.isnull().sum())

movies.to_csv('100_movies.csv')




















