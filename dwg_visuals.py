# dwg_visuals.py
# 02.11.2019 

import pygal 

from dwg_errors_DB import pull_sql_data

def plot_error(rows):
	"""
	Creates bar graph based on the number of individual dwgs an
	error has occurred. I.e. How pervasisve is a particular error? 
	"""
	
	# tuple order:
	# error_code, count, error_msg
	codes, plot_dcnys = [], []
	for row in rows:
		codes.append(row[0])
		# dcny created so error description can be included in tooltip
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
	plot.render_to_file('dwg_errors.svg')
	
def plot_pie(rows):
	"""Plots the pie graph showing the difference between part and prod."""
	
	pie_chart = pygal.Pie()
	pie_chart.title = 'Dist. of Part versus Product'	
	
	# loop through the list of tuples and add() to chart 
	for row in rows:
		pie_chart.add(row[0], row[1]) # This is based on value, not %
	
	pie_chart.render_to_file('errors_by_ext.svg')


def plot_line(rows):
	"""Create a line graph of number of dwgs per date."""
	
	# Create the x and y lists 
	labels, values = [], [] 
	for row in rows:
		labels.append(row[0])
		values.append(row[1])
	
	line_chart = pygal.Line(x_label_rotation = 45)
		
	line_chart.title = 'Number of Error DWGs by date.'
	line_chart.x_labels = labels 
	line_chart.add('Num DWGs', values)
	
	line_chart.render_to_file('errors_by_date.svg')

if __name__ == '__main__':
	
	queries = [
			'''SELECT dwg.error_code, count(*), be.error_msg
			 FROM dwg_details dwg INNER JOIN dwg_errors be
			 ON dwg.error_code = be.error_code
			 GROUP BY dwg.error_code, be.error_msg
			 ORDER BY count(*) DESC
			''',
			'''
			SELECT part_number_ext, count(*)
			FROM parts
			GROUP BY part_number_ext
			ORDER BY count(*) DESC
			''',
			'''SELECT date::date, count(*)
			FROM parts
			GROUP BY date::date 
			ORDER BY date ASC
			''',
		]
	
	# Return list of results from the queries above 
	query_results = pull_sql_data(queries)
	
	# Plot based on the number of unique dwgs the errors  appear on
	plot_error(query_results[0])
	
	# Plot based on part extension 
	plot_pie(query_results[1])
	
	# Plot based on the number of dwgs with error, per day
	plot_line(query_results[2])

	print('Plotting complete...')
