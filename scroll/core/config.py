#!/usr/bin/env python
# Scroll IRC Bot - Developed by acidvegas in Python (https://acid.vegas/scroll)
# config.py

class connection:
	server     = 'irc.server.com'
	port       = 6697
	proxy      = None
	ipv6       = False
	ssl        = True
	ssl_verify = False
	vhost      = None
	channel    = '#chats'
	key        = None

class cert:
	key      = None
	file     = None
	password = None

class ident:
	nickname = 'scroll'
	username = 'scroll'
	realname = 'acid.vegas/scroll'

class login:
	network  = None
	nickserv = None
	operator = None

class settings:
	admin = 'nick!user@host' # Must be in nick!user@host format (Can use wildcards here)
	log   = False
	modes = None

IMGUR_API_KEY = 'CHANGEME' # https://apidocs.imgur.com/
