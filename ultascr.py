import selenium
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import re
import pandas as pd

# choose the range of years you are interested in; the earliest available year is 1897
y_from = 2005
y_to = 2008

"""
choose what format to save data in:
	0 : don't save at all, just show first 10 rdata ows on screen
	1 : save as a table in .CSV 
	2 : save as a JSON file
"""
save_flag = 1

# want to see yearly counts for the retrieved records? 1 for yes

show_yrecs = 1

# sanity check

assert y_from > 2004, ("sorry, there\'s no data for earliest year {} that you\'ve picked." 
						"you may want to choose another year from 2005 and on..".format(y_from))
assert y_to < 2017, ("sorry, there\'s no data for last year {} that you\'ve picked." 
						"you may want to choose another year before 2017..".format(y_to))
assert y_from <= y_to, ("no, this won\'t work. make sure that the earliest year you pick is before or equal to the last year...")

# show this 
print("""-------> scraping ultimatealeague.com""")

list_rounds = []
list_team_1 = []
list_team_2 = []
list_score_1 = []
list_pen1 = []
list_score_2 = []
list_pen2 = []
list_dates = []
list_att = []
list_venues = []

LONGEST_WAIT_SEC = 20

start_page_url = "http://www.ultimatealeague.com/fixtures.php?show=season"
#driver = webdriver.Chrome('/Users/ik/Codes/soccerway-scraping/chromedriver')
driver = webdriver.PhantomJS()
#driver = webdriver.Firefox('/Users/ik/Codes/soccerway-scraping/')
driver.get(start_page_url)
#driver.implicitly_wait(20)
# wait up to 10 seconds before throwing a TimeoutException (if there's still no "Previous" link)

NEED_CLICK_FLAG = True

# note: the tabs on the web site start from "2005-06"
tab_full_yrs = [y for y in range(2005,2017)]

if y_from in tab_full_yrs:
	tab_click_first = str(y_from) + "-" + str(y_from + 1)[-2:]
else:
	tab_click_first = str(y_from-1) + "-" + str(y_from)[-2:]

tab_click = tab_click_first

while NEED_CLICK_FLAG:

	print("scraping results for", tab_click, "...", end="")

	WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, tab_click))).click()
	
	# get the table headers that are in <tr> that belongs to the class "datatrheader"
	hdrs = driver.find_element_by_class_name("datatrheader").text.split()
	
	# table
	tbl = driver.find_element_by_id("tablesort")
	# print(tbl)
	# got to the table first
	rows = tbl.find_elements_by_xpath('//tbody/tr[@class]')
	
	for r in rows:
		# go by celld, i.e. <td>s
		cs = r.find_elements_by_xpath('td[@class]')
	
		for i, c in enumerate(cs):
			if i == 1:
				list_rounds.append(c.text.strip())
			elif i ==2:
				list_dates.append(c.text.strip())
			elif i ==3:
				list_venues.append(c.text.strip())
			elif i == 4:
				list_att.append(c.text.strip())
			elif i == 5:
				team1, team2 = c.find_elements_by_xpath('a[@href]')
				list_team_1.append(team1.text.strip())
				list_team_2.append(team2.text.strip())
			elif i == 6:
	
				score_txt = c.text.split()
				#print("score:",score_txt)
				if len(score_txt) == 2:  # no penalties, just full time score
					score_1, score_2 = score_txt
					pen1 = pen2 = None
					list_pen1.append(pen1)
					list_pen2.append(pen2)
				elif len(score_txt) == 4:  # penalties, i.e. 1 (4) 1 (5)
					score_1, score_2 = score_txt[::2]
					pen1, pen2 = score_txt[1::2]
					list_pen1.append(pen1[1:-1])
					list_pen2.append(pen2[1:-1])
	
				list_score_1.append(score_1.strip())
				list_score_2.append(score_2.strip())
	
	# finished scraping this page; now the question is if we need to scrape another one
	print("ok")

	clicked_years_short = tab_click.split("-")
	clicked_years = [int(clicked_years_short[0]), int("20" + clicked_years_short[1])]

	if y_to not in clicked_years:
		tab_click = str(clicked_years[1]) + "-" + str(clicked_years[1]+1)[-2:]
		NEED_CLICK_FLAG = True
	else:
		NEED_CLICK_FLAG = False


data = zip(list_rounds, list_dates, list_team_1, list_score_1, list_pen1, 
				 list_team_2, list_score_2, list_pen2, list_venues, list_att)
df = pd.DataFrame(columns="round date team1 t1score t1pen team2 t2score t2pen venue attendance".split())

for i, row in enumerate(data):
	df.loc[i] = row

if y_from != y_to:
	csv_fl = "scraped_data_from_ultimatealeague_yrs_" + str(y_from) + "_to_" + str(y_to) + ".csv"
else:
	csv_fl = "scraped_data_from_ultimatealeague_" + str(y_from) + ".csv"

df.to_csv(csv_fl, index=False)

print("successfully retrieved {} results..".format(len(df.index)))
print(df.head(10))
