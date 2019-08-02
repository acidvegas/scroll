#!/usr/bin/env python
# Scroll IRC Bot - Developed by acidvegas in Python (https://acid.vegas/scroll)
# irc.py

import glob
import os
import random
import socket
import threading
import time

import ascii2png
import config
import constants
import database
import debug
import functions

# Load optional modules
if config.connection.ssl:
	import ssl
if config.connection.proxy:
	try:
		import sock
	except ImportError:
		debug.error_exit('Missing PySocks module! (https://pypi.python.org/pypi/PySocks)') # Required for proxy support.

def color(msg, foreground, background=None):
	return f'\x03{foreground},{background}{msg}{constants.reset}' if background else f'\x03{foreground}{msg}{constants.reset}'

ascii_dir = os.path.join('data', 'art')

class IRC(object):
	def __init__(self):
		self.last     = 0
		self.last_png = 0
		self.playing  = False
		self.slow     = False
		self.stopper  = False
		self.sock     = None

	def connect(self):
		try:
			self.create_socket()
			self.sock.connect((config.connection.server, config.connection.port))
			self.register()
		except socket.error as ex:
			debug.error('Failed to connect to IRC server.', ex)
			Events.disconnect()
		else:
			self.listen()

	def create_socket(self):
		family = socket.AF_INET6 if config.connection.ipv6 else socket.AF_INET
		if config.connection.proxy:
			proxy_server, proxy_port = config.connection.proxy.split(':')
			self.sock = socks.socksocket(family, socket.SOCK_STREAM)
			self.sock.setblocking(0)
			self.sock.settimeout(15)
			self.sock.setproxy(socks.PROXY_TYPE_SOCKS5, proxy_server, int(proxy_port))
		else:
			self.sock = socket.socket(family, socket.SOCK_STREAM)
		if config.connection.vhost:
			self.sock.bind((config.connection.vhost, 0))
		if config.connection.ssl:
			ctx = ssl.create_default_context()
			if config.cert.file:
				ctx.load_cert_chain(config.cert.file, config.cert.key, config.cert.password)
			if config.connection.ssl_verify:
				ctx.verify_mode = ssl.CERT_REQUIRED
				ctx.load_default_certs()
			else:
				ctx.check_hostname = False
				ctx.verify_mode = ssl.CERT_NONE
			self.sock = ctx.wrap_socket(self.sock)

	def listen(self):
		while True:
			try:
				data = self.sock.recv(1024).decode('utf-8')
				for line in (line for line in data.split('\r\n') if len(line.split()) >= 2):
					debug.irc(line)
					Events.handle(line)
			except (UnicodeDecodeError, UnicodeEncodeError):
				pass
			except Exception as ex:
				debug.error('Unexpected error occured.', ex)
				break
		Events.disconnect()

	def register(self):
		if config.login.network:
			Commands.raw('PASS ' + config.login.network)
		Commands.raw(f'USER {config.ident.username} 0 * :{config.ident.realname}')
		Commands.raw('NICK '+ config.ident.nickname)

