#!/usr/bin/python3

import requests
import json

SEED_AMOUNT = 50
params = dict(wanted=SEED_AMOUNT)

def check_subreddit_validity(subreddit):
	resp = requests.get('http://lbscrape:8000/check/%s'%subreddit)
	if resp.status_code == 200:
		return resp.json().get('valid', False)
	return False

def create_job(subreddit):
	resp = requests.get('http://lbscrape:8000/r/%s'%subreddit, params=params)
	if resp.status_code == 202:
		data = resp.json()
		job_id = data.get('result', dict()).get('uuid', None)
		return job_id
	return None

with open('seed.json') as f:
	subs = json.load(f)

for sub in subs:
	if check_subreddit_validity(sub):
		print('Seeding %s'%sub)
		uuid = create_job(sub)
		if uuid:
			print('Created job for %s with id %s'%(sub, uuid))
		else:
			print('Failed to create job for %s'%sub)
	else:
		print('%s is not a vaid subreddit!'%sub)
print('Finished queueing jobs')