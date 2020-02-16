#!/usr/bin/env python

class store():
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