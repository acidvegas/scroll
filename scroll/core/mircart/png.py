#!/usr/bin/env python
import canvas
from PIL import Image, ImageDraw, ImageFont

# canvasStore = canvas.store(inFile=argv[1])
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
                if inCurCell[2] & canvas.store._CellState.CS_BOLD:
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
                if inCurCell[2] & canvas.store._CellState.CS_UNDERLINE:
                    outColours[0] = self._ColourMapNormal[inCurCell[0]]
                    self._drawUnderLine(outCurPos, self.outImgFontSize, outImgDraw, (*outColours[0], 255))
                outCurPos[0] += self.outImgFontSize[0]
            outCurPos[0] = 0
            outCurPos[1] += self.outImgFontSize[1]
        outImg.save(output_file)