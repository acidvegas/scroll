#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Scroll IRC Bot - Developed by acidvegas in Python (https://acid.vegas/scroll))
# mircart.py

from PIL import Image, ImageDraw, ImageFont

def ansi(input_file):
	ansi_colors = [97,30,94,32,91,31,35,33,93,92,36,96,34,95,90,37]
	canvasStore = canvas.(input_file)
	inMap = canvasStore.outMap.copy(); del canvasStore;
	with open(input_file, 'w+') as output_file:
		for inCurRow in range(len(inMap)):
			lastAttribs = canvas._CellState.CS_NONE
			lastColours = None
			for inCurCol in range(len(inMap[inCurRow])):
				inCurCell = inMap[inCurRow][inCurCol]
				if lastAttribs != inCurCell[2]:
					if inCurCell[2] & canvas._CellState.CS_BOLD:
						print('\u001b[1m', end='', file=output_file)
					if inCurCell[2] & canvas._CellState.CS_UNDERLINE:
						print('\u001b[4m', end='', file=output_file)
					lastAttribs = inCurCell[2]
				if lastColours == None or lastColours != inCurCell[:2]:
					ansiBg = ansi_colors[int(inCurCell[1])] + 10
					ansiFg = ansi_colors[int(inCurCell[0])]
					print('\u001b[{:02d}m\u001b[{:02d}m{}'.format(ansiBg, ansiFg, inCurCell[3]), end='', file=output_file)
					lastColours = inCurCell[:2]
				else:
					print(inCurCell[3], end='', file=output_file)
			print('\u001b[0m\n', end='', file=output_file)

def canonicalise(input_file):
	canvasStore = canvas.(input_file)
	inMap = canvasStore.outMap.copy(); del canvasStore;
	with open(input_file, 'w+') as output_file:
		for inCurRow in range(len(inMap)):
			lastAttribs = canvas._CellState.CS_NONE
			lastColours = None
			for inCurCol in range(len(inMap[inCurRow])):
				inCurCell = inMap[inCurRow][inCurCol]
				if lastAttribs != inCurCell[2]:
					if inCurCell[2] & canvas._CellState.CS_BOLD:
						print('\u0002', end='', file=output_file)
					if inCurCell[2] & canvas._CellState.CS_UNDERLINE:
						print('\u001f', end='', file=output_file)
					lastAttribs = inCurCell[2]
				if lastColours == None or lastColours != inCurCell[:2]:
					print('\u0003{:02d},{:02d}{}'.format(*inCurCell[:2], inCurCell[3]), end='', file=output_file)
					lastColours = inCurCell[:2]
				else:
					print(inCurCell[3], end='', file=output_file)
			print('\n', end='', file=output_file)#!/usr/bin/env python3

