#!/usr/bin/env python
# Scroll IRC Bot - Developed by acidvegas in Python (https://acid.vegas/scroll)
# functions.py

import base64
import json
import os
import random
import re
import subprocess
import urllib.parse
import urllib.request

import config

def cmd(command):
	return subprocess.check_output(command, shell=True).decode()

def check_trunc(trunc):
	trunc = trunc.split(',')
	if len(trunc) == 5 and ''.join(trunc).isdigit():
		trunc = [int(item) for item in trunc]
		up,down,left,right,space=trunc
		if down == 0:
			down = 1
		if right == 0:
			right = 1
		return trunc
	else:
		return False

def get_size(file_path):
	return os.path.getsize(file_path)

def get_source(url):
	return urllib.request.urlopen(url, timeout=15).read().decode('utf8')

def imgur_upload(file_path):
	data = urllib.parse.urlencode({'image':base64.b64encode(open(file_path,'rb').read()),'key':config.IMGUR_API_KEY,'name':'ASCII uploaded via Scroll','title':'ASCII uploaded via Scroll','type':'base64'}).encode('utf8')
	headers = {'Authorization':'Client-ID ' + config.IMGUR_API_KEY}
	req = urllib.request.Request('https://api.imgur.com/3/upload.json', data, headers)
	response = json.loads(urllib.request.urlopen(req).read())
	return response['data']['link']

def is_admin(ident):
	return re.compile(config.settings.admin.replace('*','.*')).search(ident)

def floatint(data):
	if data.isdigit():
		return int(data)
	else:
		try:
			return float(data)
		except:
			return data

def random_int(min, max):
	return random.randint(min, max)
