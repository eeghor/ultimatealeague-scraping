import requests
import re
from bs4 import BeautifulSoup
from collections import defaultdict
import json
import time

# url to start scraping from
start_url = "http://www.ultimatealeague.com/fixtures.php"

r = requests.get(start_url).text  # response body as bytes so need get text first
soup = BeautifulSoup(r, "lxml")

data = defaultdict(lambda: defaultdict(list))

# first see what seasons are available
season_urls = defaultdict()

for season_td in soup.find("table", class_="fixturetable").find("tr").find_all("td"):
	season_urls[season_td.text.strip()] = {"season_url": start_url + "?" + season_td.a["href"].split("?")[1]}

sorted_season_list = sorted(list(season_urls.keys()))
min_season = min(sorted_season_list)
max_season = max(sorted_season_list)

print("fixtures available for {} seasons in total, from {} to {}".format(len(season_urls),
	min_season, max_season))

# for s in season_urls:
# 	print(season_urls[s])

# start goign through the seasons
for season in sorted_season_list:
	r = requests.get(season_urls[season]["season_url"]).text
	soup = BeautifulSoup(r, "lxml")
	# look at the 2nd fixture table (there are two in total)
	for round_td in soup.find_all("table", class_="fixturetable")[1].find("tr").find_all("td"):
		season_urls[season].update({round_td.text.strip(): season_urls[season]["season_url"] + "&" + round_td.a["href"].split("&")[1]})

# now go through all seasons and all rounds
for season in sorted_season_list:
	print("scraping season {}...".format(season), end="")
	for rnd in  season_urls[season]:

		if rnd != "season_url":
			r = requests.get(season_urls[season][rnd]).text
			soup = BeautifulSoup(r, "lxml")

			match_list = []

			for mtch in soup.find_all("div", class_="fixture-container"):

				teams_box = mtch.find("div", id="fixture-details-teams")

				try:
					attend = mtch.find("span", id="fixture-details-att").text.lower().strip()
				except:
					attend = None
				try:
					refree = mtch.find("span", id="fixture-details-ref").text.lower().strip()
				except:
					refree = None

				match_list.append(
				{
				"home": teams_box.find("div", id="fixture-details-home").text.lower().strip(),
				"away": teams_box.find("div", id="fixture-details-away").text.lower().strip(),
				"date": mtch.find("span", id="fixture-details-date").text.lower().strip(),
				"venue": mtch.find("span", id="fixture-details-stad").text.lower().strip(),
				"attendance": attend,
				"referee": refree
				}
				)
			# finished picking matches; now put that match list into the data dict
			data[season][rnd.lower()] = match_list
	print("ok")

json.dump(data, open("aleague_{}_{}_matches.json".format(min_season, max_season), "w"), sort_keys=False, indent=4)