class Commands:
	def error(chan, msg, reason=None):
		if reason:
			Commands.sendmsg(chan, '[{0}] {1} {2}'.format(color('ERROR', constants.red), msg, color(f'({reason})', constants.grey)))
		else:
			Commands.sendmsg(chan, '[{0}] {1}'.format(color('ERROR', constants.red), msg))

	def join_channel(chan, key=None):
		Commands.raw(f'JOIN {chan} {key}') if key else Commands.raw('JOIN ' + chan)

	def play(chan, ascii_file, trunc=None):
		try:
			Bot.playing = True
			data = open(ascii_file, encoding='utf8', errors='replace').read()
			if len(data.splitlines()) > int(database.Settings.get('max_lines')) and chan != '#scroll':
				Commands.error(chan, 'File is too big.', 'Take it to #scroll')
			else:
				name = ascii_file.split(ascii_dir)[1]
				data = data.splitlines()[trunc[0]:-trunc[1]] if trunc else data.splitlines()
				Commands.sendmsg(chan, ascii_file.split(ascii_dir)[1])
				for line in (line for line in data if line):
					if Bot.stopper:
						break
					elif trunc:
						line = line[trunc[2]:-trunc[3]]
					Commands.sendmsg(chan, ' '*trunc[4] + line) if trunc else Commands.sendmsg(chan, line)
		except Exception as ex:
			debug.error('Error occured in the play function!', ex)
		finally:
			Bot.stopper = False
			Bot.playing = False

	def raw(msg):
		Bot.sock.send(bytes(msg + '\r\n', 'utf-8'))

	def sendmsg(target, msg):
		Commands.raw(f'PRIVMSG {target} :{msg}')
		time.sleep(functions.floatint(database.Settings.get('msg_throttle')))

