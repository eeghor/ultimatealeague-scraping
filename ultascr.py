import selenium
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from selenium.webdriver.common.action_chains import ActionChains
import time
import re


LONGEST_WAIT_SEC = 20

start_page_url = "http://www.ultimatealeague.com/fixtures.php?show=season"
#driver = webdriver.Chrome('/Users/ik/Codes/soccerway-scraping/chromedriver')
driver = webdriver.PhantomJS()
#driver = webdriver.Firefox('/Users/ik/Codes/soccerway-scraping/')
driver.get(start_page_url)
#driver.implicitly_wait(20)
# wait up to 10 seconds before throwing a TimeoutException (if there's still no "Previous" link)

WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "2005-06"))).click()

for tr in driver.find_elements_by_class_name("even"):
	print(tr.text)
