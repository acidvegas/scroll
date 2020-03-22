#!/usr/bin/env python
# Scroll IRC Art Bot - Developed by acidvegas in Python (https://acid.vegas/scroll)
# scroll.py

import os
import sys

sys.dont_write_bytecode = True
os.chdir(sys.path[0] or '.')
sys.path += ('core',)

print('#'*56)
print('#{:^54}#'.format(''))
print('#{:^54}#'.format('Scroll IRC Art Bot'))
print('#{:^54}#'.format('Developed by acidvegas in Python'))
print('#{:^54}#'.format('https://acid.vegas/scroll'))
print('#{:^54}#'.format(''))
print('#'*56)
import database
database.check()
import irc
irc.Bot.connect()
