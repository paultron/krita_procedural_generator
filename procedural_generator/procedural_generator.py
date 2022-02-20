from krita import Krita, DockWidget, QWidget, QCheckBox, QLabel, QPushButton, QSpinBox, QVBoxLayout
from PyQt5.QtCore import pyqtSlot
import random

DOCKER_TITLE = 'Procedural Generator'


class ProceduralGenerator(DockWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle(DOCKER_TITLE)

        mainWidget = QWidget(self)

        self.setWidget(mainWidget)

        buttonGenerateSingle = QPushButton("Generate This Layer!", mainWidget)
        buttonGenerateSingle.clicked.connect(self.generateThisLayer)

        buttonGenerateAll = QPushButton("Generate All!", mainWidget)
        buttonGenerateAll.clicked.connect(self.generateAllLayers)

        buttonDrawOutline = QPushButton("Draw Outline", mainWidget)
        buttonDrawOutline.clicked.connect(lambda x: self.drawOutline(
            Krita.instance().activeDocument().activeNode()))

        # self.checkLayersAll = QCheckBox("All Layers", mainWidget)
        self.checkMirrorX = QCheckBox("Mirror X Generation", mainWidget)
        self.checkMirrorY = QCheckBox("Mirror Y Generation", mainWidget)
        self.checkStrayPixels = QCheckBox("Remove Stray Pixels", mainWidget)
        self.checkOutlineCorners = QCheckBox(
            "Outline Extra Corners", mainWidget)
        self.checkOutlineGenerate = QCheckBox(
            "Generate with fg outline", mainWidget)
        labelVariations = QLabel("Number of variations:", mainWidget)
        self.spinVariations = QSpinBox(mainWidget)
        self.spinVariations.setMinimum(1)

        mainWidget.setLayout(QVBoxLayout())
        mainWidget.layout().addWidget(buttonGenerateSingle)
        mainWidget.layout().addWidget(buttonGenerateAll)
        mainWidget.layout().addWidget(buttonDrawOutline)

        # mainWidget.layout().addWidget(self.checkLayersAll)
        mainWidget.layout().addWidget(self.checkMirrorX)
        mainWidget.layout().addWidget(self.checkMirrorY)
        mainWidget.layout().addWidget(self.checkStrayPixels)
        mainWidget.layout().addWidget(self.checkOutlineGenerate)
        mainWidget.layout().addWidget(self.checkOutlineCorners)
        mainWidget.layout().addWidget(labelVariations)
        mainWidget.layout().addWidget(self.spinVariations)

    # notifies when views are added or removed
    # 'pass' means do not do anything
    def canvasChanged(self, canvas):
        pass

    def generateLayer(self, aNode, newNode):

        width = self.activeDoc.width()
        height = self.activeDoc.height()

        # GET centerPixel value
        cp = 0

        # byte array for active layer
        pixelBytes = aNode.pixelData(
            0, 0, width, height)
        newPixelBytes = newNode.pixelData(
            0, 0, width, height)

        # loop through each pixel
        for pix in range(0, len(pixelBytes), 4):
            if (self.checkMirrorX.isChecked() and pix/4 % width > width/2 - (1-(width % 2))):
                continue
            if (self.checkMirrorY.isChecked() and int(pix/4 / width) > height/2 - (1-(width % 2))):
                continue

            x = pix/4 % width
            y = int(pix/4 / width)

            # B, G, R
            thisPixel = [int.from_bytes(pixelBytes[pix + 0], 'little'),
                         int.from_bytes(pixelBytes[pix + 1], 'little'),
                         int.from_bytes(pixelBytes[pix + 2], 'little')]
            # A
            oldAlpha = int.from_bytes(
                pixelBytes[pix+3], 'little')

            tempPixel = [int.from_bytes(newPixelBytes[pix + 0], 'little'),
                         int.from_bytes(newPixelBytes[pix + 1], 'little'),
                         int.from_bytes(newPixelBytes[pix + 2], 'little')]

            # roll the chance that the pixel gets generated
            chance = int(random.random() * 256)

            newAlpha = 255 if (oldAlpha == 255 or chance < oldAlpha) else 0

            # if (chance <= oldAlpha) and (oldAlpha > 0):

            #newAlpha = 255
            if newAlpha == 255:
                newNode.setPixelData(
                    bytearray([thisPixel[0], thisPixel[1], thisPixel[2], newAlpha]), x, y, 1, 1)

            # mirror horizontally
            if self.checkMirrorX.isChecked():

                # mirror horizontally
                pX = pix + ((width/2-x) * 2 - 1 - cp)*4
                xPixel = [int.from_bytes(pixelBytes[pX + 0], 'little'),
                          int.from_bytes(pixelBytes[pX + 1], 'little'),
                          int.from_bytes(pixelBytes[pX + 2], 'little')]

                # if it's not empty
                if (pixelBytes[pX+3] != 0):
                    # if passes chance
                    newAlpha = 255 if (
                        int.from_bytes(pixelBytes[pX + 3], 'little') == 255 or chance < int.from_bytes(pixelBytes[pX + 3], 'little')) else 0
                    if newAlpha == 255:
                        newNode.setPixelData(
                            bytearray([xPixel[0], xPixel[1], xPixel[2], newAlpha]), (pX/4) % width, y, 1, 1)

            # mirror vertically
            if self.checkMirrorY.isChecked():

                # mirror vertically
                pY = pix + ((height/2-y) * 2 - 1 - cp)*width*4
                yPixel = [int.from_bytes(pixelBytes[pY + 0], 'little'),
                          int.from_bytes(pixelBytes[pY + 1], 'little'),
                          int.from_bytes(pixelBytes[pY + 2], 'little')]

                # if it's not empty
                if (pixelBytes[pY+3] != 0):
                    # if passes chance
                    newAlpha = 255 if (
                        int.from_bytes(pixelBytes[pY + 3], 'little') == 255 or chance < int.from_bytes(pixelBytes[pY + 3], 'little')) else 0
                    if newAlpha == 255:

                        newNode.setPixelData(
                            bytearray([yPixel[0], yPixel[1], yPixel[2], newAlpha]), x, y+(width/2-y)*2-1-cp, 1, 1)

            # mirror horizontally and vertically
            if (self.checkMirrorX.isChecked() and self.checkMirrorY.isChecked()):

                # mirror vertically and horizontally
                pXY = pix + ((width/2-x) * 2 - 1 - cp)*4 + \
                    ((height/2-y) * 2 - 1 - cp)*width*4
                xyPixel = [int.from_bytes(pixelBytes[pXY + 0], 'little'),
                           int.from_bytes(pixelBytes[pXY + 1], 'little'),
                           int.from_bytes(pixelBytes[pXY + 2], 'little')]
                # if it's not empty
                if (pixelBytes[pXY+3] != 0):
                    # if passes chance
                    newAlpha = 255 if (
                        int.from_bytes(pixelBytes[pXY + 3], 'little') == 255 or chance < int.from_bytes(pixelBytes[pXY + 3], 'little')) else 0
                    if newAlpha == 255:

                        newNode.setPixelData(
                            bytearray([xyPixel[0], xyPixel[1], xyPixel[2], newAlpha]), (pXY/4) % width, y+(width/2-y)*2-1-cp, 1, 1)

        if self.checkStrayPixels.isChecked():

            pixelBytes = newNode.pixelData(
                0, 0, width+2, height+2)

            for pix in range(0, len(pixelBytes), 4):
                # print(pixelBytes[pix+3])
                thisPixel = [int.from_bytes(pixelBytes[pix + 0], 'little'),
                             int.from_bytes(pixelBytes[pix + 1], 'little'),
                             int.from_bytes(pixelBytes[pix + 2], 'little')]

                x = int(pix/4 % (width+2))
                y = int(pix/4 / (width+2))

                l = pix - 4
                r = pix + 4
                u = pix - 4 * (width + 2)
                ul = pix - 4 * (width + 2) - 4
                ur = pix - 4 * (width + 2) + 4
                d = pix + 4 * (width + 2)
                dl = pix + 4 * (width + 2) - 4
                dr = pix + 4 * (width + 2) + 4
                # print(f"{pix}: x{x} y{y}")
                if x <= width and y <= height:
                    if (pixelBytes[l+3] == b'\x00' and
                            pixelBytes[r+3] == b'\x00' and
                            pixelBytes[u+3] == b'\x00' and
                            pixelBytes[ul+3] == b'\x00' and
                            pixelBytes[ur+3] == b'\x00' and
                            pixelBytes[d+3] == b'\x00' and
                            pixelBytes[dl+3] == b'\x00' and
                            pixelBytes[dr+3] == b'\x00'):
                        # erase
                        newNode.setPixelData(
                            bytearray([thisPixel[0], thisPixel[1], thisPixel[2], 0]), x, y, 1, 1)

        if self.checkOutlineGenerate.isChecked():
            self.drawOutline(newNode)

        # self.activeDoc.refreshProjection()

    def generateThisLayer(self):
        self.activeDoc = Krita.instance().activeDocument()
        root = self.activeDoc.rootNode()
        aNode = self.activeDoc.activeNode()
        if not aNode.locked():
            _groupLayer = self.activeDoc.createNode("Output(s)", "groupLayer")
            root.addChildNode(_groupLayer, None)
            for v in range(self.spinVariations.value()):
                layerName = "Variation " + str(v + 1)
                _newLayer = self.activeDoc.createNode(layerName, "paintLayer")
                self.generateLayer(aNode, _newLayer)
                _groupLayer.addChildNode(_newLayer, None)
                _newLayer.setLocked(True)
                # self.activeDoc.refreshProjection()
            _groupLayer.setLocked(True)
            self.activeDoc.refreshProjection()  # update canvas on screen

    def generateAllLayers(self):
        self.activeDoc = Krita.instance().activeDocument()
        root = self.activeDoc.rootNode()

        for v in range(self.spinVariations.value()):
            layerName = "Variation " + str(v + 1)
            _newLayer = self.activeDoc.createNode(layerName, "paintLayer")

            # grab all top level nodes
            self.topLevelLayers = self.activeDoc.topLevelNodes()

            for layer in self.topLevelLayers:
                if layer.visible() and not layer.locked():
                    if len(layer.pixelData(0, 0, self.activeDoc.width(), self.activeDoc.height())) > 0:
                        self.activeDoc.setActiveNode(layer)
                        self.activeNode = self.activeDoc.activeNode()
                        self.generateLayer(self.activeNode, _newLayer)

                    layerChildren = layer.childNodes()

                    if len(layerChildren) > 0:
                        # we have children, so loop through those
                        for child in layerChildren:
                            if child.visible() and (len(child.pixelData(0, 0, self.activeDoc.width(), self.activeDoc.height())) > 0) and not child.locked():
                                self.activeDoc.setActiveNode(child)
                                self.activeNode = self.activeDoc.activeNode()
                                self.generateLayer(self.activeNode, _newLayer)

            root.addChildNode(_newLayer, None)
            _newLayer.setLocked(True)

        self.activeDoc.refreshProjection()  # update canvas on screen

    def drawOutline(self, aNode):
        if not aNode.locked():
            self.activeDoc = Krita.instance().activeDocument()

            aView = Krita.instance().activeWindow().activeView()
            # aNode = activeDoc.activeNode()

            fg = aView.foregroundColor().colorForCanvas(aView.canvas())
            fgBytes = bytearray([fg.blue(), fg.green(), fg.red()])

            width = self.activeDoc.width()
            height = self.activeDoc.height()

            pixelBytes = aNode.pixelData(
                0, 0, width+2, height+2)

            for pix in range(0, len(pixelBytes), 4):

                thisPixel = [int.from_bytes(pixelBytes[pix + 0], 'little'),
                             int.from_bytes(pixelBytes[pix + 1], 'little'),
                             int.from_bytes(pixelBytes[pix + 2], 'little')]

                x = int(pix/4 % (width+2))
                y = int(pix/4 / (width+2))

                l = pix - 4
                r = pix + 4
                u = pix - 4 * (width + 2)
                ul = pix - 4 * (width + 2) - 4
                ur = pix - 4 * (width + 2) + 4
                d = pix + 4 * (width + 2)
                dl = pix + 4 * (width + 2) - 4
                dr = pix + 4 * (width + 2) + 4

                if (x <= width and y <= height and pixelBytes[pix + 3] == b'\x00'):
                    if ((pixelBytes[l:l+3] != fgBytes and pixelBytes[l+3] != b'\x00') or
                            (pixelBytes[r:r+3] != fgBytes and pixelBytes[r+3] != b'\x00') or
                            (pixelBytes[u:u+3] != fgBytes and pixelBytes[u+3] != b'\x00') or
                            (pixelBytes[d:d+3] != fgBytes and pixelBytes[d+3] != b'\x00') or
                            (pixelBytes[ul:ul+3] != fgBytes and pixelBytes[ul+3] != b'\x00' and self.checkOutlineCorners.isChecked()) or
                            (pixelBytes[ur:ur+3] != fgBytes and pixelBytes[ur+3] != b'\x00' and self.checkOutlineCorners.isChecked()) or
                            (pixelBytes[dl:dl+3] != fgBytes and pixelBytes[dl+3] != b'\x00' and self.checkOutlineCorners.isChecked()) or
                            (pixelBytes[dr:dr+3] != fgBytes and pixelBytes[dr+3] != b'\x00' and self.checkOutlineCorners.isChecked())):
                        aNode.setPixelData(
                            bytearray([fg.blue(), fg.green(), fg.red(), 255]), x, y, 1, 1)
            self.activeDoc.refreshProjection()
