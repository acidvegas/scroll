#!/usr/bin/env python
# Scroll IRC Art Bot - Developed by acidvegas in Python (https://acid.vegas/scroll)
# database.py

import re
import sqlite3

db  = sqlite3.connect('scroll.db', check_same_thread=False)
sql = db.cursor()

def check():
	tables = sql.execute('SELECT name FROM sqlite_master WHERE type=\'table\'').fetchall()
	if not len(tables):
		sql.execute('CREATE TABLE IGNORE (IDENT TEXT NOT NULL);')
		sql.execute('CREATE TABLE SETTINGS (SETTING TEXT NOT NULL, VALUE TEXT NOT NULL);')
		sql.execute('INSERT INTO SETTINGS (SETTING,VALUE) VALUES (?,?)', ('max_lines',    '300'))
		sql.execute('INSERT INTO SETTINGS (SETTING,VALUE) VALUES (?,?)', ('max_results',  '10'))
		sql.execute('INSERT INTO SETTINGS (SETTING,VALUE) VALUES (?,?)', ('rnd_exclude',  'ansi,big,birds,hang,pokemon'))
		sql.execute('INSERT INTO SETTINGS (SETTING,VALUE) VALUES (?,?)', ('throttle_cmd', '3'))
		sql.execute('INSERT INTO SETTINGS (SETTING,VALUE) VALUES (?,?)', ('throttle_msg', '0.03'))
		db.commit()

class Ignore:
	def add(ident):
		sql.execute('INSERT INTO IGNORE (IDENT) VALUES (?)', (ident,))
		db.commit()

	def check(ident):
		for ignored_ident in Ignore.read():
			if re.compile(ignored_ident.replace('*','.*')).search(ident):
				return True
		return False

	def read():
		return [item[0] for item in sql.execute('SELECT IDENT FROM IGNORE').fetchall()]

	def remove(ident):
		sql.execute('DELETE FROM IGNORE WHERE IDENT=?', (ident,))
		db.commit()

class Settings:
	def get(setting):
		return sql.execute('SELECT VALUE FROM SETTINGS WHERE SETTING=?', (setting,)).fetchone()[0]

	def read():
		return sql.execute('SELECT SETTING,VALUE FROM SETTINGS ORDER BY SETTING ASC').fetchall()

	def settings():
		return list(item[0] for item in sql.execute('SELECT SETTING FROM SETTINGS').fetchall())

	def update(setting, value):
		sql.execute('UPDATE SETTINGS SET VALUE=? WHERE SETTING=?', (value, setting))
		db.commit()