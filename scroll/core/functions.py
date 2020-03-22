#!/usr/bin/env python
# Scroll IRC Art Bot - Developed by acidvegas in Python (https://acid.vegas/scroll)
# functions.py

import random
import re
import subprocess

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
