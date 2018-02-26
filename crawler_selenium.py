from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from pymongo import MongoClient
import uuid

def visit(get_link):
	#options = Options()
	#options.add_argument("--headless")
	#browser = webdriver.Firefox(firefox_options=options)
	browser = webdriver.Firefox()
	try:
		browser.get(get_link)
		soup = BeautifulSoup(browser.page_source, "lxml")
		browser.quit()
		return soup
	except:
		browser.quit()
		return None

def create_unique_object_id():
    unique_object_id = "RA_{uuid}".format(uuid=uuid.uuid4())
    return unique_object_id
 
valiance = MongoClient('192.168.2.152:27000')
db = valiance['TCR']
collections = db.company_url.find_one({})

for site in collections['url']:
	if site.startswith('http') is False:
		site = 'http://'+site
	if db.test.find({'url':site}).count():
		print(site)
		continue
	temp = site.split(':')
	depth = 2
	sites = set()
	visited = set()
	sites.add(site)
	id = create_unique_object_id()

	for i in range(depth):
	    next = set()
	    for links in sites:
	    	print(links)
	        soup = visit(links)
	        if soup is not None:
	            if i is 0:
	                dict_data = {"id":id, "url":links, "title":str(soup.title.text), "data":str(soup), "section":[]}
	                db.test.insert_one(dict_data)
	            else:
	                try:
	                    dict_data = {"url":links, "title":str(soup.title.text), "data":str(soup)}
	                    db.test.update_one({"url":site}, {"$push":{"section": dict_data}})
	                except:
	                	print('Error')
	            for link in soup.find_all('a', href = True):
	                if temp[1] in link['href'] or link['href'].startswith('/'):
	                    if link['href'].startswith('/') and len(link['href']) > 1:
	                        link['href'] = site+link['href'][1:]
	                if link['href'] not in visited:
	                    #print(link['href'])
	                    visited.add(link['href'])
	                    next.add(link['href'])
	    print("Crawling done for "+links)
	    sites = next
	print("Over for "+site+" in collections")