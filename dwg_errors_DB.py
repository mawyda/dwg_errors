# dwg_errors_DB.py
# 02.12.2019

from collections import Counter
import psycopg2


# NOTE: 
# Password to be entered by user...

def pull_parts(password = 'Strider142'):
	"""
	Returns list of parts from DB. 
	"""
	conn = psycopg2.connect(database = 'dwg_project', 
							user = 'postgres',
							password = password,
						)
	cur = conn.cursor()
	# Get the part numbers. 
	cur.execute('SELECT part_number FROM parts')
	# Returns list of tuples from query 
	rows = cur.fetchall()
	# create a list to return 
	parts = list(row[0] for row in rows)
	
	return parts 

def pull_error_codes(password = 'Strider142'):
	"""
	Returns list of dwg error codes from DB.
	"""
	conn = psycopg2.connect(database = 'dwg_project', 
							user = 'postgres', 
							password = password,
						)
	# Create cursor object 
	cur = conn.cursor()
	# Make query 
	cur.execute('SELECT error_code FROM dwg_errors')
	# return the rows of query
	rows = cur.fetchall()
	# create list to return. fetchall() creates a tuple.
	full_errors = list(row[0] for row in rows)
	# Shut it down
	cur.close()
	conn.close()
	
	return full_errors

def update_error_codes(dcny, password = 'Strider142'): 	
	"""
	Write updated dcny to DB.
	Takes dcny of new error codes and updates appropriate table in DB.
	"""
	conn = psycopg2.connect(database = 'dwg_project', 
							user = 'postgres',
							password = password,
						)
	cur = conn.cursor()
	# Create statement. Note no semi-colon
	sql = '''INSERT INTO dwg_errors 
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

def final_db_write(data, table, password = 'Strider142'):
	""" 
	Writes the list of tuples into the table specified by arg
	"""	
	conn = psycopg2.connect(database = 'dwg_project', 
							user = 'postgres', 
							password = password,
						)
	cur = conn.cursor()
	# Create query. Works for both parts and dwg_details tables
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
	first_table = list((row['part_num'],
						row['part_ext'],
						row['date']) for row in full_list
					)	
					
	# second_table == dwg_details table
	# The block below creates a list of tuples that contain each individual
	# error and the number of times that error appears in the dwg			
	second_table = []
	for row in full_list:
		counted = Counter(row['errors'])
		for key, value in counted.items():
			second_table.append((row['part_num'], key, value))
		
	# Pass both lists (of tuples) to functions to write to DB. 
	final_db_write(first_table, 'parts')
	final_db_write(second_table, 'dwg_details')
	
def pull_sql_data(queries, password = 'Strider142'):
	"""
	Fetches data based on queries in passed arg.
	"""
	# Create the connection
	conn = psycopg2.connect(database = 'dwg_project', 
							user = 'postgres', 
							password = password,
						)
	cur = conn.cursor()
	# init the list to return 
	query_results = []
	# Loop through each 
	for query in queries:
		cur.execute(query)
		rows = cur.fetchall()
		query_results.append(rows)
	
	cur.close()
	conn.close()
	
	return query_results
	

