# Zillow Foreclosure Scraper
Scrape foreclosure properties from Zillow


## Install the requirements 
`pip install -r requirements.txt`

## Scrape properties
`python main.py`
It'll scrape the properties and save them in JSOM format. You'll be promted to enter the name of the county you want to scrape.

## Convert JSON to CSV
`python csv_json.py`
It'll convert the scraped JSON files into a single CSV file.  You'll be promted to enter the name of the county you want to convert.
