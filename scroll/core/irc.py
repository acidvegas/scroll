#!/usr/bin/env python
# Scroll IRC Art Bot - Developed by acidvegas in Python (https://acid.vegas/scroll)
# irc.py

import chardet
import glob
import os
import random
import socket
import ssl
import threading
import time

import config
import database
import functions

# Control characters & color codes
bold        = '\x02'
underline   = '\x1F'
reset       = '\x0f'
white       = '00'
black       = '01'
blue        = '02'
green       = '03'
red         = '04'
brown       = '05'
purple      = '06'
orange      = '07'
yellow      = '08'
light_green = '09'
cyan        = '10'
light_cyan  = '11'
light_blue  = '12'
pink        = '13'
grey        = '14'
light_grey  = '15'

def color(msg, foreground, background=None):
	return f'\x03{foreground},{background}{msg}{reset}' if background else f'\x03{foreground}{msg}{reset}'

class IRC(object):
	def __init__(self):
		self.last     = 0
		self.playing  = False
		self.slow     = False
		self.stopper  = False
		self.sock     = None

	def connect(self):
		try:
			self.sock = socket.socket(socket.AF_INET6) if config.connection.ipv6 else socket.socket()
			if config.connection.vhost:
				self.sock.bind((config.connection.vhost, 0))
			if config.connection.ssl:
				ctx = ssl.create_default_context()
				ctx.check_hostname = False
				ctx.verify_mode = ssl.CERT_NONE
				if config.cert.file:
					ctx.load_cert_chain(config.cert.file, password=config.cert.password)
				self.sock = ctx.wrap_socket(self.sock)
			self.sock.connect((config.connection.server, config.connection.port))
			Commands.raw(f'USER {config.ident.username} 0 * :{config.ident.realname}')
			Commands.raw('NICK '+ config.ident.nickname)
		except Exception as ex:
			print(f'[!] - Failed to connect to IRC server! ({ex!s})')
			Events.disconnect()
		else:
			self.listen()

	def listen(self):
		while True:
			try:
				data = self.sock.recv(1024).decode('utf-8')
				for line in (line for line in data.split('\r\n') if len(line.split()) >= 2):
					print('[~] - ' + line)
					Events.handle(line)
			except (UnicodeDecodeError, UnicodeEncodeError):
				pass
			except Exception as ex:
				print(f'[!] - Unexpected error occured! ({ex!s})')
				break
		Events.disconnect()

