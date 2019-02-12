# dwg_error_main.py
# 01.14.2019

import os

from bs4 import BeautifulSoup

from dwg_errors_DB import (pull_parts, pull_error_codes, update_error_codes, 
						   update_DB)

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
	
def scrape_ind_html(filename, error_codes, parts_list):
	"""
	Full scrape of the file for:
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
	if part_num in parts_list:
		print('{} already in DB.'.format(part_num))
		return None, ''
	
	# date. 
	# DB will convert to datetime...
	date = trs[2].find('td', width="750").text
		
	# Second table contains errors and error messages
	trs = tables[1].find_all('tr', bgcolor = "#ffffff")
	# init ind error list. This will be passed with the full part details
	error_list = []
	# Collect codes and check for new ones. 
	error_update = {}
	for tr in trs:
		# Pull a.text for error code 
		error_code = tr.a.text
		if error_code not in error_codes:
			print('Found code in {}.'.format(filename))
			# Capture msg as well
			error_update[error_code] = tr.find('td', width = "550").text

		error_list.append(error_code)
		
	# populate dcny, then return 
	part_data = {'part_num' : part_num,
			'part_ext' : part_ext,
			'date': date,
			'errors': error_list
		}
		
	return part_data, error_update
	
	
if __name__ == '__main__':
	
	# path to be entered by user...
	root = 'C:\\enter_path_as_string'
	
	# Get current error codes and parts from DB 
	error_codes = pull_error_codes()
	parts_list = pull_parts()
	
	# Find all error htmls in root.
	error_htmls = find_error_htmls(root)
	# Since dir is periodically expunged, show that data was found...
	print(len(error_htmls))
	
	# init list for ind part dcny's
	full_list= []	
	for html in error_htmls:
		print(html) 
		part_data, error_updates = scrape_ind_html(html, error_codes, 
			parts_list)
		# Append the ind scrape dcny to list. 
		if part_data != None:
			full_list.append(part_data)
		# Update full_errors if necessary
		# Re-returns list from DB after update.
		if error_updates:
			print('Updating DB error list...')
			update_error_codes(error_updates)
			error_codes = pull_error_codes()		
	
	###	
	# Can be commented, but prints the new dwgs captured. 
	# Useful for comparing against known dwg executions for the day. 
	print()	
	for line in full_list:
		for key, value in line.items():
			print(key , value)
		print()
	###
	
	# Write out the data
	update_DB(full_list)
	
	print('\n-----Process complete!-----')
	
	
