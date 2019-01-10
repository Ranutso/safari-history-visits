#!/usr/bin/env python3
##
## First draft on the project to query Safari's history
##

import sqlite3
import argparse
from pathlib import Path
from datetime import datetime

## Some Global definitions
DEFAULT_LIMIT = 10
DISPLAY_LINE = "Showing the last {visit_number} visits to this site"
TIME_STRING = "%A, %B %d %Y %H:%M:%S"
TIME_STRING_TABBED = "%A\t%B\t%d\t%Y\t%H:%M:%S"

## Helpful functions

def dateString(dateobj, tabbed=False):
	### Converts dateobj into a human readable string.

	# Adding 978307200 to the visit number is required in order to correctly display the date.
	if tabbed:
		return datetime.fromtimestamp(dateobj+978307200).strftime(TIME_STRING_TABBED)
	else:
		return datetime.fromtimestamp(dateobj+978307200).strftime(TIME_STRING)

## Parsing our command options.
## Usage: command [optional] url

parser = argparse.ArgumentParser()
parser.add_argument("url", help="the URL of the web page you want to query")
parser.add_argument("--max", "-m", help="maximum number of visits to show (default: {}, 0 shows all entries)".format(DEFAULT_LIMIT), type=int)
args = parser.parse_args()

## Before we connect to the database. Let's do some user checking.

# Check and process the maximum number of entries to show.

if type(args.max) is int:
	# First and foremost, we need to check if the variable is a valid int, since python won't allows us to use comparisons without it.

	if args.max < 0:
		# If max specified by the user is 0 or a negative number, let's display an error.
		print("The maximum number of entries to display must be a positive number.")
		exit(1)

	elif args.max == 0:
		# Show all entries
		limit = '' # This variable stores the SQL query for limiting the number of entries.
		display_line = DISPLAY_LINE + ":"

	else:
		# Show the specified number of entries
		limit = "LIMIT {}".format(args.max)
		display_line = DISPLAY_LINE + ":"

else:
	# Show the default number of entries
	limit = "LIMIT {}".format(DEFAULT_LIMIT)
	display_line = DISPLAY_LINE + ":\n(If you want to see more visits use the --max parameter)"

## Connecting to the database

home = str(Path.home())
safari = sqlite3.connect("{}/Library/Safari/History.db".format(home))
c = safari.cursor()

## The basic query

# First we'll query for the URL's ID on Safari's database.
query_url = (args.url,) # Not checking for valid URLs. sqlite3 method below should help with SQL injection attacks.
c.execute('SELECT id, visit_count from history_items WHERE url=?', query_url)
result = c.fetchone()
if result:
	(id,visit_count) = result
else:
	print("You have never visited that web page.")
	exit()

## If there was any visits to that web page, let's retrieve the dates.

# First, let's get the date for the first visit ever.
c.execute('SELECT visit_time from history_visits where history_item=? ORDER BY visit_time asc LIMIT 1', (id,))
(first_visit,) = c.fetchone()

if visit_count == 1:
	print("You have visited that web page once at {}.".format(dateString(first_visit)))
	exit()

else:
	print("You have visited that web page {} times.".format(visit_count))
	print("Your first visit was on {}.".format(dateString(first_visit)))
	print()

# Now we'll query for the visits.

query_visit = (id,)
visits_query_result = c.execute('SELECT visit_time, title from history_visits WHERE history_item=? ORDER BY visit_time desc ' + limit, query_visit)
visits = visits_query_result.fetchall() # Damn you SQLite!!!!!!!!!
print(display_line.format(visit_number=len(visits)))
for visit in visits:
	print("{}\t|\t{}".format(dateString(visit[0], tabbed=True), visit[1]))

safari.close()