class canvas():
	def flip_cell_state(self, cellState, bit):
		if cellState & bit:
			return cellState & ~bit
		else:
			return cellState | bit

	def parse_char(self, colourSpec, curColours):
		if len(colourSpec) > 0:
			colourSpec = colourSpec.split(',')
			if len(colourSpec) == 2 and len(colourSpec[1]) > 0:
				return (int(colourSpec[0] or curColours[0]), int(colourSpec[1]))
			elif len(colourSpec) == 1 or len(colourSpec[1]) == 0:
				return (int(colourSpec[0]), curColours[1])
		else:
			return (15, 1)

	def importTextFile(self, pathName):
		self.inFile = open(pathName, 'r', encoding='utf-8')
		self.inSize = self.outMap = None;
		inCurColourSpec = ''; inCurRow = -1;
		inLine = self.inFile.readline()
		inSize = [0, 0]; outMap = []; inMaxCols = 0;
		while inLine:
			inCellState = 0x00
			inParseState = 1
			inCurCol = 0; inMaxCol = len(inLine);
			inCurColourDigits = 0; inCurColours = (15, 1); inCurColourSpec = '';
			inCurRow += 1; outMap.append([]); inRowCols = 0; inSize[1] += 1;
			while inCurCol < inMaxCol:
				inChar = inLine[inCurCol]
				if inChar in set('\r\n'):
					inCurCol += 1
				elif inParseState == 1:
					inCurCol += 1
					if inChar == '':
						inCellState = self.flip_cell_state(inCellState, 0x01)
					elif inChar == '':
						inParseState = 2
					elif inChar == '':
						inCellState = self.flip_cell_state(inCellState, 0x02)
					elif inChar == '':
						inCellState |= 0x00
						inCurColours = (15, 1)
					elif inChar == '':
						inCurColours = (inCurColours[1], inCurColours[0])
					elif inChar == '':
						inCellState = self.flip_cell_state(inCellState, 0x04)
					else:
						inRowCols += 1
						outMap[inCurRow].append([*inCurColours, inCellState, inChar])
				elif inParseState == 2 or inParseState == 3:
					if inChar == ',' and inParseState == 2:
						if (inCurCol + 1) < inMaxCol and not inLine[inCurCol + 1] in set('0123456789'):
							inCurColours = self.parse_char(inCurColourSpec, inCurColours)
							inCurColourDigits = 0; inCurColourSpec = '';
							inParseState = 1
						else:
							inCurCol += 1
							inCurColourDigits = 0; inCurColourSpec += inChar;
							inParseState = 3
					elif inChar in set('0123456789') and inCurColourDigits == 0:
						inCurCol += 1
						inCurColourDigits += 1; inCurColourSpec += inChar;
					elif inChar in set('0123456789') and inCurColourDigits == 1 and inCurColourSpec[-1] == '0':
						inCurCol += 1
						inCurColourDigits += 1; inCurColourSpec += inChar;
					elif inChar in set('012345') and inCurColourDigits == 1 and inCurColourSpec[-1] == '1':
						inCurCol += 1
						inCurColourDigits += 1; inCurColourSpec += inChar;
					else:
						inCurColours = self.parse_char(inCurColourSpec, inCurColours)
						inCurColourDigits = 0; inCurColourSpec = '';
						inParseState = 1
			inMaxCols = max(inMaxCols, inRowCols)
			inLine = self.inFile.readline()
		inSize[0] = inMaxCols;
		self.inSize = inSize;
		self.outMap = outMap;
		self.inFile.close()

