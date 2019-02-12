# birth_visuals.py
# 02.06.2019

import psycopg2 
import pygal 

def pull_data_one():
	"""
	Pulls and returns the SQL query for the error codes, associated 
	error descriptions (error_msg), and the count of the errors (i.e. 
	the number of parts/ dwgs the error appears in/on.
	"""
	
	# Create connection
	conn = psycopg2.connect(database = 'test', user = 'postgres', 
							password = 'Strider142')
	# set cursor 
	cur = conn.cursor()
	# Create query
	sql = '''SELECT dwg.error_code, count(*), be.error_msg
			 FROM dwg_details dwg INNER JOIN birth_errors be
			 ON dwg.error_code = be.error_code
			 GROUP BY dwg.error_code, be.error_msg
			 ORDER BY count(*) DESC
		'''
	
	# exucute query
	cur.execute(sql)
	
	# get full list and return 
	rows = cur.fetchall()
	# close it 
	cur.close()
	conn.close()
	### TEST ### 
	print(len(rows))
	return rows

def error_plot(rows):
	# Should the tuple get cleaned up inside this function? 
	# Maybe create a sub function to do this (i.e. refactor when needed)
	
	# tuple order:
	# error_code, count, error_msg
	
	codes, plot_dcnys = [], []
	for row in rows:
		codes.append(row[0])
		plot_dcny = {'value': row[1],
					 'label': row[2],
					 }
		plot_dcnys.append(plot_dcny)
		
	# Data prepared, create plot.
	plot = pygal.Bar(x_label_rotation = 45)
	
	plot.title = 'Errors by part occurrence'
	plot.x_labels = codes
	plot.x_title = 'Error Codes'
	plot.y_title = 'Amounts'
	
	# Plot it 
	plot.add('Errors', plot_dcnys)
	plot.render_to_file('birth_errors.svg')

def get_pie_data():
	"""Simple query to get the data basing on extensions."""
	
	# Create conenction
	conn = psycopg2.connect(database = 'test', user = 'postgres', 
							password = 'Strider142')
	# set cursor 
	cur = conn.cursor()
	# Set query 
	sql = '''
		SELECT part_number_ext, count(*)
		FROM parts
		GROUP BY part_number_ext
		ORDER BY count(*) DESC
		'''
	
	cur.execute(sql)
	rows = cur.fetchall() # Should be two rows
	
	# close it 
	cur.close()
	conn.close()
	
	return rows 
	
def plot_pie(rows):
	"""Plots the pie grpah showing the difference between part and prod
	"""
	
	pie_chart = pygal.Pie()
	pie_chart.title = 'Dist. of Part versus Product'	
	
	# loop through the list of tuples and add() to chart 
	for row in rows:
		pie_chart.add(row[0], row[1]) # This is based on value, not %
	
	pie_chart.render_to_file('errors_ext.svg')

def pull_dwg_dates():
	""" Pull dates and the count to get the number of dwgs per day."""
	
	conn = psycopg2.connect(database = 'test', user = 'postgres', 
							password = 'Strider142')
	cur = conn.cursor()
	sql = '''SELECT date::date, count(*)
		FROM parts
		GROUP BY date::date 
		ORDER BY date ASC
		'''
	cur.execute(sql)
	rows = cur.fetchall()
	
	# close it 
	cur.close()
	conn.close()
	
	return rows 

def plot_line(rows):
	"""Create a line graph of number of dwgs per date."""
	
	# Create the x and y lists 
	labels, values = [], [] 
	for row in rows:
		labels.append(row[0])
		values.append(row[1])
	
	line_chart = pygal.Line(x_label_rotation = 45)
		
	line_chart.title = 'Number of dwgs with Error per date.'
	line_chart.x_labels = labels 
	line_chart.add('Num DWGs', values)
	
	line_chart.render_to_file('birth_dates.svg')


if __name__ == '__main__':
	
	# First 
	rows = pull_data_one()
	# Plot it 
	error_plot(rows)

	# Second
	rows = get_pie_data()
	plot_pie(rows)
	
	# Third 
	rows = pull_dwg_dates()
	plot_line(rows)

	
