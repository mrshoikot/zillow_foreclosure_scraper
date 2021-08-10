import urllib3
import json
import sqlite3
import os
from bs4 import BeautifulSoup
import csv
import re
import os.path
from urllib.parse import urlencode
import requests
import time
import csv
import chromedriver_binary
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import sqlite3
import os.path
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from requestium import Session, Keys

options = Options()
# options.add_argument('--headless')
# options.add_argument('--disable-gpu')
# prefs = {"profile.managed_default_content_settings.images": 2}
# options.add_experimental_option("prefs", prefs)
s = Session(webdriver_path='./chromedriver',
            browser='chrome',
            default_timeout=15,
            webdriver_options={'arguments': []})


session = requests.Session()

match = False
switch = False

county = input("Enter county: ")+" County"

def isLastPage(html):
    soup = BeautifulSoup(html, 'html.parser')
    nextBtn = soup.find('a', attrs={"title": "Next page"})
    
    if nextBtn is None:
        return True

    return str(nextBtn).find('disabled') != -1

def visit(page, switch, zip):
    if page==1 and not switch:
        url = 'https://www.zillow.com/homes/for_sale/fore_lt/'+zip+'_rb/pmf,pf_pt/'
        print(url)
        s.driver.get(url)

        try:
            notfound = s.driver.find_element_by_xpath('//*[@id="grid-search-results"]/div[2]/div')
            if notfound and notfound.text.find("find this area") != -1:
                return 'break'
        except:
            pass


        if s.driver.find_element_by_xpath('//*[@id="grid-search-results"]/div[1]/div/div[1]/div/button[1]/div').text == '0':
            switch = True

    else:
        try:
            s.driver.find_element_by_css_selector('#grid-search-results > div.search-pagination > nav > ul a[rel="next"]').click()
        except:
            return 'break'
        time.sleep(2)
        s.driver.refresh()

    
    while True:
        
        try:
            if s.driver.find_element_by_class_name('zsg-content_collapsed').text == 'No matching results':
                return 'break'
        except:
            pass
        
        try:
            h = s.driver.page_source
        except:
            return [ids, s.driver.page_source]

        key = '"zpid":"'


        arrs = [m.start() for m in re.finditer(key, h)]
        ids = []

        for arr in arrs:
            lastIndex = h[arr+len(key):arr+len(key)+100].find('"')
            ids.append(h[arr+len(key):arr+len(key)+lastIndex])
        
        if ids:
            return [ids, h]


page = 1

for row in csv.reader(open('zip.csv')):
    switch = False

    zip = row[0]

    print(zip)

    while True:

        print('city: '+county)
        print("Page: "+str(page))

        idss = []
        html = ''

        
        d = visit(page, switch, zip)

        if d == 'break':
            break

        idss = d[0]
        html = d[1]

        print(idss)


        for id in idss:
            if not os.path.isfile(county+'/'+id+'.json'):
                params = {
                    "zpid": id,
                    "contactFormRenderParameter": '',
                    "queryId": 'ad0ce4836b6d639412ddf8b179725546',
                    "operationName": 'ForSaleDoubleScrollFullRenderQuery'
                }

                data = {
                    "clientVersion": "home-details/6.0.11.0.0.hotfix-01-28-21.fe0539e",
                    "operationName": "ForSaleDoubleScrollFullRenderQuery",
                    "queryId": "ad0ce4836b6d639412ddf8b179725546",
                    "variables": {
                        "contactFormRenderParameter": {"zpid": id, "platform": "desktop", "isDoubleScroll": True},
                        "zpid": id
                    }
                }


                url = 'https://www.zillow.com/graphql/?'+urlencode(params)

                s.transfer_driver_cookies_to_session()
                response = s.post(url,json=data)


                text = response.text
                
                try:
                    data = json.loads(text)
                except:
                    visit(page, switch, zip)
                    continue

                if county not in data['data']['property']['county']:
                    print(str(id)+" suspecious! - " + data['data']['property']['county'])
                    continue

                # print(data['data']['property']['foreclosureTypes']['isPreforeclosure'])
                # if not (data['data']['property']['listing_sub_type']['is_FSBO'] or data['data']['property']['foreclosureTypes']['isPreforeclosure']):
                #     continue

                if not os.path.exists(county):
                    os.makedirs(county)

                with open(county+'/'+id+'.json', 'w') as outfile:
                    json.dump(data, outfile)
                    print(str(id)+" saved!")
            else:
                print(str(id)+" already exist!")
                pass
        page += 1

        print("Last Page: " + str(isLastPage(html)))
        print("Switch: " + str(switch))
        if(isLastPage(html)) and switch:
            page = 1
            break
        elif isLastPage(html):
            switch = True

            s.driver.find_element_by_xpath('//*[@id="grid-search-results"]/div[1]/div/div[1]/div/button[2]').click()
            time.sleep(5)
            s.driver.refresh()
            page=1
