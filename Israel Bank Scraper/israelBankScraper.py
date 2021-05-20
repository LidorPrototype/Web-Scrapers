import csv
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import time

# The urls to scrape data from
url_about = 'https://www.boi.org.il/he/AboutTheBank/Pages/Default.aspx'
url_research = 'https://www.boi.org.il/he/Research/Pages/Default.aspx'
url_statistics_series = 'https://www.boi.org.il/he/DataAndStatistics/Pages/Series.aspx'
url_education_dictionary = 'https://www.boi.org.il/he/Education/Glossary/Pages/Default.aspx'
url_students_jobs = 'https://careers.boi.org.il/index.html?FTXT=&F1C=משרות+לסטודנטים&F2C='

driver = webdriver.Chrome()


# Careers Scraping
def getCareersData():
    driver.get(url_students_jobs)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    jobs_inners = soup.find_all('div', {'class': 'inner'})
    jobs_headers = ['Title', 'Number', 'Location', 'Type', 'Last Submission Date', 'Link']
    __jobs = []
    for item in jobs_inners:
        __job = []
        title = item.find('div', {'class': 'title-container'})
        description = (item.find('div', {'class': 'listing-details'})).find_all('div', {'class', 'line'})
        link = 'https://careers.boi.org.il/' + (item.find('div', {'class': 'button-container'})).a.get('href')
        __job.append(title.h3.text)
        __job.append(description[0].find('span', {'class', 'value'}).text.strip())
        __job.append(description[1].find('span', {'class', 'value'}).text.strip())
        __job.append(description[2].find('span', {'class', 'value'}).text.strip())
        __job.append(description[3].find('span', {'class', 'value'}).text.strip())
        __job.append(link)
        __jobs.append(__job)
    _jobs = (jobs_headers, __jobs)
    return _jobs


# Education-Glossary-Dictionary Scraping
def getDictionaryData():
    driver.get(url_education_dictionary)
    titles = ['Word', 'Definition']
    divBody = driver.find_element_by_class_name('BoiTermsWrapper')
    descriptionList = divBody.find_element_by_class_name('BoiTerms')
    definitionTerms = descriptionList.find_elements_by_xpath('.//dt')
    for item in definitionTerms:
        item.click()
    describeTerms = descriptionList.find_elements_by_xpath('.//dd')
    _definitions = []
    for index in range(0, len(definitionTerms)):
        _definition = [definitionTerms[index].text, describeTerms[index].text]
        _definitions.append(_definition)
    _definitions = (titles, _definitions)
    return _definitions


# DataAndStatistics-Series Scraping
def getStatisticsData():
    driver.get(url_statistics_series)
    pages = driver.find_element_by_id('BoiPages').find_elements_by_xpath('.//option')
    max_page = len(pages)
    statistics = getStatistics(max_page, max_page)
    return statistics


def getStatistics(number_of_pages, __max_page):
    _max_page = 1
    if number_of_pages > __max_page:
        _max_page = __max_page
    else:
        _max_page = number_of_pages
    table_headers = ['תאור הסדרה', 'תדירות', 'יחידות', 'בסיס מחירים', 'ניכוי עונתיות', 'עדכון אחרון', 'קוד סדרה',
                     'מקור הנתונים', 'סוג הנתונים', 'עיבוד הנתונים', 'תיעוד']
    pageData = []
    for index in range(0, _max_page):
        pageData.extend(extractTableData())
        time.sleep(1.0)
        nextButtonClick()
    statistics = (table_headers, pageData)
    return statistics


def extractTableData():
    while True:
        try:
            table = driver.find_element_by_id('BoiSeriesResultsTable')
            break
        except NoSuchElementException:
            pass # ignore
    tableRows = table.find_elements_by_xpath('.//table/tbody/tr')
    tableHeaders = tableRows[0].find_elements_by_xpath('.//th')
    headers = []
    for item in tableHeaders[:-3]:
        headers.append(item.text)
    headers.append("Extra Information")
    tableData = tableRows[1].find_elements_by_xpath('.//td')
    rowsData = []
    rowsExtraData = []
    for index in range(1,31, 3):
        rowsData.append(getRowData(tableRows[index]))
    for index in range(2,31, 3):
        rowsExtraData.append(getExtraRowData(tableRows[index]))
    for index in range(0,10):
        rowsData[index].extend(rowsExtraData[index])
    return rowsData


def getRowData(_row):
    _tableData = _row.find_elements_by_xpath('.//td')
    _rowData = []
    for item in _tableData[:-3]:
        _rowData.append(item.text)
    idx = (len(_tableData) - 3)
    _tableData[idx].click()
    return _rowData


def getExtraRowData(_row):
    _tableData = _row.find_elements_by_xpath('.//td/div/p')
    _rowExtraData = []
    for _p in _tableData:
        _rowExtraData.append(_p.text)
    return _rowExtraData


def nextButtonClick():
    driver.find_element_by_id('btnNext').click()


# Scrape the about url data
def getResearchData():
    driver.get(url_research)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    # Making the page display the max rows that it have
    number_of_results_dropdown = soup.find('select', {'id': 'selNumOfResults'})
    selector = driver.find_element_by_id('selNumOfResults')
    selector.click()
    options = selector.find_elements_by_xpath('//option[text()="100"]')
    options[0].click()
    btn = driver.find_element_by_id('btnSearchPublicationFilter')
    btn.click()
    page_cards = driver.find_elements_by_xpath('//div[@class="TitleAuthorDateBriefLink"]')
    researches = []
    for card in page_cards:
        notice = getNoticeData(card)
        researches.append(notice)
    return researches


def getNoticeData(_card):
    title = _card.find_element_by_xpath('.//h5').text
    author = _card.find_element_by_xpath('.//div["class=@Author"]').text
    creation_date = _card.find_elements_by_xpath('.//span')[0].text.replace(' ', '').replace('|', '')
    brief = _card.find_elements_by_xpath('.//span')[1].text
    link = _card.find_element_by_xpath('.//a').get_attribute('href')
    notice = (title, author, creation_date, brief, link)
    return notice


# Scrape the about url data
def getAboutData():
    driver.get(url_about)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    titles = soup.find_all('h3', {'class': 'WpTitle'})
    bodies = soup.find_all('div', {'class': 'WpBody'})
    data_titles = []
    data_bodies = []
    data_clean_bodies = []
    for index in range(0, len(titles)):
        title = titles[index].text.strip()
        body = bodies[index].text.strip()
        data_titles.append(title)
        data_bodies.append(body)
        for item in data_bodies:
            data_clean_bodies.append(item.replace('\n', ' ').replace('\u200b', ' ').replace('\xa0', ' ').strip())
    data_clean_bodies = list(dict.fromkeys(data_clean_bodies))
    about = (data_titles, data_clean_bodies)
    return about

