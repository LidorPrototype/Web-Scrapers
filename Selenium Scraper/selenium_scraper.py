import os, time, datetime
from datetime import timedelta
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from time import sleep
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
import platform
import zipfile
import gzip
import shutil
import requests

# Number of stores: 27
# https://www.gov.il/he/departments/legalInfo/cpfta_prices_regulations

class Foodmarket1():
    
    def __init__(self, _url_, _exports_, _prefix_):
        """ Init fumction that will setup basis functionality """
        self.url = _url_
        self.rows = []
        self.free_hrefs = {
                "type_1": ["https://www.kingstore.co.il/Food_Law/Main.aspx", "http://maayan2000.binaprojects.com/Main.aspx", "http://zolvebegadol.binaprojects.com/Main.aspx", "http://shuk-hayir.binaprojects.com/Main.aspx", "http://shefabirkathashem.binaprojects.com/Main.aspx", "http://paz.binaprojects.com/Main.aspx"],
                "type_2": ["http://matrixcatalog.co.il/NBCompetitionRegulations.aspx", "http://www.matrixcatalog.co.il/"],
                "type_3": ["http://141.226.222.202/"],
                "type_4": ["http://prices.super-pharm.co.il/?type=&date=&page={}"],
                "type_5": ["http://publishprice.mega.co.il/", "http://publishprice.mega-market.co.il/", "http://publishprice.ybitan.co.il/"],
                "type_6": ["http://prices.shufersal.co.il/"], # Download yesterday everything it have + todays FULLS
            }
        self.auth_hrefs = {
            "no_pass": {
                "doralon": ["https://url.publishedprices.co.il/login"],
                "TivTaam": ["https://url.publishedprices.co.il/login"],
                "HaziHinam": ["https://url.publishedprices.co.il/login"],
                "yohananof": ["https://url.publishedprices.co.il/login"],
                "osherad": ["https://url.publishedprices.co.il/login"],
                "Stop_Market": ["https://url.publishedprices.co.il/login"],
                "politzer": ["https://url.publishedprices.co.il/login"],
                "freshmarket": ["https://url.publishedprices.co.il/login"],
                "Keshet": ["https://url.publishedprices.co.il/login"],
                "RamiLevi": ["https://url.publishedprices.co.il/login"],
                "SuperCofixApp":["https://url.publishedprices.co.il/login"],
            },
            "yes_pass": {
                "SalachD": {"pass": "12345", "url": "https://url.publishedprices.co.il/login"},
                "Paz_bo": {"pass": "paz468", "url": "https://url.publishedprices.co.il/login"},
            },
        }
        self.exports = os.getcwd() + _exports_
        self.download_delay = 0.1
        self.prefix_ = _prefix_
        self.yesterday_date_MDY = datetime.datetime.strftime(datetime.datetime.now() - timedelta(1), '%m/%d/%Y')
        self.yesterday_date_DMY = datetime.datetime.strftime(datetime.datetime.now() - timedelta(1), '%d/%m/%Y')
        self.yesterday_date_YMD = datetime.datetime.strftime(datetime.datetime.now() - timedelta(1), '%Y/%m/%d')
        self.current_type = "type_1"

    def setup_driver(self):
        """ 
            An advance function to the init one, it's also a must function, without it it will not work
            This function creates and configure everything that is related to the selenium library and driver
        """
        chrome_options = Options()
        chrome_options.add_experimental_option("detach", True)
        preferences = {
            "download.default_directory": self.exports,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "directory_upgrade": True,
            'profile.default_content_setting_values.automatic_downloads': 1,
            "safebrowsing.enabled": True 
            }
        # chrome_options.headless = True
        chrome_options.add_experimental_option("prefs", preferences)
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    def set_url(self, new_url):
        self.url = new_url

    def _teardown_(self):
        self.driver.quit()

    def ensure_dir(self, folder, flat: bool = False):
        """
            If the directory :folder: does not exists, create it
        """
        _location_ = self.exports + devider + folder
        if flat:
            _location_ = folder
        try:
            if not os.path.exists(_location_):
                os.makedirs(_location_)
        except OSError as e:
            raise

    def move_files_to(self, dir_name, print_flag = False):
        """ Moves files from the base exports folder to a deeper desired one """
        sleep(self.download_delay * 10)
        file_names = os.listdir(self.exports)
        _target_ = self.exports + devider + dir_name
        if print_flag:
            print("Number of files: ", len(file_names))
        for file_name in file_names:
            if '.' in file_name:
                try:
                    file_name_path = os.path.join(self.exports, file_name)
                    if 'Unconfirmed' not in file_name and not file_name.endswith('.tmp'):
                        try:
                            with zipfile.ZipFile(file_name_path, 'r') as zip_ref:
                                for name in zip_ref.namelist():
                                    innerfilename = zip_ref.extract(name, _target_)
                        except zipfile.BadZipFile:
                            with gzip.open(file_name_path, 'rb') as f_in:
                                gzip_xml_name = _target_ + "\\" + f_in.name.split('\\')[-1].split('.')[0] + ".xml"
                                with open(gzip_xml_name, 'wb') as f_out:
                                    shutil.copyfileobj(f_in, f_out)
                    else:
                        os.remove(file_name)
                except Exception as e:
                    print(str(e))
                finally:
                    os.remove(file_name_path)
            else: pass

    def split_hrefs(self):
        for row in self.rows:
            if str(row[-1]).strip() == "":
                self.free_hrefs.append(row[1])
            elif str(row[-1]).strip() != "":
                self.auth_hrefs.append(row[1])

    def wait_for_element(self, element_tuple, delay_timer = 15):
        """ Delay Function For Rendering of a desired element """
        WebDriverWait(self.driver, delay_timer).until(
            EC.presence_of_element_located(element_tuple)
        )
        sleep(delay_timer // 4)

    def try_maximize(self):
        try:
            self.driver.maximize_window()
        except:
            return -1

    def fix_date_padding(self, old_date):
        new_dates = []
        temp = old_date.split("/")
        for item in temp:
            if len(item) < 2:
                new_dates.append(f"0{item}")
            else:
                new_dates.append(item)
        return new_dates[0] + "/" + new_dates[1] + "/" + new_dates[2]

    def check_td_row(self, click_cell, name_cell, _date_, auth_key: bool = False, sufersal_flag: bool = False) -> bool:
        validity = False
        _date_ = _date_.replace("-", "/").replace("_", "/")
        if click_cell.text.strip().endswith('xml'):
            validity = False
        if (
            (
                ((name_cell.text.strip().startswith("PromoFull") or name_cell.text.strip().startswith("PriceFull") or name_cell.text.strip().startswith("StoresFull")) 
                or 
                (name_cell.text.strip().startswith("Stores") and auth_key))
            and (_date_.strip() == self.yesterday_date_DMY or _date_.strip() == self.yesterday_date_MDY or _date_.strip() == self.yesterday_date_YMD))
            ):
            validity = True
        if sufersal_flag:
            if _date_.strip() == self.yesterday_date_DMY or _date_.strip() == self.yesterday_date_MDY or _date_.strip() == self.yesterday_date_YMD:
                validity = True
            if name_cell.text.strip().startswith("PromoFull") or name_cell.text.strip().startswith("PriceFull") or name_cell.text.strip().startswith("StoresFull"):
                validity = True
        return validity

    # Deprecated
    def layer1_get_list_of_hrefs(self, xpath_command):
        # Open webpage with the given url and maximizing the window
        self.driver.get(self.url)
        self.wait_for_element((By.XPATH, xpath_command))
        self.try_maximize()
        elements = self.driver.find_elements_by_xpath(xpath_command)
        for item in elements:
            tds = item.find_elements_by_xpath('.//td')
            if isinstance(tds[1], WebElement):
                all_a = tds[1].find_elements_by_xpath('.//a')
                hrefs = []
                for a in all_a:
                    href = a.get_attribute('href')
                    hrefs.append(href)
                self.rows.append((tds[0].text, hrefs, tds[2].text))

    def layer2_website_types_1_2_3_4(self, new_url, xpath_command):
        """ This function is suitable for websites of types 1 till 4 (can find them in the init function or in self object) """
        self.url = new_url
        store_name = [i for i in self.url.split('.') if 'www' not in i][0]
        try:
            if 'prices' in store_name or 'publishprice' in store_name:
                store_name = [i for i in self.url.split('.') if 'www' not in i][1]
            if 'https://' in store_name:
                store_name = store_name.replace("https://", "")
            if 'http://' in store_name:
                store_name = store_name.replace("http://", "")
            if new_url == self.free_hrefs['type_2'][0] or new_url == self.free_hrefs['type_2'][1]:
                store_name = new_url.split('/')[-1].split('.')[0]
        except: pass
        store_name = self.prefix_ + store_name
        self.ensure_dir(store_name)
        self.driver.get(self.url)
        self.try_maximize()
        sleep(1)
        if self.current_type == "type_3":
            self.layer2_website_type_2_3_fix_date(input_area_xpath="//div[@id='MainContent_search']//ul", correct_input_xpath="//input[@id='MainContent_MainContent_txtDate']", input_cell_number=2)
            sleep(1)
        if self.current_type == "type_2":
            self.layer2_website_type_2_3_fix_date(input_area_xpath="//div[@id='MainContent_search']//ul", correct_input_xpath="//input[@id='MainContent_txtDate']", input_cell_number=3)
            sleep(1)
        self.wait_for_element(((By.XPATH, xpath_command)))
        # Find the 'containers' in each row
        elements = self.driver.find_elements_by_xpath(xpath_command)
        elements = elements[1:]
        for item in elements:
            # Find the correct cell in each row
            tds = item.find_elements_by_xpath('.//td')
            click_td = tds[-1]
            name_td = tds[0]
            date_td = tds[-2]
            if self.current_type == "type_1" or self.current_type == "type_3":
                date_str = date_td.text.split()[-1]
            if self.current_type == "type_2":
                date_str = date_td.text.split()[0]
            if self.current_type == "type_4":
                date_td = tds[2]
                date_str = date_td.text.split()[0]
                name_td = tds[1]
                print(date_str, "<-->", self.yesterday_date_DMY, "<-->", self.yesterday_date_MDY, "<-->", self.yesterday_date_YMD)
            if tds[-4] == 'xml' or tds[-3] == 'xml' or tds[-5] == 'xml':
                continue
            if self.check_td_row(click_td, name_td, date_str):
                    click_td.click()
                    sleep(1)
            sleep(self.download_delay)
        # Use the function move_files_to twice because sometimes it will not count some of them (because of the massive size of them all)
        self.move_files_to(store_name)
        self.move_files_to(store_name)

    def layer2_website_type_2_3_fix_date(self, input_area_xpath, correct_input_xpath, input_cell_number) -> None:
        ul_cels = self.driver.find_elements_by_xpath(input_area_xpath)
        date_ul_cel = ul_cels[input_cell_number]
        date_input = date_ul_cel.find_element_by_xpath(correct_input_xpath)
        date_input.clear()
        date_input.send_keys(self.yesterday_date_DMY)
        date_input.send_keys(Keys.ENTER)

    def layer2_website_type_5(self, new_url, xpath_command):
        """  This function is suitable for websites of type 5 (can find them in the init function or in self object) """
        self.url = new_url
        store_name = [i for i in self.url.split('.') if 'www' not in i][0]
        if 'prices' in store_name or 'publishprice' in store_name:
            store_name = [i for i in self.url.split('.') if 'www' not in i][1]
        if 'https://' in store_name:
            store_name = store_name.replace("https://", "")
        if 'http://' in store_name:
            store_name = store_name.replace("http://", "")
        store_name = self.prefix_ + store_name
        self.ensure_dir(store_name)
        self.driver.get(self.url)
        self.try_maximize()
        sleep(1.5)
        # Find the 'containers' each row
        elements = self.driver.find_elements_by_xpath(xpath_command)
        elements = elements[3:]
        urls = []
        for item in elements:
            # Add the currect url to our urls list for next pages
            if (item.text.split('/')[0] == "".join(self.yesterday_date_DMY.split('/')[::-1]) 
                or item.text.split('/')[0] == "".join(self.yesterday_date_MDY.split('/')[::-1])
                or item.text.split('/')[0] == "".join(self.yesterday_date_YMD.split('/')[::-1])):
                urls.append(self.url + f"/{item.text.split('/')[0]}/")
                break
        for __url in urls:
            # For each URL move to the next function for it in order to get it's data
            self.layer3_website_type_5(__url, xpath_command, start_type=3)

    def layer3_website_type_5(self, new_url, xpath_command, start_type = 1):
        """ This function is an advancment from function layer2_website_type_5 in order to get one step in and get all of the data """
        self.url = new_url
        store_name = [i for i in self.url.split('.') if 'www' not in i][0]
        if 'prices' in store_name or 'publishprice' in store_name:
            store_name = [i for i in self.url.split('.') if 'www' not in i][1]
        if 'https://' in store_name:
            store_name = store_name.replace("https://", "")
        if 'http://' in store_name:
            store_name = store_name.replace("http://", "")
        store_name = self.prefix_ + store_name
        self.ensure_dir(store_name)
        self.driver.get(self.url)
        self.try_maximize()
        sleep(1.5)
        # Find all of the rows on the given page
        elements = self.driver.find_elements_by_xpath(xpath_command)
        elements = elements[start_type:]
        for item in elements:
            # Detect all the cells that are in the current row
            tds = item.find_elements_by_xpath('.//td')
            try:
                # Find the download tag in the currect cell (currect cell number is examine manually)
                click_td = tds[1].find_element_by_xpath('.//a')
                name_td = tds[1]
                date_td = tds[2]
                if self.check_td_row(click_td, name_td, date_td.text.split()[0].replace('-', '/')):
                    click_td.click()
                sleep(self.download_delay)
            except Exception as e:
                print("Exception: ", str(e))
        # Use the function move_files_to twice because sometimes it will not count some of them (because of the massive size of them all)
        self.move_files_to(store_name)
        self.move_files_to(store_name)
        
    def layer2_website_type_6_fix_date(self) -> None:
        input_area_xpath = "//th"
        input_cell_number = 1
        ul_cels = self.driver.find_elements_by_xpath(input_area_xpath)
        date_ul_cel = ul_cels[input_cell_number]
        date_ul_cel.click()

    def layer2_website_type_6(self, new_url, xpath_command1, xpath_command2):
        """ This function is an advancment from function layer2_website_type_5 in order to get one step in and get all of the data """
        self.url = new_url
        store_name = [i for i in self.url.split('.') if 'www' not in i][0]
        if 'prices' in store_name or 'publishprice' in store_name:
            store_name = [i for i in self.url.split('.') if 'www' not in i][1]
        if 'https://' in store_name:
            store_name = store_name.replace("https://", "")
        if 'http://' in store_name:
            store_name = store_name.replace("http://", "")
        store_name = self.prefix_ + store_name
        self.ensure_dir(store_name)
        self.driver.get(self.url)
        self.try_maximize()
        sleep(1)
        self.layer2_website_type_6_fix_date()
        final_page = 94
        # This page is a dynamic page, so loop for all the pages numbers (final page number examine manually)
        for i in range(1, final_page + 1):
            # Find all of the rows in the table of current page
            elements = self.driver.find_elements_by_xpath(xpath_command1)
            for item in elements:
                try:
                    # Detect the cells in the row and select downloadable one (number is examine manually)
                    tds = item.find_elements_by_xpath('.//td')
                    click_td = tds[0]
                    name_td = tds[-2]
                    date_td = tds[1]
                    date_str = self.fix_date_padding(date_td.text.split()[0])
                    if self.check_td_row(click_td, name_td, date_str, sufersal_flag = True):
                        click_td.click()
                    sleep(self.download_delay)
                except:
                    print("LEN: ", len(tds))
            self.move_files_to(store_name)
            next_page = self.driver.find_elements_by_xpath(xpath_command2)
            for page_a in next_page:
                tds = page_a.find_elements_by_xpath('.//td')
                click_td = tds[0]
                all_a = click_td.find_elements_by_xpath('.//a')
                for a in all_a:
                    if a.text == '>':
                        a.click()
                        sleep(1)
                        break
            i += 1
        # Use the function move_files_to twice because sometimes it will not count some of them (because of the massive size of them all)
        self.move_files_to(store_name)
        self.move_files_to(store_name)

    def use_free_links(self):
        """
            Driver function responisble for all of the links that do not require username and / or password
            Each loop in here are responisble for a different type of website (even though methods may be the same, the xpath shoul dbe changed)
        """
        for _link_ in self.free_hrefs['type_1']:
            print(_link_)
            xpath_website_type_1 = "//table[@id='myTable']//tbody//tr"
            self.current_type = "type_1"
            try:
                _obj.layer2_website_types_1_2_3_4(_link_, xpath_website_type_1)
            except Exception as e: 
                print("use_free_links - type_1 - Exception: ", str(e))
        for _link_ in self.free_hrefs['type_2']:
            print(_link_)
            xpath_website_type_2_3 = "//div[@id='download_content']//tbody//tr"
            self.current_type = "type_2"
            try:
                _obj.layer2_website_types_1_2_3_4(_link_, xpath_website_type_2_3)
            except Exception as e: 
                print(str(e))
        for _link_ in self.free_hrefs['type_3']:
            print(_link_)
            xpath_website_type_2_3 = "//div[@id='download_content']//tbody//tr"
            self.current_type = "type_3"
            try:
                _obj.layer2_website_types_1_2_3_4(_link_, xpath_website_type_2_3)
            except Exception as e: 
                print(str(e))
        for _link_ in self.free_hrefs['type_4']:
            start = 1
            end = 256
            self.current_type = "type_4"
            for page in range(start, end + 1):
                current_link = _link_.format(page)
                print(current_link)
                xpath_website_type_2 = "//div[@class='file_list']//tbody//tr"
                try:
                    _obj.layer2_website_types_1_2_3_4(current_link, xpath_website_type_2)
                except Exception as e: 
                    print(str(e))   
        for _link_ in self.free_hrefs['type_6']:
            print(_link_)
            xpath_website_type_6_1 = "//div[@id='gridContainer']//tbody//tr"
            xpath_website_type_6_2 = "//div[@id='gridContainer']//tfoot//tr"
            self.current_type = "type_6"
            try:
                _obj.layer2_website_type_6(_link_, xpath_website_type_6_1, xpath_website_type_6_2)
            except Exception as e: 
                print(str(e))

    def use_long_free_links(self):
        """
            Special function for the first website of type 5, this function was created so it will run this website as the last website of the scrape.
            This is because this website take a very long time to download everything, so if push come to shove we can cancel the download and only this 
            website will have short data (because sometimes it can take more then a full day).
        """
        for _link_ in self.free_hrefs['type_5']:
            print(_link_)
            xpath_website_type_5 = "//div[@id='files']//tbody//tr"
            self.current_type = "type_5"
            try:
                _obj.layer2_website_type_5(_link_, xpath_website_type_5)
            except Exception as e: 
                print(str(e))

    def use_auth_links(self):
        """
            Driver function responisble for all of the links that do require username and / or password
            Firs tloop is for all the links the require username alone
            Second loop is for all the links that require username and password together
        """
        for _username in self.auth_hrefs['no_pass']:
            for _link_ in self.auth_hrefs['no_pass'][_username]:
                print(_link_)
                xpath_after_auth = "//div[@id='fileList_wrapper']//table[@id='fileList']//tbody//tr"
                self.current_type = "auth:no_pass"
                try:
                    self.apply_authentication(url=_link_, username=_username)
                    self.download_data_after_auth(xpath_command=xpath_after_auth)
                    store_name = _username
                    store_name = self.prefix_ + store_name
                    self.ensure_dir(store_name)
                    self.move_files_to(store_name)
                    self.move_files_to(store_name)
                except Exception as e: 
                    print(str(e))
        for _username in self.auth_hrefs['yes_pass']:
            _password = self.auth_hrefs['yes_pass'][_username]['pass']
            _url = self.auth_hrefs['yes_pass'][_username]['url']
            print(_url)
            xpath_after_auth = "//div[@id='fileList_wrapper']//table[@id='fileList']//tbody//tr"
            self.current_type = "auth:yes_pass"
            try:
                self.apply_authentication(url=_url, username=_username, password=_password)
                self.download_data_after_auth(xpath_command=xpath_after_auth)
                store_name = _username
                store_name = self.prefix_ + store_name
                self.ensure_dir(store_name)
                self.move_files_to(store_name)
                self.move_files_to(store_name)
            except Exception as e: 
                print(str(e))

    def apply_authentication(self, url, username, password=None):
        """ Function for all of the auth links (they got the same login form) that will log in to the suitable data """
        self.set_url(new_url=url)
        xpath_input_user = "//div[@id='login']//div[@class='form-group']//input[@id='username']"
        xpath_input_pass = "//div[@id='login']//div[@class='form-group']//input[@id='password']"
        xpath_sign_in = "//div[@id='login']//div[@class='row']//button[@id='login-button']"
        # Open webpage with the given url and maximizing the window
        self.driver.get(self.url)
        self.try_maximize()
        self.wait_for_element((By.XPATH, xpath_input_user))
        input_ref_user = self.driver.find_element_by_xpath(xpath_input_user)
        input_ref_user.send_keys(username)
        if password:
            input_ref_pass = self.driver.find_element_by_xpath(xpath_input_pass)
            input_ref_pass.send_keys(password)
        submit = self.driver.find_element_by_xpath(xpath_sign_in)
        submit.click()

    def download_data_after_auth(self, xpath_command):
        """ This function is after the authentication has completed, and now it's time to parse the pages and download the data """
        self.try_maximize()
        self.wait_for_element((By.XPATH, xpath_command))
        elements = self.driver.find_elements_by_xpath(xpath_command)
        for element in elements:
            try:
                tds = element.find_elements_by_xpath('.//td')
                click_td = tds[0].find_element_by_xpath('.//a')
                name_td = tds[0]
                date_td = tds[3]
                date_str = date_td.text.split()[0]
                # Trying to find extra date when it's hidden
                try:
                    date_str_hidden = date_td.find_element_by_xpath('.//time').get_attribute("datetime")
                    date_str_hidden = date_str_hidden.split('T')[0].replace('-', '/')
                    if len(date_str_hidden.split('/')) == 3: 
                        # print(date_str_hidden, "<------>", date_str_hidden.split('/'), "<------->", len(date_str_hidden.split('/')), "<----->", len(date_str_hidden.split('/')) == 3)
                        date_str = date_str_hidden
                except: 
                    pass
                # Fixing the date padding
                date_str = self.fix_date_padding(date_str)
                # print("<----->", date_str)
                # print(f"************************************************************* {self.current_type} *************************************************************")
                # print("click_td.text: ", click_td.text[::-1], "<->", "click_td.text.endswith('xml'): ", click_td.text.endswith('xml'))
                # print("name_td.text.strip() ", name_td.text.strip(), "<->", "startswith(\"PromoFull\"): ", name_td.text.strip().startswith("PromoFull"), "startswith(\"PriceFull\"): ", name_td.text.strip().startswith("PriceFull"), "startswith(\"StoresFull\"): ", name_td.text.strip().startswith("StoresFull"))
                # print("click_td.text.endswith('txt') or click_td.text.endswith('TXT': ", click_td.text.endswith('txt') or click_td.text.endswith('TXT'))
                # print("self.check_td_row(click_td, name_td, date_str): ", self.check_td_row(click_td, name_td, date_str, auth_key=True))
                # print("date_str", date_str, "<->", f"== {self.yesterday_date_MDY}: ", date_str == self.yesterday_date_MDY)
                if click_td.text.endswith('txt') or click_td.text.endswith('TXT'):
                    continue
                if self.check_td_row(click_td, name_td, date_str, auth_key=True):
                    # print('Download It!')
                    if click_td.text.strip().endswith("xml") and self.current_type.startswith("auth"):
                        ahref = str(tds[0].find_element_by_xpath('.//a').get_attribute("href"))
                        res = requests.get (ahref)
                        stores_xml = self.exports + "/" + name_td.text.strip()
                        with open(stores_xml, 'w') as f:
                            f.write(res.text)
                    else:
                        click_td.click()
                    sleep(self.download_delay)
            except:
                self.driver.find_element_by_xpath('//p//a').click()
            sleep(self.download_delay)

def download_data():
    """ 
        Driver Function for this entire program 
        Avarage Download Time: 5 hours
    """
    _obj.setup_driver()
    _obj.use_free_links()
    _obj.use_auth_links()
    _obj.use_long_free_links()
    print("-------------------------------------------------------------------------------------------------------")
    print("------------------------------------------------- End -------------------------------------------------")
    print("-------------------------------------------------------------------------------------------------------")
    _obj._teardown_()

if __name__ == '__main__':
    global devider, _date_
    start = time.time()
    curr_system = platform.system()
    if curr_system == "Windows":
        devider = "\\"
    elif curr_system == "Linux":
        devider = "/"
    _date_ = datetime.datetime.strftime(datetime.datetime.now() - timedelta(1), '%Y_%m_%d')
    _url = 'https://www.gov.il/he/departments/legalInfo/cpfta_prices_regulations'
    input_dir = f'{devider}ExportsInputs'
    output_dir = f'{devider}ExportsOutputs'
    _obj = Foodmarket1(_url, input_dir, _date_ + devider)
    _obj.ensure_dir(input_dir[len(devider):], flat=True)
    _obj.ensure_dir(output_dir[len(devider):], flat=True)
    download_data()
    end = time.time()
    time_dif = end - start
    print(f"This entire download took: {str(datetime.timedelta(seconds=int(time_dif)))} seconds")
