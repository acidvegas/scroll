#!/usr/bin/env python
# Scroll IRC Art Bot - Developed by acidvegas in Python (https://acid.vegas/scroll)
# config.py

class connection:
	server  = 'irc.server.com'
	port    = 6667
	ipv6    = False
	ssl     = False
	vhost   = None
	channel = '#chats'
	key     = None

class cert:
	file     = None
	password = None

class ident:
	nickname = 'scroll'
	username = 'scroll'
	realname = 'acid.vegas/scroll'

class login:
	nickserv = None
	operator = None

class settings:
	admin = 'nick!user@host' # Must be in nick!user@host format (Wildcards accepted)
	modes = None