class Commands:
	def error(chan, msg, reason=None):
		if reason:
			Commands.sendmsg(chan, '[{0}] {1} {2}'.format(color('ERROR', red), msg, color(f'({reason})', grey)))
		else:
			Commands.sendmsg(chan, '[{0}] {1}'.format(color('ERROR', red), msg))

	def join_channel(chan, key=None):
		Commands.raw(f'JOIN {chan} {key}') if key else Commands.raw('JOIN ' + chan)

	def play(chan, ascii_file, trunc=None):
		try:
			Bot.playing = True
			data = open(ascii_file, 'rb').read()
			data = data.decode(chardet.detect(data)['encoding'])
			if len(data.splitlines()) > functions.floatint(database.Settings.get('max_lines')) and chan != '#scroll':
				Commands.error(chan, 'File is too big.', 'Take it to #scroll')
			else:
				data = data.splitlines()[trunc[0]:-trunc[1]] if trunc else data.splitlines()
				Commands.sendmsg(chan, f'{bold}the ascii gods have chosen: {underline}{ascii_file[4:-4]}')
				for line in (line for line in data if line):
					if Bot.stopper:
						break
					elif trunc:
						line = line[trunc[2]:-trunc[3]]
					Commands.sendmsg(chan, ' '*trunc[4]+line+reset) if trunc else Commands.sendmsg(chan, line+reset)
		except Exception as ex:
			print(f'Error occured in the play function! ({ex!s})')
		finally:
			Bot.stopper = False
			Bot.playing = False

	def raw(data):
		Bot.sock.send(bytes(data[:510] + '\r\n', 'utf-8'))

	def sendmsg(target, msg):
		Commands.raw(f'PRIVMSG {target} :{msg}')
		time.sleep(functions.floatint(database.Settings.get('throttle_msg')))

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

	def message(ident, nick, chan, msg):
		try:
			args = msg.split()
			if msg == '@scroll':
				Commands.sendmsg(chan, bold + 'Scroll IRC Bot - Developed by acidvegas in Python - https://github.com/ircart/scroll')
			elif args[0] == '.ascii' and not database.Ignore.check(ident):
				if Bot.playing and msg == '.ascii stop':
					Bot.stopper = True
				elif time.time() - Bot.last < int(database.Settings.get('throttle_cmd')) and not functions.is_admin(ident):
					if not Bot.slow:
						Commands.error(chan, 'Slow down nerd!')
						Bot.slow = True
				elif len(args) >= 2:
					Bot.slow = False
					if args[1] == 'dirs' and len(args) == 2:
						dirs = sorted(glob.glob('art/*/'))
						for directory in dirs:
							name = os.path.basename(os.path.dirname(directory))
							file_count = str(len(glob.glob(os.path.join(directory, '*.txt'))))
							Commands.sendmsg(chan, '[{0}] {1} {2}'.format(color(str(dirs.index(directory)+1).zfill(2), pink), name.ljust(10), color(f'({file_count})', grey)))
					elif args[1] == 'search' and len(args) == 3:
						query   = args[2]
						results = glob.glob(f'art/**/*{query}*.txt', recursive=True)
						if results:
							results = results[:int(database.Settings.get('max_results'))]
							for file_name in results:
								count = str(results.index(file_name)+1)
								Commands.sendmsg(chan, '[{0}] {1}'.format(color(count.zfill(2), pink), os.path.basename(file_name)[:-4]))
						else:
							Commands.error(chan, 'No results found.')
					elif args[1] == 'random':
						if len(args) == 2:
							ascii_file = random.choice([file for file in glob.glob('art/**/*.txt', recursive=True) if os.path.basename(os.path.dirname(file)) not in database.Settings.get('rnd_exclude').split(',')])
							threading.Thread(target=Commands.play, args=(chan, ascii_file)).start()
						elif len(args) == 3:
							dir = args[2]
							if not dir.isalpha():
								Commands.error(chan, 'Nice try nerd!')
							elif os.path.isdir('art/' + dir):
								ascii_file = random.choice(glob.glob(f'art/{dir}/*.txt', recursive=True))
								threading.Thread(target=Commands.play, args=(chan, ascii_file)).start()
							else:
								Commands.error(chan, 'Invalid directory name.', 'Use ".ascii dirs" for a list of valid directory names.')
					else:
						option = args[1]
						if '/' in option:
							Commands.error(chan, 'Nice try nerd!')
						else:
							ascii_file = (glob.glob(f'art/**/{option}.txt', recursive=True) or [None])[0]
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
			if time.time() - Bot.last < int(database.Settings.get('throttle_cmd')):
				if not Bot.slow:
					Commands.sendmsg(chan, color('Slow down nerd!', red))
					Bot.slow = True
			else:
				Commands.error(chan, 'Command threw an exception.', ex)
			Bot.last = time.time()

	def private(ident, nick, msg):
		if functions.is_admin(ident):
			args = msg.split()
			if msg == '.update':
				output = functions.cmd(f'git -C art pull')
				if output:
					for line in output.split('\n'):
						Commands.sendmsg(chan, line)
			elif args[0] == '.config':
				if len(args) == 1:
					settings = database.Settings.read()
					Commands.sendmsg(nick, '[{0}]'.format(color('Settings', purple)))
					for setting in settings:
						Commands.sendmsg(nick, '{0} = {1}'.format(color(setting[0], yellow), color(setting[1], grey)))
				elif len(args) == 3:
					setting, value = args[1], args[2]
					if setting in database.Settings.settings():
						database.Settings.update(setting, value)
						Commands.sendmsg(nick, 'Change setting for {0} to {1}.'.format(color(setting, yellow), color(value, grey)))
					else:
						Commands.error(nick, 'Invalid config variable.')
			elif args[0] == '.ignore':
				if len(args) == 1:
					ignores = database.Ignore.read()
					if ignores:
						Commands.sendmsg(nick, '[{0}]'.format(color('Ignore List', purple)))
						for ignore_ident in ignores:
							Commands.sendmsg(nick, color(ignore_ident, yellow))
						Commands.sendmsg(nick, '{0} {1}'.format(color('Total:', light_blue), color(len(ignores), grey)))
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

	def handle(data):
		args = data.split()
		if args[0] == 'PING':
			Commands.raw('PONG ' + args[1][1:])
		elif args[1] == '001': # RPL_WELCOME
			Events.connect()
		elif args[1] == '433': # ERR_NICKNAMEINUSE
			config.ident.nickname = 'scroll' + str(functions.random_int(10,99))
			Commands.raw('NICK '+ config.ident.nickname)
		elif args[1] == 'KICK' and len(args) >= 4:
			chan, kicked = args[2], args[3]
			if chan in (config.connection.channel,'#scroll') and kicked == config.ident.nickname:
				time.sleep(3)
				Commands.join_channel(chan, config.connection.key)
		elif args[1] == 'PRIVMSG' and len(args) >= 4:
			ident = args[0][1:]
			nick  = args[0].split('!')[0][1:]
			chan  = args[2]
			msg   = ' '.join(args[3:])[1:]
			if chan == config.ident.nickname:
				Events.private(ident, nick, msg)
			elif chan in (config.connection.channel,'#scroll'):
				Events.message(ident, nick, chan, msg)

Bot = IRC()
