import re
import json
import csv
import requests
from io import StringIO
from bs4 import BeautifulSoup

url_stats = 'https://finance.yahoo.com/quote/{}/key-statistics?p={}'
url_profile = 'https://finance.yahoo.com/quote/{}/profile?p={}'
url_financials = 'https://finance.yahoo.com/quote/{}/financials?p={}'
stock = 'F'


def getFinancialsData():
    response = requests.get(url_financials.format(stock, stock))
    soup = BeautifulSoup(response.text, 'html.parser')
    pattern = re.compile(r'\s--\sData\s--\s')
    script_data = soup.find('script', text=pattern).contents[0]
    start = script_data.find("context") - 2
    json_data = json.loads(script_data[start:-12])
    annual_is = json_data['context']['dispatcher']['stores']['QuoteSummaryStore']['incomeStatementHistory'][
        'incomeStatementHistory']
    quarterly_is = json_data['context']['dispatcher']['stores']['QuoteSummaryStore']['incomeStatementHistoryQuarterly'][
        'incomeStatementHistory']
    annual_cf = json_data['context']['dispatcher']['stores']['QuoteSummaryStore']['cashflowStatementHistory'][
        'cashflowStatements']
    quarterly_cf = json_data['context']['dispatcher']['stores']['QuoteSummaryStore'][
        'cashflowStatementHistoryQuarterly']['cashflowStatements']
    annual_bs = json_data['context']['dispatcher']['stores']['QuoteSummaryStore']['balanceSheetHistory'][
        'balanceSheetStatements']
    quarterly_bs = json_data['context']['dispatcher']['stores']['QuoteSummaryStore']['balanceSheetHistoryQuarterly'][
        'balanceSheetStatements']
    annual_is_stmts = []
    annual_cf_stmts = []
    annual_bs_stmts = []
    quarterly_is_stmts = []
    quarterly_cf_stmts = []
    quarterly_bs_stmts = []
    # Annual
    for s in annual_is:
        statement = {}
        for key, val in s.items():
            try:
                statement[key] = val['raw']
            except TypeError:
                continue
            except KeyError:
                continue
        annual_is_stmts.append(statement)
    for s in annual_cf:
        statement = {}
        for key, val in s.items():
            try:
                statement[key] = val['raw']
            except TypeError:
                continue
            except KeyError:
                continue
        annual_cf_stmts.append(statement)
    for s in annual_bs:
        statement = {}
        for key, val in s.items():
            try:
                statement[key] = val['raw']
            except TypeError:
                continue
            except KeyError:
                continue
        annual_bs_stmts.append(statement)
    # Quarterly
    for s in quarterly_is:
        statement = {}
        for key, val in s.items():
            try:
                statement[key] = val['raw']
            except TypeError:
                continue
            except KeyError:
                continue
        quarterly_is_stmts.append(statement)
    for s in quarterly_cf:
        statement = {}
        for key, val in s.items():
            try:
                statement[key] = val['raw']
            except TypeError:
                continue
            except KeyError:
                continue
        quarterly_cf_stmts.append(statement)
    for s in quarterly_bs:
        statement = {}
        for key, val in s.items():
            try:
                statement[key] = val['raw']
            except TypeError:
                continue
            except KeyError:
                continue
        quarterly_bs_stmts.append(statement)
    print(annual_is_stmts)
    print(annual_cf_stmts)
    print(annual_bs_stmts)
    print(quarterly_is_stmts)
    print(quarterly_cf_stmts)
    print(quarterly_bs_stmts)


def getProfileData():
    response = requests.get(url_profile.format(stock, stock))
    soup = BeautifulSoup(response.text, 'html.parser')
    pattern = re.compile(r'\s--\sData\s--\s')
    script_data = soup.find('script', text=pattern).contents[0]
    start = script_data.find("context") - 2
    json_data = json.loads(script_data[start:-12])
    companyOfficers = json_data['context']['dispatcher']['stores']['QuoteSummaryStore']['assetProfile']['companyOfficers']
    longBusinessSummary = json_data['context']['dispatcher']['stores']['QuoteSummaryStore']['assetProfile'][
        'longBusinessSummary']  # Description
    secFilings = json_data['context']['dispatcher']['stores']['QuoteSummaryStore']['secFilings']['filings']
    summaryDetails = json_data['context']['dispatcher']['stores']['QuoteSummaryStore']['summaryDetail']
    profileData = (companyOfficers, longBusinessSummary, secFilings, summaryDetails)
    return profileData
    # return companyOfficers


def getStatistic():
    response = requests.get(url_stats.format(stock, stock))
    soup = BeautifulSoup(response.text, 'html.parser')
    pattern = re.compile(r'\s--\sData\s--\s')
    script_data = soup.find('script', text=pattern).contents[0]
    start = script_data.find("context") - 2
    json_data = json.loads(script_data[start:-12])
    defaultKeyStatistics = json_data['context']['dispatcher']['stores']['QuoteSummaryStore']['defaultKeyStatistics']
    return defaultKeyStatistics


def getHistoricalStockData():
    # stock_url = 'https://query1.finance.yahoo.com/v7/finance/download/F?period1=1589659203&period2=1621195203&
    #               interval=1d&events=history&includeAdjustedClose=true'
    # response = requests.get(stock_url)
    # wholeHistory = response.text
    stock_url = 'https://query1.finance.yahoo.com/v7/finance/download/F?'
    params = {
        'range': '5y',
        'interval': '1d',
        'events': 'history',
        'includeAdjustedClose': 'true',
    }
    response = requests.get(stock_url.format(stock), params=params)
    paramsHistory = response.text
    return paramsHistory


profile_data = getProfileData()
index = 0
for element in profile_data:
    print("<**********************************>")
    print(element)
    print("Type: " + str(type(element)) + ", Size: " + str(len(element)))
    if index < 3:
        print("Type: " + str(type(element[1])) + ", Size: " + str(len(element[1])))
        for item in element[1]:
            print("Type: " + str(type(item)) + ", Size: " + str(len(item)))
            break
    else:
        for elem in element:
            print("Type: " + str(type(elem)) + ", Size: " + str(len(elem)))
            print("<**********************************>")
            break
    index += 1
with open('dataProfile.json', 'w') as outfile:
    json.dump(profile_data, outfile)
# with open('profile_data.csv', 'w', newline='', encoding='utf-8') as f:
#     header = {'companyOfficers', 'longBusinessSummary', 'secFilings', 'summaryDetails'}
#     writer = csv.writer(f)
#     writer.writerow(header)
#     writer.writerows(profile_data)

# Check this link for csv in folders
# https://stackoverflow.com/a/26028591/8405296
