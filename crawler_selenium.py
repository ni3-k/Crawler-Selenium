from bs4 import BeautifulSoup
from selenium import webdriver
from pymongo import MongoClient
import uuid

def visit(get_link):
	browser = webdriver.Firefox()
	try:
		browser.get(get_link)
		soup = BeautifulSoup(browser.page_source, "lxml")
		browser.quit()
	except:
		browser.quit()
		return None
	return soup

def create_unique_object_id():
    unique_object_id = "RA_{uuid}".format(uuid=uuid.uuid4())
    return unique_object_id
 
valiance = MongoClient('192.168.2.152:27000')
db = valiance['TCR']
collections = db.company_url.find_one({})

for site in collections['url']:
	if site.startswith('http') is False:
		site = 'http://'+site
	temp = site.split(':')
	depth = 2
	sites = set()
	visited = set()
	sites.add(site)


	for i in range(depth):
	    next = set()
	    for links in sites:
	        id = create_unique_object_id()
	        soup = visit(links)
	        if soup is not None:
	            if i is 0:
	                dict_data = {"id":id, "url":links, "title":str(soup.title.text), "data":str(soup), "section":[]}
	                db.test.insert_one(dict_data)
	            else:
	                dict_data = {"url":links, "title":str(soup.title.text), "data":str(soup)}
	                db.test.update_one({"url":site}, {"$push":{"section": dict_data}})
	            for link in soup.find_all('a', href = True):
	                if temp[1] in link['href'] or link['href'].startswith('/'):
	                    if link['href'].startswith('/'):
	                        if len(link['href']) > 1 and link['href'][1] == '/':
	                            link['href'] = 'https:'+link['href']
	                        else:
	                            link['href'] = site+link['href']
	                    if temp[0] not in link['href']:
	                        http = link['href'].split(':')
	                        link['href'] = 'https:'+http[1]

	                    if link['href'] not in visited:
	                        #print(link['href'])
	                        visited.add(link['href'])
	                        next.add(link['href'])
	    sites = next