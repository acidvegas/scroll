#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Scroll IRC Art Bot - Developed by acidvegas in Python (https://acid.vegas/scroll)
# ascii2png.py

'''
Credits to VXP for making the original "pngbot" script (https://github.com/lalbornoz/MiRCARTools)
'''

import os
import urllib.request

from PIL import Image, ImageDraw, ImageFont

def flip_cell_state(cellState, bit):
	if cellState & bit:
		return cellState & ~bit
	else:
		return cellState | bit

def parse_char(colourSpec, curColours):
	if len(colourSpec) > 0:
		colourSpec = colourSpec.split(',')
		if len(colourSpec) == 2 and len(colourSpec[1]) > 0:
			return (int(colourSpec[0] or curColours[0]), int(colourSpec[1]))
		elif len(colourSpec) == 1 or len(colourSpec[1]) == 0:
			return (int(colourSpec[0]), curColours[1])
	else:
		return (15, 1)

def ascii_png(url):
	text_file = os.path.join('data','temp.txt')
	if os.path.isfile(text_file):
		os.remove(text_file)
	urllib.request.urlretrieve(url, text_file)
	data = open(text_file)
	inCurColourSpec = ''
	inCurRow = -1
	inLine = data.readline()
	inSize = [0, 0]
	inMaxCols = 0
	outMap = []
	while inLine:
		inCellState = 0x00
		inParseState = 1
		inCurCol = 0
		inMaxCol = len(inLine)
		inCurColourDigits = 0
		inCurColours = (15, 1)
		inCurColourSpec = ''
		inCurRow += 1
		outMap.append([])
		inRowCols = 0
		inSize[1] += 1
		while inCurCol < inMaxCol:
			inChar = inLine[inCurCol]
			if inChar in set('\r\n'):
				inCurCol += 1
			elif inParseState == 1:
				inCurCol += 1
				if inChar == '':
					inCellState = flip_cell_state(inCellState, 0x01)
				elif inChar == '':
					inParseState = 2
				elif inChar == '':
					inCellState = flip_cell_state(inCellState, 0x02)
				elif inChar == '':
					inCellState |= 0x00
					inCurColours = (15, 1)
				elif inChar == '':
					inCurColours = (inCurColours[1], inCurColours[0])
				elif inChar == '':
					inCellState = flip_cell_state(inCellState, 0x04)
				else:
					inRowCols += 1
					outMap[inCurRow].append([*inCurColours, inCellState, inChar])
			elif inParseState == 2 or inParseState == 3:
				if inChar == ',' and inParseState == 2:
					if (inCurCol + 1) < inMaxCol and not inLine[inCurCol + 1] in set('0123456789'):
						inCurColours = parse_char(inCurColourSpec, inCurColours)
						inCurColourDigits = 0
						inCurColourSpec = ''
						inParseState = 1
					else:
						inCurCol += 1
						inCurColourDigits = 0
						inCurColourSpec += inChar
						inParseState = 3
				elif inChar in set('0123456789') and inCurColourDigits == 0:
					inCurCol += 1
					inCurColourDigits += 1
					inCurColourSpec += inChar
				elif inChar in set('0123456789') and inCurColourDigits == 1 and inCurColourSpec[-1] == '0':
					inCurCol += 1
					inCurColourDigits += 1
					inCurColourSpec += inChar
				elif inChar in set('012345') and inCurColourDigits == 1 and inCurColourSpec[-1] == '1':
					inCurCol += 1
					inCurColourDigits += 1
					inCurColourSpec += inChar
				else:
					inCurColours = parse_char(inCurColourSpec, inCurColours)
					inCurColourDigits = 0
					inCurColourSpec = ''
					inParseState = 1
		inMaxCols = max(inMaxCols, inRowCols)
		inLine = data.readline()
	inSize[0] = inMaxCols
	canvas_data = outMap
	numRowCols = 0
	for numRow in range(len(outMap)):
		numRowCols = max(numRowCols, len(outMap[numRow]))
	for numRow in range(len(outMap)):
		if len(outMap[numRow]) != numRowCols:
			for numColOff in range(numRowCols - len(outMap[numRow])):
				outMap[numRow].append([1,1,0,' '])
		outMap[numRow].insert(0,[1,1,0,' '])
		outMap[numRow].append([1,1,0,' '])
	outMap.insert(0,[[1,1,0,' ']] * len(outMap[0]))
	outMap.append([[1,1,0,' ']] * len(outMap[0]))
	inCanvasMap = outMap
	outImgFont = ImageFont.truetype(os.path.join('data','DejaVuSansMono.ttf'), 11)
	outImgFontSize = [*outImgFont.getsize(' ')]
	outImgFontSize[1] += 3
	ColorsBold   = [[255,255,255],[85,85,85],[85,85,255],[85,255,85],[255,85,85],[255,85,85],[255,85,255],[255,255,85],[255,255,85],[85,255,85],[85,255,255],[85,255,255],[85,85,255],[255,85,255],[85,85,85],[255,255,255]]
	ColorsNormal = [[255,255,255],[0,0,0],[0,0,187],[0,187,0],[255,85,85],[187,0,0],[187,0,187],[187,187,0],[255,255,85],[85,255,85],[0,187,187],[85,255,255],[85,85,255],[255,85,255],[85,85,85],[187,187,187]]
	inSize = (len(inCanvasMap[0]), len(inCanvasMap))
	outSize = [a*b for a,b in zip(inSize, outImgFontSize)]
	outCurPos = [0, 0]
	outImg = Image.new('RGBA', outSize, (*ColorsNormal[1], 255))
	outImgDraw = ImageDraw.Draw(outImg)
	for inCurRow in range(len(inCanvasMap)):
		for inCurCol in range(len(inCanvasMap[inCurRow])):
			inCurCell = inCanvasMap[inCurRow][inCurCol]
			outColours = [0, 0]
			if inCurCell[2] & 0x01:
				if inCurCell[3] != ' ':
					if inCurCell[3] == '█':
						outColours[1] = ColorsNormal[inCurCell[0]]
					else:
						outColours[0] = ColorsBold[inCurCell[0]]
						outColours[1] = ColorsNormal[inCurCell[1]]
				else:
					outColours[1] = ColorsNormal[inCurCell[1]]
			else:
				if inCurCell[3] != ' ':
					if inCurCell[3] == '█':
						outColours[1] = ColorsNormal[inCurCell[0]]
					else:
						outColours[0] = ColorsNormal[inCurCell[0]]
						outColours[1] = ColorsNormal[inCurCell[1]]
				else:
					outColours[1] = ColorsNormal[inCurCell[1]]
			outImgDraw.rectangle((*outCurPos,outCurPos[0] + outImgFontSize[0], outCurPos[1] + outImgFontSize[1]), fill=(*outColours[1], 255))
			if  not inCurCell[3] in ' █' and outColours[0] != outColours[1]:
				outImgDraw.text(outCurPos,inCurCell[3], (*outColours[0], 255), outImgFont)
			if inCurCell[2] & 0x04:
				outColours[0] = ColorsNormal[inCurCell[0]]
				outImgDraw.line(xy=(outCurPos[0], outCurPos[1] + (outImgFontSize[1] - 2), outCurPos[0] + outImgFontSize[0], outCurPos[1] + (outImgFontSize[1] - 2)), fill=(*outColours[0], 255))
			outCurPos[0] += outImgFontSize[0]
		outCurPos[0] = 0
		outCurPos[1] += outImgFontSize[1]
	out_file = os.path.join('data','temp.png')
	if os.path.isfile(out_file):
		os.remove(out_file)
	outImg.save(out_file)