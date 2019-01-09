#!/usr/bin/env python3
##
## First draft on the project to query Safari's history
##

import sqlite3
import argparse
from pathlib import Path
from datetime import datetime

## Parsing our command options.
## Usage: command [optional] url

parser = argparse.ArgumentParser()
parser.add_argument("url", help="the URL of the web page you want to query")
parser.add_argument("--max", "-m", help="maximum number of visits to show (default: 10)", type=int, default=10)
args = parser.parse_args()

## Connecting to the database

home = str(Path.home())
safari = sqlite3.connect("{}/Library/Safari/History.db".format(home))
c = safari.cursor()

## The basic query

# First we'll query for the URL's ID on Safari's database.
query_url = (args.url,)
c.execute('SELECT id from history_items WHERE url=?', query_url)
(id,) = c.fetchone()

# Now we'll query for the visits.
limit = args.max
query_visit = (id, limit)
for visit in c.execute('SELECT visit_time from history_visits WHERE history_item=? ORDER BY visit_time desc LIMIT ?', query_visit):
	# Adding 978307200 to the visit number is required in order to correctly display the date.
	visit_time = datetime.fromtimestamp(visit[0]+978307200).strftime("%A, %B %d %Y | %H:%M:%S")
	print("{}".format(visit_time, visit[0]))