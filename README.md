# DWG_errors 
---
## Description
Simply put, the code here captures data from HTML files (saved locally) and stores them in a database (versus using flat files). A second module (dwg_visuals.py) was created to begin looking at data visualizations and how I might want to present data to others. 

I automate Catia drawing creation ('drafting') through the use of RPA software at my current job (R&D for a global vehicle manufacturer). If any errors occur in the drafting process, an HTML file is created (shown in "dummy_html.html") by the application and my script then saves it locally.  A directory has been specifically built to hold all files related to an individual dwg. 

The main script in this project (dwg_errors_main.py) searches the directory for html files, scrapes each of these files for relevant data, and updates the database with newly found data. Any dwg/ part numbers that have already been uploaded to the DB will be ignored, and any new error codes will be captured and updated on the fly. It would be desirable to remove files from the dir once scraped, but unfortunately others in my department make use of these as well. 

The dwg_visuals.py file was built to visualize some of the more interesting SQL queries. 

## Goals
This project was conceived with two goals in mind:
1. To begin applying concepts learning in Web Scraping, PostgreSQL/ DBA, and Data Science
2. To improve the analytics and foster a data-driven mindset within my current place of work. This can be done by collecting data and showing issues that occur over time.

As this is still in the beginning stages there's a lot to be desired. Ultimately, the data retrieved should be compared against the entire job queue to get an understanding of how good (or poor) data quality actually is. Additionally, the next phase (or another side project) would involve creating a web based dashboard where visualizations and simple queries could be easily accessible to mgmt or the average user. 

##  Licensing 
I have done my best to adhere to my company's non-disclosure and confidentiality standards. With this in mind, I have masked dwg codes and any proprietary information. The codes left in the html file should be generic to Dessault and Catia, so I assume these to be public knowledge. 

## TODO
* The sql code does not contain constraints or indexing at the moment. 
* Code for the svg files could include some more customization- I think the point does get across, at least. 
* Refactor, refactor, refactor
* The visualisation and main scripts will probably end up being run concurrently. With that in mind, a few things can be altered (sys.argv, etc) for scheduled execution (especially if visualisations will be used in a dashboard and expected to be real-time)
