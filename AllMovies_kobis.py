#-*- coding: utf-8 -*-
import urllib2  
import string
import os
import re
import sys
import time
import glob
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging  
import ssl
import Config
logging.basicConfig(filename=Config.LOG_PATH,level=logging.DEBUG)

ssl._create_default_https_context = ssl._create_unverified_context
os.environ["PARSE_API_ROOT"] = Config.PARSE_SERVER_URI

from parse_rest.datatypes import Function, Object, GeoPoint, File
from parse_rest.connection import register
from parse_rest.query import QueryResourceDoesNotExist
from parse_rest.connection import ParseBatcher
from parse_rest.core import ResourceRequestBadRequest, ParseError

register(Config.APPLICATION_ID, "", master_key=Config.MASTER_KEY)
reload(sys)
sys.setdefaultencoding('utf-8')

# for saving server progress to backend
class Parsing(Object):
    pass

class Parsing_err(Object):
    pass

# currError = Parsing_err(page_num=0, entity_num=1, err_url="test", status="pending")
# currError.save()
# print "saved"

def move_to_download_folder(downloadPath, newFileName, fileExtension):
    got_file = False   
    ## Grab current file name.
    while got_file == False:
        try: 
            currentFile = glob.glob(downloadPath + "*.xls")
            got_file = True

        except:
            print "File has not finished downloading"
            time.sleep(20)

    ## Create new file name
    fileDestination = "C:\Users\fanta\Documents\Movie_DataMiner\KOBIS_download" + newFileName +"." + fileExtension
    os.rename(currentFile[0], fileDestination)
    return

def FindAndAcceptAlert(browser):
    try:
        alert = None
        while(True): # check till alert is popped up
            alert = isAlertPresent(browser)
            if alert is not None:
                alert.accept()
                return
    except:
        return

def isAlertPresent(browser):
   try:
       
        alert= browser.driver.switch_to_alert()
        return alert
   except NoAlertPresentException: 
        return None

def parseThisPage(soup, browser, page_num):
    browser.execute_script("goPage('" + str(page_num) + "')" )

    table= soup.find("table", {"class":"boardList03"})
    arrMovies= table.tbody.find_all("tr")

    for idx,movie in enumerate(arrMovies):
        click_content= movie.td.a['onclick']
        movieNum= re.sub(r'\D', "", click_content) # sub non-digits by regex

        if movieNum:
            print movieNum
            # dtlExcelDn('movie','box','20080828');
            browser.execute_script("dtlExcelDn('movie','box','" + movieNum + "');" )
            #print result
            
            #wait = WebDriverWait(browser, 10)
            #wait.until(EC.alert_is_present)
            time.sleep(1)
            alert= browser.switch_to_alert()
            alert.accept()

            move_to_download_folder("C:\\Users\\fanta\\Downloads\\", "new_file_test", "xls")
            #FindAndAcceptAlert(browser)
        else:
            print "nothing found!"

url = ("http://kobis.or.kr/kobis/business/mast/mvie/searchMovieList.do")
print url

MOVIES_PER_PAGE= 10

#Chrome driver setting
#options = webdriver.ChromeOptions() 
#options.add_argument("download.default_directory=./KOBIS_download")
#browser = webdriver.Chrome(chrome_options=options)
browser = webdriver.Chrome()

# Firefox : To prevent download dialog
# profile = webdriver.FirefoxProfile()
# profile.set_preference('browser.download.folderList', 2) # custom location
# profile.set_preference('browser.download.manager.showWhenStarting', False)
# profile.set_preference('browser.download.dir', '/KOBIS_download')
# profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'application/vnd.ms-excel')
#browser = webdriver.Firefox()

browser.implicitly_wait(3) # seconds
browser.get(url)

try:
    elem = browser.find_element_by_name('sOpenYearS')
    elem.send_keys('2004-01-01')

    elem = browser.find_element_by_name('sOpenYearE')
    elem.send_keys('2016-12-31')

    browser.execute_script("fn_searchList();")
    time.sleep(1)

    soup = BeautifulSoup(browser.page_source, "lxml")
    countMovies= soup.find("div", { "class":"board_btm" })
    countMovies_filtered= re.sub(r'\D', "", countMovies.em.text)
    print "retrieved movies : "+countMovies_filtered
    TOTAL_PAGES = (int(countMovies_filtered) / MOVIES_PER_PAGE)+1
    print "total pages : "+ str(TOTAL_PAGES)

    for x in range(1, TOTAL_PAGES):
        print "current page : " + str(x)
        parseThisPage(soup, browser, x)
except Exception, e:
    print str(e)
finally:
    browser.quit()