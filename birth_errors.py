# birth_errors.py
# 01.14.2019

import os
import csv
from collections import Counter # Still needed? it is used in prod code

from bs4 import BeautifulSoup

import psycopg2




def find_error_htmls(root):
	"""
	Finds all html files in the root dir.
	Returns list of full paths.
	"""
	
	error_htmls = []
	for dirpath, dirnames, dirfiles in os.walk(root):
		for dirfile in dirfiles:
			if os.path.splitext(dirfile)[-1] == '.html':
				error_htmls.append(os.path.join(dirpath, dirfile))

	return error_htmls

def init_scrape(filename):
	"""     TEST. TEST TEST
	Just using for test. To pull out the error code test."""
	# Open the file, create the soup, parse out the data. 
	with open(filename, 'r') as htmlfile:
		contents = htmlfile.read()
		# Q?: Can a regex be used here instead? 
	# Make soup
	soup = BeautifulSoup(contents, 'html.parser')
	# Pull out all td's w/ att and print
	tds = soup.find_all('td', width = "550")
	# show it 
	
	# init counter
	counter = 0
	for td in tds[1:]:
		# print(i.text)
		len_text = len(td.text)
		if len_text > counter:
			counter = len_text
	# print()
	return counter 

def build_error_table(filename):
	"""
		NO LONGER IN USE... Used to build the initial DB table.
	Collects and returns unique error codes and messages from html.
	"""
	
	with open(filename, 'r') as htmlfile:
		contents = htmlfile.read()
	soup  = BeautifulSoup(contents, 'html.parser')
	# The second table in html houses the error information.
	table = soup.find_all('table')[1]
	# Find trs that are not headers
	trs = table.find_all('tr', bgcolor = "#ffffff")
	# init dcny and loop for data 
	codes = {}
	for tr in trs:
		# Pull just the a.text
		error_code = tr.a.text # Works. Could have searched on td
		error_msg = tr.find('td', width = "550").text
		if error_code not in codes:
			codes[error_code] = error_msg

	return codes
	
def write_errors_csv(full_codes):
	"""
		NO LONGER IN USE... Used to build the initial DB table.
	Writes out (CWD) error codes dcny to a csv for SQL import.
	"""
	# Passing in dcny, so simple reader is enough
	with open('birth_codes.csv', 'w', newline = '') as csvfile:
		csvwriter = csv.writer(csvfile, delimiter = ',', 
			quotechar = '"')
		# Write header
		csvwriter.writerow(['Error Code', 'Error Message'])
		# Loop to write rows 
		for key, value in full_codes.items():
			csvwriter.writerow([key, value])
	
def scrape_ind_html(filename, full_errors, full_parts):
	"""
	Full scrape of the file of:
	part number, part extension, date, and list of error codes.
	Compares against the current part number table and ignores if a match.
	Compares against current error code table and returns new codes for table 
	update.
	"""
	
	# open file, create soup
	with open(filename, 'r') as htmlfile:
		contents = htmlfile.read()
	# Make soup 
	soup  = BeautifulSoup(contents, 'html.parser')
	
	# Additional error types are saved as html files in dwg dirs.
	# The conditional below checks and ignores these
	if (
		'Check & Save' in soup.h3.text or
		'3DADSS' in soup.h3.text):
		return None, ''
		
	# Get the filename td
	tables = soup.find_all('table')
	
	# Find data from first table 
	# 3 rows in first table 
	trs = tables[0].find_all('tr')	
	# Get part number.
	part_full = trs[0].find('td', width="750").text
	part_num, part_ext = os.path.splitext(part_full)
	# Check if part_num in the full_part list
	if part_num in full_parts:
		print('{} already in DB.'.format(part_num))
		return None, ''
	
	# date. 
	# Does this need updated from string? DB should handle...
	date = trs[2].find('td', width="750").text
		
	# Second table 
	trs = tables[1].find_all('tr', bgcolor = "#ffffff")
	# init ind error list
	error_list = []
	# iterate through, check if code exists. 
	err_update = {}
	for tr in trs:
		# Pull a.text for error code 
		error_code = tr.a.text
		if error_code not in full_errors:
			# function for importing into DB list. 
			print('Found code in {}.'.format(filename))
			# Need to return the error code and its msg.
			# CREATE  as tuple, for the DB input. 
			# Although this can return multiple codes per html
			err_update[error_code] = tr.find('td', width = "550").text
		# continue by adding the error code to the list. 
		error_list.append(error_code)
		
	# populate dcny, then return 
	dcny = {'part_num' : part_num,
			'part_ext' : part_ext,
			'date': date,
			'errors': error_list
		}
		
	return dcny, err_update