class Events:
	def connect():
		if config.settings.modes:
			Commands.raw(f'MODE {config.ident.nickname} +{config.settings.modes}')
		if config.login.nickserv:
			Commands.sendmsg('NickServ', f'IDENTIFY {config.ident.nickname} {config.login.nickserv}')
		if config.login.operator:
			Commands.raw(f'OPER {config.ident.username} {config.login.operator}')
		Commands.join_channel(config.connection.channel, config.connection.key)
		Commands.join_channel('#scroll')

	def disconnect():
		Bot.sock.close()
		time.sleep(15)
		Bot.connect()

	def kick(chan, kicked):
		if kicked == config.ident.nickname:
			if chan == config.connection.channel:
				time.sleep(3)
				Commands.join_channel(chan, config.connection.key)
			elif chan == '#scroll':
				time.sleep(3)
				Commands.join_channel(chan)

	def message(ident, nick, chan, msg):
		try:
			args = msg.split()
			if msg == '@scroll':
				Commands.sendmsg(chan, constants.bold + 'Scroll IRC Bot - Developed by acidvegas in Python - https://acid.vegas/scroll')
			elif args[0] == '.ascii' and not database.Ignore.check(ident):
				if Bot.playing and msg == '.ascii stop':
					Bot.stopper = True
				elif time.time() - Bot.last < int(database.Settings.get('cmd_throttle')) and not functions.is_admin(ident):
					if not Bot.slow:
						Commands.error(chan, 'Slow down nerd!')
						Bot.slow = True
				elif len(args) >= 2:
					Bot.slow = False
					if args[1] == 'dirs' and len(args) == 2:
						dirs = sorted(glob.glob(os.path.join(ascii_dir, '*/')))
						for directory in dirs:
							name = os.path.basename(os.path.dirname(directory))
							file_count = str(len(glob.glob(os.path.join(directory, '*.txt'))))
							Commands.sendmsg(chan, '[{0}] {1} {2}'.format(color(str(dirs.index(directory)+1).zfill(2), constants.pink), name.ljust(10), color(f'({file_count})', constants.grey)))
					elif args[1] == 'png' and len(args) == 3:
						url = args[2]
						if url.startswith('https://pastebin.com/raw/') or url.startswith('http://termbin.com/'):
							ascii2png.ascii_png(url)
							ascii_file = os.path.join('data','temp.png')
							if os.path.getsize(ascii_file) < int(database.Settings.get('png_max_bytes')):
								Commands.sendmsg(chan, functions.imgur_upload(os.path.join('data','temp.png')))
								Bot.last_png = time.time()
							else:
								Commands.error(chan, 'File too large', '2MB Max')
						else:
							Commands.error(chan, 'Invalid URL.', 'Only PasteBin & TermBin URLs can be used.')
					elif args[1] == 'remote' and len(args) == 3:
						url = args[2]
						if 'pastebin.com/raw/' in url or 'termbin.com/' in url:
							data = functions.get_source(url)
							if data:
								for item in data.split('\n'):
									Commands.sendmsg(chan, item)
							else:
								Commands.error(chan, 'Found no data on URL!')
						else:
							Commands.error(chan, 'Invalid URL!', 'Must be a pastebin.com or termbin.com link.')
					elif args[1] == 'search' and len(args) == 3:
						query   = args[2]
						results = glob.glob(os.path.join(ascii_dir, f'**/*{query}*.txt'), recursive=True)
						if results:
							results = results[:int(database.Settings.get('max_results'))]
							for file_name in results:
								count = str(results.index(file_name)+1)
								Commands.sendmsg(chan, '[{0}] {1}'.format(color(count.zfill(2), constants.pink), os.path.basename(file_name)))
						else:
							Commands.error(chan, 'No results found.')
					elif args[1] == 'upload':
						if len(args) == 2:
							uploads = database.Uploads.read()
							if uploads:
								for upload in uploads:
									Commands.sendmsg(chan, '[{0}] {1} - {2} - {3}.txt'.format(color(uploads.index(upload)+1, constants.pink), color(upload[0], constants.yellow), color(upload[1], constants.grey), upload[2]))
							else:
								Commands.error(chan, 'No uploaded files!', 'Use ".ascii upload <url> <title>" to upload.')
						elif len(args) == 4:
							url = args[2]
							if url.startswith('https://pastebin.com/raw/') or url.startswith('https://termbin.com/'):
								if url not in [item[1] for item in database.Uploads.read()]:
									title = args[3].lower()[:20]
									check = (glob.glob(os.path.join(ascii_dir, f'**/{title}.txt'), recursive=True)[:1] or [None])[0]
									if not check:
										if len(database.Uploads.read(nick)) == int(database.Settings.get('max_uploads_per')):
											database.Uploads.remove(database.Uploads.read(nick)[0][1])
										elif len(database.Uploads.read()) == int(database.Settings.get('max_uploads')):
											database.Uploads.remove(database.Uploads.read()[0][1])
										database.Uploads.add(nick, url, title)
										Commands.sendmsg(chan, 'Uploaded!')
									else:
										Commands.error(chan, 'File with that title already exists!')
								else:
									Commands.error(chan, 'URL is already uploaded!')
							else:
								Commands.error(chan, 'Invalid URL.', 'Only PasteBin & TermBin URLs can be used.')
					elif args[1] == 'random':
						if len(args) == 2:
							ascii_file = random.choice([file for file in glob.glob(os.path.join(ascii_dir, '**/*.txt'), recursive=True) if os.path.basename(os.path.dirname(file)) not in database.Settings.get('rnd_exclude').split(',')])
							threading.Thread(target=Commands.play, args=(chan, ascii_file)).start()
						elif len(args) == 3:
							dir = args[2]
							if '../' in dir:
								Commands.error(chan, 'Nice try nerd!')
							elif os.path.isdir(os.path.join(ascii_dir, dir)):
								ascii_file = random.choice(glob.glob(os.path.join(ascii_dir, dir + '/*.txt'), recursive=True))
								threading.Thread(target=Commands.play, args=(chan, ascii_file)).start()
							else:
								Commands.error(chan, 'Invalid directory name.', 'Use ".ascii dirs" for a list of valid directory names.')
					else:
						option = args[1]
						if '/' in option:
							Commands.error(chan, 'Nice try nerd!')
						else:
							ascii_file = (glob.glob(os.path.join(ascii_dir, f'**/{option}.txt'), recursive=True)[:1] or [None])[0]
							if ascii_file:
								if len(args) == 3:
									trunc = functions.check_trunc(args[2])
									if trunc:
										threading.Thread(target=Commands.play, args=(chan, ascii_file, trunc)).start()
									else:
										Commands.error(chan, 'Invalid truncate option.' 'Use TOP,BOTTOM,LEFT,RIGHT,SPACE as integers to truncate.')
								else:
									threading.Thread(target=Commands.play, args=(chan, ascii_file)).start()
							else:
								Commands.error(chan, 'Invalid file name.', 'Use ".ascii list" for a list of valid file names.')
					Bot.last = time.time()
		except Exception as ex:
			if time.time() - Bot.last < int(database.Settings.get('cmd_throttle')):
				if not Bot.slow:
					Commands.sendmsg(chan, color('Slow down nerd!', constants.red))
					Bot.slow = True
			else:
				Commands.error(chan, 'Command threw an exception.', ex)
			Bot.last = time.time()

	def private(ident, nick, msg):
		if functions.is_admin(ident):
			args = msg.split()
			if msg == '.update':
				output = functions.cmd(f'git -C {ascii_dir} reset --hard FETCH_HEAD')
				if output:
					for line in output.split('\n'):
						Commands.sendmsg(chan, line)
			elif args[0] == '.config':
				if len(args) == 1:
					settings = database.Settings.read()
					Commands.sendmsg(nick, '[{0}]'.format(color('Settings', constants.purple)))
					for setting in settings:
						Commands.sendmsg(nick, '{0} = {1}'.format(color(setting[0], constants.yellow), color(setting[1], constants.grey)))
				elif len(args) == 3:
					setting, value = args[1], args[2]
					if setting in database.Settings.settings():
						database.Settings.update(setting, value)
						Commands.sendmsg(nick, 'Change setting for {0} to {1}.'.format(color(setting, constants.yellow), color(value, constants.grey)))
					else:
						Commands.error(nick, 'Invalid config variable.')
			elif args[0] == '.ignore':
				if len(args) == 1:
					ignores = database.Ignore.read()
					if ignores:
						Commands.sendmsg(nick, '[{0}]'.format(color('Ignore List', constants.purple)))
						for ignore_ident in ignores:
							Commands.sendmsg(nick, color(ignore_ident, constants.yellow))
						Commands.sendmsg(nick, '{0} {1}'.format(color('Total:', constants.light_blue), color(len(ignores), constants.grey)))
					else:
						Commands.error(nick, 'Ignore list is empty!')
				elif len(args) == 2 and args[0] == '.ignore':
					option = args[1][:1]
					if option in '+-':
						ignore_ident = args[1][1:]
						if (not database.Ignore.check(ignore_ident) and option == '+') or (database.Ignore.check(ignore_ident) and option == '-'):
							database.Ignore.add(ignore_ident) if option == '+' else database.Ignore.remove(ignore_host)
							Commands.sendmsg(nick, 'Ignore list has been updated!')
						else:
							Commands.error(nick, 'Invalid option')
					else:
						Commands.error(nick, 'Invalid option', 'Must be a + or - prefixing the ident.')
			elif args[0] == '.raw' and len(args) >= 2:
				data = msg[5:]
				Commands.raw(data)


	def nick_in_use():
		config.ident.nickname = 'scroll' + str(functions.random_int(10,99))
		Commands.nick(config.ident.nickname)

	def handle(data):
		args = data.split()
		if args[0] == constants.PING:
			Commands.raw('PONG ' + args[1][1:])
		elif args[1] == constants.RPL_WELCOME:
			Events.connect()
		elif args[1] == constants.ERR_NICKNAMEINUSE:
			Events.nick_in_use()
		elif args[1] == constants.KICK and len(args) >= 4:
			chan   = args[2]
			kicked = args[3]
			Events.kick(chan, kicked)
		elif args[1] == constants.PRIVMSG and len(args) >= 4:
			ident = args[0][1:]
			nick  = args[0].split('!')[0][1:]
			chan  = args[2]
			msg   = ' '.join(args[3:])[1:]
			if chan == config.ident.nickname:
				Events.private(ident, nick, msg)
			elif chan in (config.connection.channel,'#scroll'):
				Events.message(ident, nick, chan, msg)

Bot = IRC()
