from krita import Krita, DockWidget
from PyQt5.QtWidgets import (
    QWidget, QCheckBox, QFrame, QGridLayout, QLabel, QPushButton, QSpinBox)
from random import random, randint

DOCKER_TITLE = 'Procedural Generator'


class ProceduralGenerator(DockWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle(DOCKER_TITLE)

        mainWidget = QWidget(self)

        self.setWidget(mainWidget)

        buttonGenerateSingle = QPushButton("Generate This Layers Pixels!")
        buttonGenerateSingle.clicked.connect(self.generateThisLayer)

        buttonGenerateAll = QPushButton("Generate All Layers Pixels!")
        buttonGenerateAll.clicked.connect(self.generateAllLayers)

        buttonDrawOutline = QPushButton("Draw Outline On This Layer ")
        buttonDrawOutline.clicked.connect(self.drawOutlineThisLayer)

        buttonGenerateGrouped = QPushButton(
            "Generate from whole layers/groups")
        buttonGenerateGrouped.clicked.connect(self.generateFromGroups)

        self.checkMirrorX = QCheckBox("Mirror X Generation")
        self.checkMirrorY = QCheckBox("Mirror Y Generation")
        self.checkStrayPixels = QCheckBox("Remove Stray Pixels")
        self.checkOutlineCorners = QCheckBox(
            "Outline Extra Corners")
        self.checkOutlineGenerate = QCheckBox(
            "Generate with foreground outline")
        self.checkDuplicateOutline = QCheckBox(
            "Allow duplicate outline"
        )
        self.checkFlattenGroups = QCheckBox("Merge Output")

        labelVariations = QLabel("Number of variations:")
        self.spinVariations = QSpinBox(mainWidget)
        self.spinVariations.setMinimum(1)

        mainLayout = QGridLayout()
        mainLayout.addWidget(buttonGenerateSingle, 0, 0)
        mainLayout.addWidget(buttonGenerateAll, 0, 1)

        mainLayout.addWidget(buttonDrawOutline, 1, 0, 1, 2)

        mainLayout.addWidget(self.checkMirrorX, 2, 0)
        mainLayout.addWidget(self.checkMirrorY, 2, 1)

        frameSeparate = QFrame()
        frameSeparate.setFrameShape(4)
        mainLayout.addWidget(frameSeparate, 3, 0, 1, 2)

        mainLayout.addWidget(self.checkStrayPixels, 4, 0, 1, 2)
        mainLayout.addWidget(self.checkOutlineGenerate, 5, 0, 1, 2)
        mainLayout.addWidget(self.checkOutlineCorners, 6, 0, 1, 2)
        mainLayout.addWidget(self.checkDuplicateOutline, 7, 0, 1, 2)
        mainLayout.addWidget(labelVariations, 8, 0)
        mainLayout.addWidget(self.spinVariations, 8, 1)

        mainLayout.addWidget(buttonGenerateGrouped, 9, 0, 1, 2)
        mainLayout.addWidget(self.checkFlattenGroups, 10, 0, 1, 2)

        mainWidget.setLayout(mainLayout)

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

            # roll the chance that the pixel gets generated
            chance = randint(0, 255)

            newAlpha = 255 if (oldAlpha == 255 or chance < oldAlpha) else 0

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

    def generateThisLayer(self):
        self.activeDoc = Krita.instance().activeDocument()
        aNode = self.activeDoc.activeNode()
        if (aNode.visible() and not aNode.locked() and
                aNode.type() == "paintlayer"):
            # len(aNode.pixelData(0, 0, self.activeDoc.width(), self.activeDoc.height())) > 0):
            root = self.activeDoc.rootNode()
            groupLayer = self.activeDoc.createNode("Output(s)", "grouplayer")
            root.addChildNode(groupLayer, None)
            for v in range(self.spinVariations.value()):
                layerName = "Variation " + str(v + 1)
                _newLayer = self.activeDoc.createNode(layerName, "paintlayer")
                self.generateLayer(aNode, _newLayer)
                if self.checkStrayPixels.isChecked():
                    self.removeStrayPixels(_newLayer)
                if self.checkOutlineGenerate.isChecked():
                    self.drawOutline(_newLayer)
                groupLayer.addChildNode(_newLayer, None)
                _newLayer.setLocked(True)
                # self.activeDoc.refreshProjection()
            groupLayer.setLocked(True)
            self.activeDoc.refreshProjection()  # update canvas on screen

    def generateAllLayers(self):
        self.activeDoc = Krita.instance().activeDocument()
        root = self.activeDoc.rootNode()
        groupLayer = self.activeDoc.createNode("Output(s)", "groupLayer")
        root.addChildNode(groupLayer, None)
        for v in range(self.spinVariations.value()):
            layerName = "Variation " + str(v + 1)
            _newLayer = self.activeDoc.createNode(layerName, "paintLayer")

            # grab all top level nodes
            self.topLevelLayers = self.activeDoc.topLevelNodes()

            for layer in self.topLevelLayers:
                if (layer.visible() and not layer.locked()):
                    if layer.type() == "paintlayer":
                        self.generateLayer(layer, _newLayer)

                    elif layer.type() == "grouplayer":
                        layerChildren = layer.childNodes()

                        if len(layerChildren) > 0:
                            # we have children, so loop through those
                            for child in layerChildren:
                                if child.visible() and child.type() == "paintlayer" and not child.locked():
                                    self.generateLayer(child, _newLayer)
            if self.checkStrayPixels.isChecked():
                self.removeStrayPixels(_newLayer)
            if self.checkOutlineGenerate.isChecked():
                self.drawOutline(_newLayer)
            groupLayer.addChildNode(_newLayer, None)
            _newLayer.setLocked(True)
        groupLayer.setLocked(True)
        self.activeDoc.refreshProjection()  # update canvas on screen

    def removeStrayPixels(self, aNode):

        self.activeDoc = Krita.instance().activeDocument()

        width = self.activeDoc.width()
        height = self.activeDoc.height()

        pixelBytes = aNode.pixelData(
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
                    aNode.setPixelData(
                        bytearray([thisPixel[0], thisPixel[1], thisPixel[2], 0]), x, y, 1, 1)

    def drawOutline(self, aNode):
        if not aNode.locked():
            self.activeDoc = Krita.instance().activeDocument()

            aView = Krita.instance().activeWindow().activeView()

            fg = aView.foregroundColor().colorForCanvas(aView.canvas())
            fgBytes = bytearray([fg.blue(), fg.green(), fg.red()])

            width = self.activeDoc.width()
            height = self.activeDoc.height()

            pixelBytes = aNode.pixelData(
                0, 0, width+2, height+2)

            for pix in range(0, len(pixelBytes), 4):

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
                    if (((pixelBytes[l:l+3] != fgBytes or self.checkDuplicateOutline.isChecked()) and pixelBytes[l+3] != b'\x00') or
                            ((pixelBytes[r:r+3] != fgBytes or self.checkDuplicateOutline.isChecked()) and pixelBytes[r+3] != b'\x00') or
                            ((pixelBytes[u:u+3] != fgBytes or self.checkDuplicateOutline.isChecked()) and pixelBytes[u+3] != b'\x00') or
                            ((pixelBytes[d:d+3] != fgBytes or self.checkDuplicateOutline.isChecked()) and pixelBytes[d+3] != b'\x00') or
                            ((pixelBytes[ul:ul+3] != fgBytes or self.checkDuplicateOutline.isChecked()) and pixelBytes[ul+3] != b'\x00' and self.checkOutlineCorners.isChecked()) or
                            ((pixelBytes[ur:ur+3] != fgBytes or self.checkDuplicateOutline.isChecked()) and pixelBytes[ur+3] != b'\x00' and self.checkOutlineCorners.isChecked()) or
                            ((pixelBytes[dl:dl+3] != fgBytes or self.checkDuplicateOutline.isChecked()) and pixelBytes[dl+3] != b'\x00' and self.checkOutlineCorners.isChecked()) or
                            ((pixelBytes[dr:dr+3] != fgBytes or self.checkDuplicateOutline.isChecked()) and pixelBytes[dr+3] != b'\x00' and self.checkOutlineCorners.isChecked())):
                        aNode.setPixelData(
                            bytearray([fg.blue(), fg.green(), fg.red(), 255]), x, y, 1, 1)

    def drawOutlineThisLayer(self):
        self.activeDoc = Krita.instance().activeDocument()
        aNode = self.activeDoc.activeNode()
        if (aNode.visible() and not aNode.locked() and aNode.type() == "paintlayer"):
            root = Krita.instance().activeDocument().rootNode()
            _newLayer = aNode.clone()
            self.drawOutline(_newLayer)
            if _newLayer.pixelData(0, 0, self.activeDoc.width(), self.activeDoc.height()) != aNode.pixelData(0, 0, self.activeDoc.width(), self.activeDoc.height()):
                _newLayer.setName(aNode.name() + " Outlined")
                root.addChildNode(_newLayer, None)

                Krita.instance().activeDocument().refreshProjection()

    def generateFromGroups(self):
        if self.checkFlattenGroups.isChecked():
            self.generateGroupsMerged()
        else:
            self.generateToGroups()

    def generateToGroups(self):
        self.activeDoc = Krita.instance().activeDocument()
        root = self.activeDoc.rootNode()

        # grab all top level nodes
        self.topLevelLayers = self.activeDoc.topLevelNodes()

        for v in range(self.spinVariations.value()):
            groupLayer = self.activeDoc.createNode("Output", "grouplayer")

            for layer in self.topLevelLayers:

                if layer.visible() and not layer.locked():
                    # if it's a paint layer, use opacity as chance
                    if layer.type() == "paintlayer":
                        if randint(0, 255) <= layer.opacity():
                            _cloneLayer = layer.clone()
                            groupLayer.addChildNode(_cloneLayer, None)
                            _cloneLayer.setOpacity(255)
                            # _cloneLayer.setLocked(True)

                    elif layer.type() == "grouplayer":
                        # go into groups, and pick one at random with even chances
                        layerChildren = layer.childNodes()
                        if len(layerChildren) > 0:
                            # we have children, so loop through those
                            groupLayer.addChildNode(
                                layerChildren[randint(0, len(layerChildren)-1)].clone(), None)

            # merge the group layer here
            if (len(groupLayer.childNodes()) > 0):
                root.addChildNode(groupLayer, None)
                groupLayer.setName("Grouped Output " + str(v+1))
                groupLayer.setLocked(True)

        self.activeDoc.refreshProjection()  # update canvas on screen

    def generateGroupsMerged(self):

        self.activeDoc = Krita.instance().activeDocument()
        root = self.activeDoc.rootNode()

        # grab all top level nodes
        self.topLevelLayers = self.activeDoc.topLevelNodes()
        groupLayer = Krita.instance().activeDocument().createNode("Output(s)", "grouplayer")

        for v in range(self.spinVariations.value()):
            outputLayer = self.activeDoc.createNode(
                "Variation " + str(v+1), "paintlayer")

            for layer in self.topLevelLayers:

                if layer.visible() and not layer.locked():
                    # if it's a paint layer, use opacity as chance
                    if layer.type() == "paintlayer":
                        if randint(0, 255) <= layer.opacity():
                            self.copyOverLayer(layer, outputLayer)

                    elif layer.type() == "grouplayer":
                        # go into groups, and pick one at random with even chances
                        layerChildren = layer.childNodes()
                        if len(layerChildren) > 0:
                            # we have children, so loop through those
                            self.copyOverLayer(layerChildren[randint(
                                0, len(layerChildren)-1)], outputLayer)
            if self.checkStrayPixels.isChecked():
                self.removeStrayPixels(outputLayer)
            if self.checkOutlineGenerate.isChecked():
                self.drawOutline(outputLayer)
            groupLayer.addChildNode(outputLayer, None)

            # merge the group layer here
        root.addChildNode(groupLayer, None)

        groupLayer.setLocked(True)

        self.activeDoc.refreshProjection()  # update canvas on screen

    def zDiv(self, x, y):
        try:
            return (x / y)
        except ZeroDivisionError:
            return 0

    def copyOverLayer(self, topLayer, bottomLayer):
        # Copies topLayer onto bottomLayer using alpha blending
        self.activeDoc = Krita.instance().activeDocument()
        width = self.activeDoc.width()
        height = self.activeDoc.height()

        topPixelBytes = topLayer.pixelData(0, 0, width, height)
        bottomPixelBytes = bottomLayer.pixelData(0, 0, width, height)

        for pix in range(0, len(topPixelBytes), 4):

            # B, G, R, A
            topPixel = [int.from_bytes(topPixelBytes[pix + 0], 'little')/255.0,
                        int.from_bytes(topPixelBytes[pix + 1], 'little')/255.0,
                        int.from_bytes(topPixelBytes[pix + 2], 'little')/255.0,
                        int.from_bytes(topPixelBytes[pix + 3], 'little')/255.0]

            bottomPixel = [int.from_bytes(bottomPixelBytes[pix + 0], 'little')/255.0,
                           int.from_bytes(
                               bottomPixelBytes[pix + 1], 'little')/255.0,
                           int.from_bytes(
                               bottomPixelBytes[pix + 2], 'little')/255.0,
                           int.from_bytes(bottomPixelBytes[pix + 3], 'little')/255.0]

            #alpha_final = alpha_bg + alpha_fg - alpha_bg * alpha_fg
            alpha_final = bottomPixel[3] + topPixel[3] - \
                bottomPixel[3] * topPixel[3]

            red_bg_a = bottomPixel[2] * bottomPixel[3]
            green_bg_a = bottomPixel[1] * bottomPixel[3]
            blue_bg_a = bottomPixel[0] * bottomPixel[3]

            red_fg_a = topPixel[2] * topPixel[3]
            green_fg_a = topPixel[1] * topPixel[3]
            blue_fg_a = topPixel[0] * topPixel[3]

            red_final = self.zDiv(
                (red_fg_a + red_bg_a * (1 - topPixel[3])), alpha_final)
            green_final = self.zDiv(
                (green_fg_a + green_bg_a * (1 - topPixel[3])), alpha_final)
            blue_final = self.zDiv(
                (blue_fg_a + blue_bg_a * (1 - topPixel[3])), alpha_final)

            finalPixel = [int(blue_final*255),
                          int(green_final*255),
                          int(red_final*255),
                          int(alpha_final*255)]

            x = pix/4 % width
            y = int(pix/4 / width)

            if topPixel[3] > 0:
                bottomLayer.setPixelData(
                    bytearray([finalPixel[0], finalPixel[1], finalPixel[2], finalPixel[3]]), x, y, 1, 1)
