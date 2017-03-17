import requests

def collapse_double_list(dlist):
	'''
		collapses a list of lists	[[1,2,3],[4,5,6],[7,8,9]]
		into a single list 			[1,2,3,4,5,6,7,8,9]
	'''
	out = []
	for slist in dlist:
		if isinstance(slist, list):
			for v in slist:
				out.append(v)
		else:
			out.append(slist)
	return out

def recurse_list(l):
	for i in l:
		if isinstance(i, list):
			for ir in recurse_list(i):
				yield ir
		else:
			yield i
			
# Check if a url is valid
def check_url(url):
	'''
		check if a HEAD call to url returns 200
	'''
	try:
		response = requests.head(url)
		if response.status_code == 200:
			return True
	except:
		pass
	return False
