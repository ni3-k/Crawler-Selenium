from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from pymongo import MongoClient
import uuid
import re

def visit(get_link):
	#options = Options()
	#options.add_argument("--headless")
	#browser = webdriver.Firefox(firefox_options=options)
	browser = webdriver.Firefox()
	#browser = webdriver.Chrome('C:\Users\Val\Anaconda2\selenium\webdriver\chromedriver.exe')
	print(get_link)
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

# To trackle links like /product.html, /home.html
def check_link(link, site):
    if site in link:
        return 'In'
    elif link.startswith('http'):
        return 'Out'
    elif len(link) < 2:
    	return 'Out'
    else: return 'Half'


def link_maker(half_link, site):
    """Manages Relative links"""
    if half_link.startswith('/'):
        link = site + half_link[1:]
    else:
        link = site + half_link
    return link


valiance = MongoClient('192.168.2.152:27000')
db = valiance['TCR']
collections = db.company_url.find_one({})

for site in collections['url']:
	if site.startswith('http') is False:
		site = 'http://'+site
	if site.endswith('/') is False:
		site = site+'/'
	if db.test.find({'url':site}):
		print('Already done for '+site)
		continue
	depth = 2
	sites = set()
	visited = set()
	sites.add(site)
	id = create_unique_object_id()

	for i in range(depth):
	    next = set()
	    for links in sites:
	        soup = visit(links)
	        if soup is not None:
	            if i is 0:
	                try:
	                    dict_data = {"id":id, "url":links, "title":str(soup.title.text), "data":str(soup), "section":[]}
	                    db.test.insert_one(dict_data)
	                except:
	                    dict_data = {"id":id, "url":links, "title":None, "data":str(soup), "section":[]}
	                    db.test.insert_one(dict_data)
	            else:
	                try:
	                    dict_data = {"url":links, "title":str(soup.title.text), "data":str(soup)}
	                    db.test.update_one({"url":site}, {"$push":{"section": dict_data}})
	                except:
	                    dict_data = {"id":id, "url":links, "title":None, "data":str(soup), "section":[]}
	                    db.test.insert_one(dict_data)
	            for link in soup.find_all('a', href = True):
	                link_status = check_link(link['href'], site)
	                if link_status is 'Out':
	                    continue
	                elif link_status is 'Half':
	                    link['href'] = link_maker(link['href'], site)
	                if link['href'] not in visited:
	                    #print(link['href'])
	                    visited.add(link['href'])
	                    next.add(link['href'])
	    print("Crawling done for "+links)
	    sites = next
	print("Site Complete: "+site)