# canvasStore = canvas.(inFile=argv[1])
# MiRCARTToPngFile(canvasStore.outMap, *argv[3:]).export(argv[2])
class png:
    inFile = inFromTextFile = None
    outFontFilePath = outFontSize = None
    _ColourMapBold   = [[255,255,255],[85,85,85],[85,85,255],[85,255,85],[255,85,85],[255,85,85],[255,85,255],[255,255,85],[255,255,85],[85,255,85],[85,255,255],[85,255,255],[85,85,255],[255,85,255],[85,85,85],[255,255,255]]
    _ColourMapNormal = [[255,255,255],[0,0,0],[0,0,187],[0,187,0],[255,85,85],[187,0,0],[187,0,187],[187,187,0],[255,255,85],[85,255,85],[0,187,187],[85,255,255],[85,85,255],[255,85,255],[85,85,85],[187,187,187]]

    def __init__(self, inCanvasMap, fontFilePath='DejaVuSansMono.ttf', fontSize=11):
        self.inCanvasMap = inCanvasMap
        self.outFontFilePath = fontFilePath; self.outFontSize = int(fontSize);
        self.outImgFont = ImageFont.truetype(self.outFontFilePath, self.outFontSize)
        self.outImgFontSize = [*self.outImgFont.getsize(' ')]
        self.outImgFontSize[1] += 3

    def _drawUnderLine(self, curPos, fontSize, imgDraw, fillColour):
        imgDraw.line(xy=(curPos[0], curPos[1] + (fontSize[1] - 2), curPos[0] + fontSize[0], curPos[1] + (fontSize[1] - 2)), fill=fillColour)

    def export(self, output_file):
        inSize = (len(self.inCanvasMap[0]), len(self.inCanvasMap))
        outSize = [a*b for a,b in zip(inSize, self.outImgFontSize)]
        outCurPos = [0, 0]
        outImg = Image.new('RGBA', outSize, (*self. _ColourMapNormal[1], 255))
        outImgDraw = ImageDraw.Draw(outImg)
        for inCurRow in range(len(self.inCanvasMap)):
            for inCurCol in range(len(self.inCanvasMap[inCurRow])):
                inCurCell = self.inCanvasMap[inCurRow][inCurCol]
                outColours = [0, 0]
                if inCurCell[2] & canvas._CellState.CS_BOLD:
                    if inCurCell[3] != ' ':
                        if inCurCell[3] == '█':
                            outColours[1] = self._ColourMapNormal[inCurCell[0]]
                        else:
                            outColours[0] = self._ColourMapBold[inCurCell[0]]
                            outColours[1] = self._ColourMapNormal[inCurCell[1]]
                    else:
                        outColours[1] = self._ColourMapNormal[inCurCell[1]]
                else:
                    if inCurCell[3] != ' ':
                        if inCurCell[3] == '█':
                            outColours[1] = self._ColourMapNormal[inCurCell[0]]
                        else:
                            outColours[0] = self._ColourMapNormal[inCurCell[0]]
                            outColours[1] = self._ColourMapNormal[inCurCell[1]]
                    else:
                        outColours[1] = self._ColourMapNormal[inCurCell[1]]
                outImgDraw.rectangle((*outCurPos, outCurPos[0] + self.outImgFontSize[0], outCurPos[1] + self.outImgFontSize[1]), fill=(*outColours[1], 255))
                if not inCurCell[3] in ' █' and outColours[0] != outColours[1]:
                    outImgDraw.text(outCurPos, inCurCell[3], (*outColours[0], 255), self.outImgFont)
                if inCurCell[2] & canvas._CellState.CS_UNDERLINE:
                    outColours[0] = self._ColourMapNormal[inCurCell[0]]
                    self._drawUnderLine(outCurPos, self.outImgFontSize, outImgDraw, (*outColours[0], 255))
                outCurPos[0] += self.outImgFontSize[0]
            outCurPos[0] = 0
            outCurPos[1] += self.outImgFontSize[1]
        outImg.save(output_file)

def reduce(input_file):
	canvasStore = canvas.(input_file)
	inMap = canvasStore.outMap.copy(); del canvasStore;
	with open(input_file, 'w+') as output_file:
		for inCurRow in range(len(inMap)):
			lastAttribs = canvas._CellState.CS_NONE
			lastColours = None
			for inCurCol in range(len(inMap[inCurRow])):
				inCurCell = inMap[inCurRow][inCurCol]
				if lastAttribs != inCurCell[2]:
					if inCurCell[2] & canvas._CellState.CS_BOLD:
						print('\u0002', end='', file=output_file)
					if inCurCell[2] & canvas._CellState.CS_UNDERLINE:
						print('\u001f', end='', file=output_file)
					lastAttribs = inCurCell[2]
				if lastColours == None or (lastColours[0] != inCurCell[:2][0] and lastColours[1] != inCurCell[:2][1]):
					print('\u0003{:d},{:d}{}'.format(*inCurCell[:2], inCurCell[3]), end='', file=output_file)
					lastColours = inCurCell[:2]
				elif lastColours[1] == inCurCell[:2][1] and lastColours[0] != inCurCell[:2][0]:
					print('\u0003{:d}{}'.format(inCurCell[:2][0], inCurCell[3]), end='', file=output_file)
					lastColours[0] = inCurCell[:2][0]
				else:
					print(inCurCell[3], end='', file=output_file)
			print('\n', end='', file=output_file)