from lbscrape.database import Image
import json


with open('seed.json') as f:
	images = json.load(f)

for img in images:
	print('Inserting %s sub: %s url:%s'%(img['fullname'], img['subreddit'], img['url']))
	Image.create(**img)