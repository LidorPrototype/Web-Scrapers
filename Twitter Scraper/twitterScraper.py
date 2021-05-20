import csv
from time import sleep
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import Chrome


def getTweetData(_card):
    """Extract data from tweet"""
    userName = card.find_element_by_xpath('.//span').text  # Username
    handle = card.find_element_by_xpath('.//span[contains(text(), "@")]').text  # Twitter handle
    try:
        postDate = card.find_element_by_xpath('.//time').get_attribute('datetime')  # Post date
    except NoSuchElementException:
        return
    # Content of the tweet
    comment = card.find_element_by_xpath('.//div[2]/div[2]/div[1]').text
    responding = card.find_element_by_xpath('.//div[2]/div[2]/div[2]').text
    tweetText = comment + responding  # Tweet whole text
    replyCount = card.find_element_by_xpath('.//div[@data-testid="reply"]').text  # Reply count
    retweetCount = card.find_element_by_xpath('.//div[@data-testid="retweet"]').text  # Retweet count
    likeCount = card.find_element_by_xpath('.//div[@data-testid="like"]').text  # Like count

    wholeTweet = (userName, handle, postDate, tweetText, replyCount, retweetCount, likeCount)  # Tweet touple complete
    return wholeTweet


# Create instance of web driver
url = 'http://www.twitter.com/login'
driver = Chrome()
# Navigate to url and login
driver.get(url)
driver.maximize_window()
username = driver.find_element_by_xpath('//input[@name="session[username_or_email]"]')
username.send_keys('INSERT YOUR USERNAME / EMAIL HERE')
myPassword = 'INSERT YOUR PASSWORD HERE'
password = driver.find_element_by_xpath('//input[@name="session[password]"]')
password.send_keys(myPassword)
password.send_keys(Keys.RETURN)
# Find search input and search for term
term = '#polynote'
search_input = driver.find_element_by_xpath('//input[@aria-label="Search query"]')
search_input.send_keys(term)
search_input.send_keys(Keys.RETURN)
# Navigate to 'Latest' tab
driver.find_element_by_link_text('Latest').click()
# Get all the tweets of the page
data = []
tweets_ids = set()
last_y_position = driver.execute_script("return window.pageYOffset;")
scrolling = True
while scrolling:
    page_cards = driver.find_elements_by_xpath('//div[@data-testid="tweet"]')
    for card in page_cards[-15:]:
        tweet = getTweetData(card)
        if tweet:
            tweet_id = ''.join(tweet)
            if tweet_id not in tweets_ids:
                tweets_ids.add(tweet_id)
                data.append(tweet)
    # Making the page scroll using JavaScript
    scroll_attempt = 0
    while True:
        driver.execute_script('window.scroll(0, document.body.scrollHeight);')
        sleep(1)
        # Checking scroll positions
        current_y_position = driver.execute_script("return window.pageYOffset;")
        if last_y_position == current_y_position:
            scroll_attempt += 1
            # end scroll region
            if scroll_attempt >= 3:
                scrolling = False
                break
            else:
                sleep(2)  # Attempt to scroll after 2 seconds ( in order to give the page enough time to load )
        else:
            last_y_position = current_y_position
            break
len(data)
with open('polynote_tweets.csv', 'w', newline='', encoding='utf-8') as f:
    header = {'UserName', 'Handle', 'Timestamp', 'Comments', 'Likes', 'Retweets', 'Text'}
    writer = csv.writer(f)
    writer.writerow(header)
    writer.writerows(data)