def pull_error_codes():
	"""
	Pulls codes from the birth_errors postgresql table.
	returns list of these codes. 
	"""
	# Make connection
	conn = psycopg2.connect(database = 'test', 
							user = 'postgres', 
							password = 'Strider142'
						)
	# Create cursor object 
	cur = conn.cursor()
	# Make query 
	cur.execute('SELECT error_code FROM birth_errors')
	# return the rows of query
	rows = cur.fetchall()
	# create list to return. fetchall() creates a tuple.
	full_errors = list(row[0] for row in rows)
	# Shut it down
	cur.close()
	conn.close()
	
	return full_errors
	
def update_error_codes(dcny): 	
	"""
	Write updated dcny to DB.
	Takes dcny of new error codes and updates appropriate table in DB.
	"""
	# connect to, write out dcny 
	conn = psycopg2.connect(database = 'test', 
							user = 'postgres',
							password = 'Strider142',
						)
	cur = conn.cursor()
	# Create statement. Note no semi-colon
	sql = '''INSERT INTO birth_errors 
			 VALUES 
				(%s, %s)
		  '''
	# Convert dcny to list of tuples for execute many stmt below.
	error_list = list((key, value) for key, value in dcny.items())
	cur.executemany(sql, error_list)
	# Commit and close out. 
	conn.commit()
	cur.close()
	conn.close()

def pull_parts():
	"""
	Grabs all parts from the DB. Used to compare new entries from dir.
	"""
	
	conn = psycopg2.connect(database = 'test', 
							user = 'postgres',
							password = 'Strider142',
						)
	cur = conn.cursor()
	# Get the part numbers. 
	cur.execute('SELECT part_number FROM parts')
	# Returns list of tuples from query 
	rows = cur.fetchall()
	# create a list to return 
	parts = list(row[0] for row in rows)
	
	return parts 

def final_db_write(data, table):
	""" 
	Writes the list of tuples into the table specified by arg
	"""
	
	# Connect to DB 
	conn = psycopg2.connect(database = 'test', user = 'postgres', 
		password = 'Strider142')
	cur = conn.cursor()
	# Create query 
	sql = 'INSERT INTO %s' % table
	sql += '''\nVALUES
		(%s, %s, %s)
		'''
	# Execute stmt and commit
	cur.executemany(sql, data)
	conn.commit()
	# Close out 
	cur.close()
	conn.close()
	
		
def update_DB(full_list):
	"""
	Takes the full list from html scrapes and breaks up into two lists.
	These are then imported into the parts and dwg_details tables in DB.
	"""
	
	# first_table == 'parts' 
	# Update 01302019: list comprehension looks ugly here- clean up.
	first_table = list((row['part_num'],
						row['part_ext'],
						row['date']) for row in full_list
					)
					
	# second_table == dwg_details table			
	second_table = []
	for row in full_list:
		counted = Counter(row['errors'])
		for key, value in counted.items():
			second_table.append((row['part_num'], key, value))
		
	# Pass both lists (of tuples) to functions to write to DB. 
	final_db_write(first_table, 'parts')
	final_db_write(second_table, 'dwg_details')
	
	
	
if __name__ == '__main__':
	
	root = 'S:\\!RPA!\\BIRTH'
	# Get current error_list from DB 
	full_errors = pull_error_codes()
	# Get current parts list
	full_parts = pull_parts()
	
	# Find all error htmls in root.
	error_htmls = find_error_htmls(root)
	# Show length 
	print(len(error_htmls))
	
	full_list = []	
	for html in error_htmls:
		print(html)
		dcny, err_update = scrape_ind_html(html, full_errors, 
			full_parts)
		# append the ind scrape dcny to list 
		# Check saves and 3DDSS are returned as None, so can be ignored
		if dcny != None:
			full_list.append(dcny)
		# Update full_errors if necessary 
		if err_update:
			# Will run code to update and return the full list. 
			print('Updating DB error list...')
			update_error_codes(err_update)
			# Need to pull the list after updates. 
			full_errors = pull_error_codes()		
			
	print()	
	### TEST ### 
	for line in full_list:
		for key, value in line.items():
			print(key , value)
		print()
	###      ###
	
	# Write out the data
	update_DB(full_list)
	
	print('\n-----Process complete!-----')
	


