# -*- coding: utf-8 -*-
# !/usr/bin/python


import sys
from sys import platform
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
from pylab import *
import scipy
from scipy import ndimage, optimize, signal
import scipy.ndimage.interpolation as spni
import scipy.fftpack as spf
from scipy.signal import *
from skimage.feature import match_template
from PIL import Image
import os
from os.path import isfile, join
import string
import pyqtgraph as pg
# from PySide import QtGui, QtCore
from pyqtgraph import QtGui, QtCore
import h5py
import tomopy
import MyImageItem


# import subpixelshift
# from subpixelshift import *

class Example(QtGui.QMainWindow):
    def __init__(self):
        super(Example, self).__init__()
        self.initUI()

    def initUI(self):
        self.fileNames = []
        self.theta = []
        self.f = []
        self.files = []
        self.thetaPos = 0
        self.ImageTag = "exchange"
        self.tmpchan = 13
        self.meanNoise = 0
        self.stdNoise = 0

        exitAction = QtGui.QAction('Exit', self)
        exitAction.triggered.connect(self.close)
        exitAction.setShortcut('Ctrl+Q')

        closeAction = QtGui.QAction('Quit', self)
        closeAction.triggered.connect(sys.exit)
        closeAction.setShortcut('Ctrl+X')

        openFileAction = QtGui.QAction('Open File', self)
        openFileAction.triggered.connect(self.openfile)

        openTiffFolderAction = QtGui.QAction("Open Tiff Folder", self)
        openTiffFolderAction.triggered.connect(self.openTiffFolder)

        sinogramAction = QtGui.QAction('Sinogram', self)
        sinogramAction.triggered.connect(self.sinogram)

        saveImageAction = QtGui.QAction('Save Projections', self)
        saveImageAction.triggered.connect(self.saveImage)

        selectElementAction = QtGui.QAction('Select Element', self)
        selectElementAction.triggered.connect(self.selectElement)

        selectFilesAction = QtGui.QAction('Select Files', self)
        selectFilesAction.triggered.connect(self.selectFilesShow)

        saveThetaTxtAction = QtGui.QAction("Save Theta Postion as txt", self)
        saveThetaTxtAction.triggered.connect(self.saveThetaTxt)

        convertAction = QtGui.QAction('Save data in memory', self)
        convertAction.triggered.connect(self.convert)

        saveSinogramAction = QtGui.QAction('Save Sinogram', self)
        saveSinogramAction.triggered.connect(self.saveSinogram)

        runReconstructAction = QtGui.QAction("Reconstruction", self)
        runReconstructAction.triggered.connect(self.runReconstruct)

        selectImageTagAction = QtGui.QAction("Select Image Tag", self)
        selectImageTagAction.triggered.connect(self.selectImageTag)

        xCorAction = QtGui.QAction("Cross Correlation", self)
        xCorAction.triggered.connect(self.CrossCorrelation_test)

        phaseXCorAction = QtGui.QAction("Phase Correlation", self)
        phaseXCorAction.triggered.connect(self.CrossCorrelation_test)

        alignFromTextAction = QtGui.QAction("Alignment from Text", self)
        alignFromTextAction.triggered.connect(self.alignFromText)

        alignFromText2Action = QtGui.QAction("Alignment from Text2", self)
        alignFromText2Action.triggered.connect(self.alignFromText2)

        saveAlignToTextAction = QtGui.QAction("Save Alignment information to text", self)
        saveAlignToTextAction.triggered.connect(self.saveAlignToText)

        restoreAction = QtGui.QAction("Restore", self)
        restoreAction.triggered.connect(self.restore)

        runCenterOfMassAction = QtGui.QAction("run center of mass action", self)
        runCenterOfMassAction.triggered.connect(self.centerOfMassWindow)

        alignCenterOfMassAction = QtGui.QAction("Align by fitting center of mass position into sine curve", self)
        alignCenterOfMassAction.triggered.connect(self.alignCenterOfMass)

        matcherAction = QtGui.QAction("match template", self)
        matcherAction.triggered.connect(self.match_window)

        selectBeamlineAction = QtGui.QAction("select beamline", self)
        selectBeamlineAction.triggered.connect(self.selectBeamline)

        exportDataAction = QtGui.QAction("export data", self)
        exportDataAction.triggered.connect(self.export_data)

        runTransRecAction = QtGui.QAction("Transmission Recon", self)
        runTransRecAction.triggered.connect(self.runTransReconstruct)

        saveHotSpotPosAction = QtGui.QAction("Save Hot Spot Pos", self)
        saveHotSpotPosAction.triggered.connect(self.saveHotSpotPos)

        alignHotSpotPosAction = QtGui.QAction("Align Hot Spot pos", self)
        alignHotSpotPosAction.triggered.connect(self.alignHotSpotPos1)

        reorderAction = QtGui.QAction("Reorder", self)
        reorderAction.triggered.connect(self.reorder_matrix)

        wienerAction = QtGui.QAction("Wiener", self)
        wienerAction.triggered.connect(self.ipWiener)

        reorderAction = QtGui.QAction("Reorder", self)
        reorderAction.triggered.connect(self.reorder_matrix)

        externalImageRegAction = QtGui.QAction("External Image Registaration", self)
        externalImageRegAction.triggered.connect(self.externalImageReg)

        ###
        self.frame = QtGui.QFrame()
        self.vl = QtGui.QVBoxLayout()

        self.tab_widget = QtGui.QTabWidget()
        # self.tab_widget.addTab(self.createMessageWidget(), unicode("Message"))
        self.tab_widget.addTab(self.createImageProcessWidget(), unicode("Image Process"))
        self.tab_widget.addTab(self.createSaveHotspotWidget(), unicode("Hotspot"))
        self.tab_widget.addTab(self.createSinoWidget(), unicode("Sinogram"))
        self.tab_widget.addTab(self.createReconWidget(), unicode("Reconstruction"))
        # self.tab_widget.addTab(self.sinoGroup, unicode("Sinogram"))
        self.tab_widget.currentChanged.connect(self.tab1manual)

        self.vl.addWidget(self.tab_widget)
        self.vl.addWidget(self.createMessageWidget())

        self.frame.setLayout(self.vl)
        self.setCentralWidget(self.frame)
        self.tab_widget.setDisabled(True)

        ## Top menu bar [file   Convert Option    Alignment   After saving in memory]
        menubar = self.menuBar()
        self.fileMenu = menubar.addMenu('&File')
        self.fileMenu.addAction(selectBeamlineAction) #to replace readconfiguration Action
        self.fileMenu.addAction(openFileAction)
        self.fileMenu.addAction(openTiffFolderAction)
        self.fileMenu.addAction(exitAction)
        self.fileMenu.addAction(closeAction)

        self.optionMenu = menubar.addMenu('Convert Option')
        self.optionMenu.addAction(selectFilesAction)
        self.optionMenu.addAction(selectImageTagAction)
        self.optionMenu.addAction(selectElementAction)
        self.optionMenu.addAction(convertAction)
        self.optionMenu.setDisabled(True)

        self.alignmentMenu = menubar.addMenu("Alignment")
        self.alignmentMenu.addAction(saveAlignToTextAction)
        self.alignmentMenu.addAction(runCenterOfMassAction)
        self.alignmentMenu.addAction(alignCenterOfMassAction)
        self.alignmentMenu.addAction(xCorAction)
        self.alignmentMenu.addAction(phaseXCorAction)
        self.alignmentMenu.addAction(matcherAction)
        self.alignmentMenu.addAction(alignFromTextAction)
        self.alignmentMenu.addAction(alignFromText2Action)
        self.alignmentMenu.addAction(saveHotSpotPosAction)
        self.alignmentMenu.addAction(alignHotSpotPosAction)
        self.alignmentMenu.addAction(externalImageRegAction)
        self.alignmentMenu.addAction(restoreAction)
        self.alignmentMenu.setDisabled(True)

        self.afterConversionMenu = menubar.addMenu('After saving data in memory')
        self.afterConversionMenu.addAction(saveImageAction)
        self.afterConversionMenu.addAction(saveThetaTxtAction)
        # self.afterConversionMenu.addAction(selectElementAction)
        self.afterConversionMenu.addAction(saveSinogramAction)
        # self.afterConversionMenu.addAction(runReconstructAction)
        self.afterConversionMenu.addAction(reorderAction)
        self.afterConversionMenu.setDisabled(True)

        add = 0
        if platform == "win32":
            add = 50
        self.setGeometry(add, add, 900 + add, 500 + add)
        self.setWindowTitle('Maps_To_Tomopy')
        self.show()

    #### TEST


    def tab1manual(self):
        '''
        tab1manual
        Displays instructions for how to use the manual hotspot alignment tool
        in the message box.
        '''
        print self.tab_widget.currentIndex()
        if self.tab_widget.currentIndex() == 1:
            self.lbl.setText('click hotspot, press n to advance frame or press S to skip frame')
        else:
            self.lbl.setText("")

    def externalImageReg(self):
        '''
        For later use. Get aligned data using written code out side of MAPSToTomoPy.
        Name should be imageReg and the function should be align
        '''
        original_path = os.getcwd()
        fileName = QtGui.QFileDialog.getExistingDirectory(self, "Open Extension",
                                                          QtCore.QDir.currentPath())
        fileName = str(fileName)
        sys.path.append(os.path.abspath(fileName))

        import imageReg
        from imageReg import align
        x = imageReg.align()
        print x

        os.chdir(original_path)

    #############################
    ## creating tab

    def createMessageWidget(self):
        '''
        create message widget and returns the group
        Returns
        ---------
        QBoxgroup
              message box group
        '''
        GridStartVal = '2'
        vbox = QtGui.QVBoxLayout()
        hbox = QtGui.QHBoxLayout()
        hbox2 = QtGui.QHBoxLayout()
        self.lbl = QtGui.QLineEdit("Step 1) Open configuration file", self)
        # self.lbl.setText("Starting")
        self.lbl2 = QtGui.QLineEdit()
        self.lbl2.setText(os.getcwd())
        self.directoryButton = QtGui.QPushButton("Change Directory")
        self.directoryButton.clicked.connect(self.changeDirectory)

        hbox.addWidget(QtGui.QLabel("Message"))
        hbox.addWidget(self.lbl)
        hbox2.addWidget(QtGui.QLabel("Set Directory"))
        hbox2.addWidget(self.lbl2)
        hbox2.addWidget(self.directoryButton)
        vbox.addLayout(hbox)
        vbox.addLayout(hbox2)
        messageGroup = QtGui.QGroupBox("Message Box")
        messageGroup.setLayout(vbox)
        return messageGroup

        print self.tab_widget.currentIndex()
        if self.tab_widget.currentIndex() == 1:
            self.lbl.setText("click hotspot, press n (to advance frame) or press",
                             "S (to skip frame)")
        else:
            self.lbl.setText("")

    def createSinoWidget(self):
        '''
        create a sinogram group for sinogram tab.

        Returns
        ---------
        QBoxgroup
              sinogram group
        '''
        self.sino = QSelect2()
        self.sinoView = SinoWidget()

        sinoBox = QtGui.QHBoxLayout()
        sinoBox.addWidget(self.sino)
        sinoBox.addWidget(self.sinoView, 10)
        sinoGroup = QtGui.QGroupBox("")
        sinoGroup.setLayout(sinoBox)

        return sinoGroup

    def createReconWidget(self):
        '''
        create a reconstruction group for reconstruction tab.
        returns reconstruction group

        Returns
        ---------
        QBoxgroup
              reconstruction tap group
        '''
        self.recon = QSelect3()
        self.recon.sld.setVisible(False)
        self.reconView = IView3()
        self.reconView.view.ROI.setVisible(False)

        reconBox = QtGui.QHBoxLayout()
        reconBox.addWidget(self.recon)
        reconBox.addWidget(self.reconView, 10)
        reconGroup = QtGui.QGroupBox("")
        reconGroup.setLayout(reconBox)
        self.reconView.lbl5.setText(str('slice'))

        return reconGroup

    def createProjWidget(self):
        '''
        create a projection group for projection tab.
        returns projection group

        Returns
        ---------
        QBoxgroup
              projection tap group
        '''
        self.projection = QSelect2()
        self.projectionView = pg.ImageView()

        projectionBox = QtGui.QHBoxLayout()
        projectionBox.addWidget(self.projection)
        projectionBox.addWidget(self.projectionView, 10)
        projectionGroup = QtGui.QGroupBox("")
        projectionGroup.setLayout(projectionBox)

        return projectionGroup

    def createSaveHotspotWidget(self):
        '''
        create a saving hotspot position group.
        returns the group

        Returns
        ---------
        QBoxgroup
              a group for saving and aliging hotspots.
        '''
        self.projViewControl = QSelect4()
        self.projView = IView3()
        self.boxSize = 20

        projViewBox = QtGui.QHBoxLayout()
        projViewBox.addWidget(self.projViewControl)
        projViewBox.addWidget(self.projView, 10)
        projViewGroup = QtGui.QGroupBox("")
        projViewGroup.setLayout(projViewBox)
        return projViewGroup

    def createImageProcessWidget(self):
        '''
        create an Image process group.
        returns the group
        Returns
        ---------
        QBoxgroup
              a group for Image processing.
        '''
        self.imgProcessControl = imageProcess()
        self.imgProcess = IView3()

        imgProcessBox = QtGui.QHBoxLayout()
        imgProcessBox.addWidget(self.imgProcessControl)
        imgProcessBox.addWidget(self.imgProcess, 10)
        imgProcessGroup = QtGui.QGroupBox("")
        imgProcessGroup.setLayout(imgProcessBox)
        return imgProcessGroup

    #############################
    ## Alignment

    def changeDirectory(self):
        '''
        change directory function so the path is changed to desired directory.
        folderName is the name of the folder that you would work on.

        '''
        folderName = QtGui.QFileDialog.getExistingDirectory(self, "Change Directory",
                                                            QtCore.QDir.currentPath())
        os.chdir(str(folderName))
        self.lbl2.setText(folderName)

    # ! Center of Mass

    def centerOfMassWindow(self):
        '''
        Creates the window for alignment with center of mass
        self.comer: window
        self.comer.num: channel name (scalar name)
        '''
        self.comer = QSelect3()
        self.comer.setWindowTitle("Center of Mass window")
        self.comer.numb = len(self.channelname)
        for j in arange(self.comer.numb):
            self.comer.combo.addItem(self.channelname[j])
        self.comer.btn.setText("Center of Mass")
        self.comer.method.setVisible(False)
        self.comer.save.setVisible(True)
        self.comer.save.setText("Restore")
        self.comer.btn.clicked.connect(self.runCenterOfMass)
        self.comer.save.clicked.connect(self.restore)
        self.comer.show()

    def runCenterOfMass(self):
        '''
        find center of mass with self.centerOfMass and fit the curve with self.fitCenterOfMass
        '''
        self.centerOfMass()
        self.fitCenterOfMass(x=self.theta)
        self.lbl.setText("Center of Mass: " + str(self.p1[2]))

    #### devel
    def runCenterOfMass2(self):
        '''
        second version of runCenterOfMass
        self.com: center of mass vector
        self.comelem: the element chosen for center of mass
        '''
        self.com = zeros(self.projections)
        temp = zeros(self.data.shape[3])
        temp2 = zeros(self.data.shape[3])
        self.comelem = self.sino.combo.currentIndex()
        for i in arange(self.projections):
            temp = sum(self.data[self.comelem, i,
                       self.sino.sld.value() - self.thickness / 2:self.sino.sld.value() + self.thickness / 2,
                       :] - self.data[self.comelem, i, :10, :10].mean(), axis=0)
            # temp=sum(self.data[self.comelem,i,:,:]-1, axis=0)
            numb2 = sum(temp)
            for j in arange(self.data.shape[3]):
                temp2[j] = temp[j] * j
            numb = float(sum(temp2)) / numb2
            self.com[i] = numb
        self.fitCenterOfMass(x=self.theta)
        self.lbl.setText("Center of Mass: " + str(self.p1[2]))
        self.alignCenterOfMass()
        self.sinogram()

    #### devel

    def centerOfMass(self):
        '''
        self.com: center of mass vector
        self.comelem: the element chosen for center of mass
        '''
        self.com = zeros(self.projections)
        temp = zeros(self.data.shape[3])
        temp2 = zeros(self.data.shape[3])
        self.comelem = self.comer.combo.currentIndex()
        for i in arange(self.projections):
            temp = sum(self.data[self.comelem, i, :, :] - self.data[self.comelem, i, :10, :10].mean(), axis=0)
            # temp=sum(self.data[self.comelem,i,:,:]-1, axis=0)
            numb2 = sum(temp)
            for j in arange(self.data.shape[3]):
                temp2[j] = temp[j] * j
            numb = float(sum(temp2)) / numb2
            self.com[i] = numb

    def fitCenterOfMass(self, ang):
        '''
        Find a position difference between center of mass of first projection
        and center of other projections.
        If we use this difference, centers will be aligned in a straigh line

        Parameters
        -----------
        ang: ndarray
              angle

        Variables
        ------------
        self.centerOfMassDiff: ndarray
              Difference of center of mass of first projections and center
              of other projections
        self.com: ndarray
              The position of center of mass
        '''
        self.centerOfMassDiff = self.com[0] - self.com

    def fitCenterOfMass(self, x):
        self.fitfunc = lambda p, x: p[0] * sin(2 * pi / 360 * (x - p[1])) + p[2]
        self.errfunc = lambda p, x, y: self.fitfunc(p, x) - y
        p0 = [100, 100, 100]
        self.p1, success = optimize.leastsq(self.errfunc, p0[:], args=(x, self.com))
        self.centerOfMassDiff = self.fitfunc(self.p1, x) - self.com
        print "here", self.centerOfMassDiff

    def fitCenterOfMass2(self, x):
        '''
        Find a position difference between center of mass of first projection
        and center of other projections.
        If we use this difference, centers will form a sine curve

        Parameters
        -----------
        ang: ndarray
              angle

        Variables
        ------------
        self.centerOfMassDiff: ndarray
              Difference of center of mass of first projections and center
              of other projections
        self.com: ndarray
              The position of center of mass
        '''
        fitfunc = lambda p, x: p[0] * sin(2 * pi / 360 * (x - p[1])) + self.p1[2]
        errfunc = lambda p, x, y: fitfunc(p, x) - y
        p0 = [100, 100]
        p2, success = optimize.leastsq(errfunc, p0[:], args=(x, self.com))
        self.centerOfMassDiff = fitfunc(p2, x) - self.com

    def alignCenterOfMass(self):
        '''
        Align center of Mass

        Variables
        ------------
        self.centerOfMassDiff: ndarray
              Difference of center of mass of first projections and center
              of other projections
        self.projections: number
              number of projections
        self.xshift: ndarray
              shift in x direction
        self.data: ndarray
              4D data [element,projections,y,x]
        '''
        for i in arange(self.projections):
            self.xshift[i] += int(self.centerOfMassDiff[i])
            self.data[:, i, :, :] = np.roll(self.data[:, i, :, :], int(round(self.xshift[i])), axis=2)
        self.lbl.setText("Alignment has been completed")

    def alignCenterOfMass2(self):
        '''
        Align center of Mass

        Variables
        ------------
        self.centerOfMassDiff: ndarray
              Difference of center of mass of first projections and center
              of other projections
        self.projections: number
              number of projections
        self.xshift: ndarray
              shift in x direction
        self.data: ndarray
              4D data [element,projections,y,x]
        '''

        j = 0

        for i in self.hotspotProj:
            self.xshift[i] += int(self.centerOfMassDiff[j])

            self.data[:, i, :, :] = np.roll(self.data[:, i, :, :], int(round(self.xshift[i])), axis=2)
            j += 1
        self.lbl.setText("Alignment has been completed")

    def CrossCorrelation_test(self):

        self.datacopy = zeros(self.data.shape)
        self.datacopy[...] = self.data[...]
        self.data[np.isnan(self.data)] = 1
        self.xcor = AlignWindow()
        self.xcor.setWindowTitle("CrossCorrelation Window")
        self.xcor.numb = len(self.channelname)
        for j in arange(self.xcor.numb):
            self.xcor.combo.addItem(self.channelname[j])
        self.xcor.btn.setText("Cross Correlation")
        self.xcor.btn2.setText("Restore")
        self.xcor.btn.clicked.connect(self.xCor)
        self.xcor.btn2.clicked.connect(self.restore)
        self.xcor.method.setVisible(False)
        self.xcor.show()

    def restore(self):
        self.xshift = zeros(self.projections, int)
        self.yshift = zeros(self.projections, int)
        self.data = zeros(self.oldData.shape)
        self.data[...] = self.oldData[...]
        self.projView.view.data = self.data[self.projViewElement, :, :, :]

    def prexCor(self):
        try:
            self.xcor.savedir = QtGui.QFileDialog.getSaveFileName()
            if not self.xcor.savedir[0]:
                raise IndexError
            self.xcor.savedir = self.xcor.savedir[0]
            self.xCor()
        except IndexError:
            print "type the header name"

    def match_window(self):
        self.matcher = AlignWindow()
        self.matcher.setWindowTitle("Match template window")
        self.matcher.numb = len(self.channelname)
        for j in arange(self.matcher.numb):
            self.matcher.combo.addItem(self.channelname[j])
        self.matcher.btn.setText("Match Template")
        self.matcher.btn2.setText("Restore")
        self.matcher.btn.clicked.connect(self.match)
        self.matcher.btn2.clicked.connect(self.restore)
        self.xcor.method.setVisible(False)
        self.matcher.show()

    def match(self):
        self.matchElem = self.matcher.combo.currentIndex()
        for i in arange(self.projections - 1):
            img = self.data[self.matchElem, i, :, :]
            img1 = ones([img.shape[0] * 2, img.shape[1] * 2]) * self.data[self.matchElem, i, :10, :10].mean()
            img1[img.shape[0] / 2:img.shape[0] * 3 / 2, img.shape[1] / 2:img.shape[1] * 3 / 2] = img
            img2 = self.data[self.matchElem, i + 1, :, :]
            result = match_template(img1, img2)
            result = np.where(result == np.max(result))
            self.yshift[i + 1] += result[0][0] - img.shape[0] / 2
            self.xshift[i + 1] += result[1][0] - img.shape[1] / 2
            print self.xshift[i + 1], self.yshift[i + 1]
            self.data[:, i + 1, :, :] = np.roll(self.data[:, i + 1, :, :], self.xshift[i + 1], axis=2)
            self.data[:, i + 1, :, :] = np.roll(self.data[:, i + 1, :, :], self.yshift[i + 1], axis=1)
        self.alignmentDone()

    def xCor(self):
        ##            self.xcor.savedir="texting"
        ##            f=open(self.xcor.savedir+".txt",'w')
        ##            onlyfilenameIndex=self.fileNames[0].rfind("/")
        ##            f.write(self.fileNames[0][onlyfilenameIndex+1:]+" \n")
        ##            f.write("0 \n")
        self.xcorElement = self.xcor.combo.currentIndex()
        for i in arange(self.projections - 1):
            # onlyfilenameIndex=self.fileNames[i+1].rfind("/")
            img1 = self.data[self.xcorElement, i, :, :]
            img2 = self.data[self.xcorElement, i + 1, :, :]

            self.t0, self.t1 = self.xcorrelate(img1, img2)
            self.data[:, i + 1, :, :] = np.roll(self.data[:, i + 1, :, :], self.t0, axis=1)
            self.data[:, i + 1, :, :] = np.roll(self.data[:, i + 1, :, :], self.t1, axis=2)
            self.xshift[i + 1] += self.t1
            self.yshift[i + 1] += self.t0
        self.alignmentDone()

    ##                  self.data[:,i+1,:,:]=np.roll(self.data[:,i+1,:,:],shift,axis=2)
    ##                  f.write(self.fileNames[i+1][onlyfilenameIndex+1:]+" \n")
    ##                  f.write(str(shift)+ "\n")
    ##                  print i
    ##            f.close()
    def alignFromText(self):
        '''
        align by reading text file that saved prior image registration
        alignment info is saved in following format: name of the file, xshift, yshift
        by locating where the comma(,) is we can extract information:
        name of the file(string before first comma),
        yshift(string after first comma before second comma),
        xshift(string after second comma)

        '''
        try:
            fileName = QtGui.QFileDialog.getOpenFileName(self, "Open File",
                                                         QtCore.QDir.currentPath(), "TXT (*.txt)")
            ##### for future reference "All File (*);;CSV (*.csv *.CSV)"

            f = open(fileName, 'r')
            read = f.readlines()
            self.datacopy = zeros(self.data.shape)
            self.datacopy[...] = self.data[...]
            self.data[np.isnan(self.data)] = 1
            for i in arange(self.projections):
                onlyfilenameIndex = self.selectedFiles[i].rfind("/")
                # onlyfilename =
                for j in arange(len(read)):
                    if string.find(read[j], self.selectedFiles[i][onlyfilenameIndex + 1:]) != -1:
                        secondcol = read[j].rfind(",")  ## find second ,
                        firstcol = read[j][:secondcol].rfind(",")
                        self.yshift[i] += int(float(read[j][secondcol + 1:-1]))
                        self.xshift[i] += int(float(read[j][firstcol + 1:secondcol]))
                        self.data[:, i, :, :] = np.roll(self.data[:, i, :, :], self.xshift[i], axis=2)
                        self.data[:, i, :, :] = np.roll(self.data[:, i, :, :], self.yshift[i], axis=1)
                    if string.find(read[j], "rotation axis") != -1:
                        commapos = read[j].rfind(",")
                        self.p1[2] = float(read[j][commapos + 1:-1])

            f.close()

            self.lbl.setText("Alignment using values from Text has been completed")
            self.updateImages()
        except IOError:
            print "choose file please"

    def alignFromText2(self):
        '''
        align by reading text file that saved prior image registration
        alignment info is saved in following format: name of the file, xshift, yshift
        by locating where the comma(,) is we can extract information:
        name of the file(string before first comma),
        yshift(string after first comma before second comma),
        xshift(string after second comma)

        '''
        try:
            fileName = QtGui.QFileDialog.getOpenFileName(self, "Open File",
                                                         QtCore.QDir.currentPath(), "TXT (*.txt)")
            ##### for future reference "All File (*);;CSV (*.csv *.CSV)"

            f = open(fileName, 'r')
            read = f.readlines()
            self.datacopy = zeros(self.data.shape)
            self.datacopy[...] = self.data[...]
            self.data[np.isnan(self.data)] = 1
            for i in arange(self.projections):
                j = i + 1
                secondcol = read[j].rfind(",")
                firstcol = read[j][:secondcol].rfind(",")
                self.yshift[i] += int(float(read[j][secondcol + 1:-1]))
                self.xshift[i] += int(float(read[j][firstcol + 1:secondcol]))
                self.data[:, i, :, :] = np.roll(self.data[:, i, :, :], self.xshift[i], axis=2)
                self.data[:, i, :, :] = np.roll(self.data[:, i, :, :], self.yshift[i], axis=1)

            f.close()

            self.lbl.setText("Alignment using values from Text has been completed")
            self.updateImages()
        except IOError:
            print "choose file please"

    def saveAlignToText(self):

        try:
            self.alignFileName = QtGui.QFileDialog.getSaveFileName()
            if string.rfind(str(self.alignFileName), ".txt") == -1:
                self.alignFileName = str(self.alignFileName) + ".txt"
            print str(self.alignFileName)
            f = open(self.alignFileName, "w")
            f.writelines("rotation axis, " + str(self.p1[2]) + "\n")
            for i in arange(self.projections):
                onlyfilenameIndex = self.selectedFiles[i].rfind("/")
                print self.selectedFiles[i]
                f.writelines(self.selectedFiles[i][onlyfilenameIndex + 1:] + ", " + str(self.xshift[i]) + ", " + str(
                    self.yshift[i]) + "\n")

            f.close()
        except IOError:
            print "choose file please"

    # ==========================
    def xcorrelate(self, a, b):
        fa = spf.fft2(a)
        fb = spf.fft2(b)

        shape = a.shape
        c = abs(spf.ifft2(fa * fb.conjugate()))
        t0, t1 = np.unravel_index(np.argmax(c), a.shape)
        if t0 > shape[0] // 2:
            t0 -= shape[0]
        if t1 > shape[1] // 2:
            t1 -= shape[1]

        return t0, t1

    def phasecorrelate(self, a, b):
        fa = spf.fft2(a)
        fb = spf.fft2(b)

        shape = a.shape
        c = abs(spf.ifft2(fa * fb.conjugate() / (abs(fa) * abs(fb))))
        t0, t1 = np.unravel_index(np.argmax(c), a.shape)
        if t0 > shape[0] // 2:
            t0 -= shape[0]
        if t1 > shape[1] // 2:
            t1 -= shape[1]
        return t0, t1

    def edgegauss(self, imagey, sigma=4):
        '''
        edge gauss for better cross correlation
        '''
        image = zeros(imagey.shape)
        image[...] = imagey[...]
        nx = image.shape[1]
        ny = image.shape[0]

        n_sigma = -log(10 ** -6)
        n_roll = max(int(1 + sigma * n_sigma), 2)
        exparg = float32(arange(n_roll) / float(sigma))
        rolloff = float32(1) - exp(-0.5 * exparg * exparg)

        ## Top edge

        xstart = 0
        xstop = nx
        iy = 0

        for i_roll in arange(n_roll):
            image[iy, xstart:xstop] = image[iy, xstart:xstop] * rolloff[iy]
            xstart = min(xstart + 1, nx / 2 - 1)
            xstop = max(xstop - 1, nx / 2)
            iy = min(iy + 1, ny - 1)

        ## Bottom edge

        xstart = 0
        xstop = nx
        iy = ny - 1

        for i_roll in arange(n_roll):
            image[iy, xstart:xstop] = image[iy, xstart:xstop] * rolloff[ny - 1 - iy]
            xstart = min(xstart + 1, nx / 2 - 1)
            xstop = max(xstop - 1, nx / 2)
            iy = max(iy - 1, 0)

        ## Left edge

        ystart = 1
        ystop = ny - 1
        ix = 0

        for i_roll in arange(n_roll):
            image[ystart:ystop, ix] = image[ystart:ystop, ix] * rolloff[ix]
            ystart = min(ystart + 1, ny / 2 - 1)
            ystop = max(ystop - 1, ny / 2)
            ix = min(ix + 1, nx - 1)

        ## Right edge

        ystart = 1
        ystop = ny - 1
        ix = nx - 1

        for i_roll in arange(n_roll):
            image[ystart:ystop, ix] = image[ystart:ystop, ix] * rolloff[nx - 1 - ix]
            ystart = min(ystart + 1, ny / 2 - 1)
            ystop = max(ystop - 1, ny / 2)
            ix = max(ix - 1, 0)

        return image

    # ==========================

    def showSaveHotSpotPos(self):
        self.tab_widget.removeTab(1)
        self.tab_widget.insertTab(1, self.createSaveHotspotWidget(), unicode("Hotspot"))
        self.projViewControl.numb = len(self.channelname)
        for j in arange(self.projViewControl.numb):
            self.projViewControl.combo.addItem(self.channelname[j])

        for k in arange(self.projections):
            self.projViewControl.combo3.addItem(str(k + 1))

        self.projViewControl.combo3.setVisible(False)
        self.projViewControl.combo.currentIndexChanged.connect(self.saveHotSpotPos)
        self.projViewControl.combo3.currentIndexChanged.connect(self.hotSpotProjChanged)
        self.projViewControl.sld.setValue(20)
        # self.projViewControl.sld.setRange(0, self.x / 2)
        self.projViewControl.lcd.display(20)
        self.projViewControl.sld.valueChanged.connect(self.projViewControl.lcd.display)
        self.projViewControl.sld.valueChanged.connect(self.boxSizeChange)
        self.projViewControl.btn.clicked.connect(self.alignHotSpotPos3)
        self.projViewControl.btn2.clicked.connect(self.alignHotSpotPos4)
        self.projViewControl.btn3.clicked.connect(self.alignHotSpotY)
        self.projViewControl.btn4.clicked.connect(self.clearHotSpotData)
        self.projViewControl.combo2.currentIndexChanged.connect(self.hotSpotSetChanged)
        self.projViewControl.show()

        self.projView.view.hotSpotNumb = 0
        self.projView.sld.setRange(0, self.projections - 1)
        self.projView.sld.valueChanged.connect(self.hotSpotLCDValueChanged)
        self.projView.sld.valueChanged.connect(self.hotSpotProjChanged)
        self.testtest = pg.ImageView()

    #########

    def clearHotSpotData(self):
        self.projView.view.posMat[...] = zeros_like(self.projView.view.posMat)

    def hotSpotLCDValueChanged(self):
        index = self.projView.sld.value()
        angle = round(self.theta[index])
        self.projView.lcd.display(angle)
        self.imgProcess.lcd.display(angle)
        self.imgProcess.sld.setValue(index)

    def hotSpotProjChanged(self):
        self.file_name_update(self.projView)
        self.projView.view.hotSpotNumb = self.projView.sld.value()
        self.projView.view.projView.setImage(self.data[self.projViewElement, self.projView.view.hotSpotNumb, :, :])
        self.imgProcess.view.projView.setImage(self.imgProcessImg)

    #########

    def boxSizeChange(self):
        self.boxSize = self.projViewControl.sld.value() / 2 * 2
        self.projView.view.ROI.setPos([int(round(self.projView.view.projView.iniX)) - self.boxSize / 2,
                                       -int(round(self.projView.view.projView.iniY)) - self.boxSize / 2])
        self.projView.view.ROI.setSize([self.boxSize, self.boxSize])
        self.projView.view.xSize = self.boxSize
        self.projView.view.ySize = self.boxSize

    def hotSpotSetChanged(self):
        self.projView.view.hotSpotSetNumb = self.projViewControl.combo2.currentIndex()

    def nextHotSpotPos(self):
        # self.projView.hotSpotNumb=self.projViewControl.sld.value()
        self.projView.view.projView.setImage(self.data[self.projViewElement, self.projView.view.hotSpotNumb, :, :])

    def saveHotSpotPos(self):
        # self.projView.view.hotSpotNumb=0
        self.projViewElement = self.projViewControl.combo.currentIndex()
        self.projView.view.data = self.data[self.projViewElement, :, :, :]
        self.projView.view.posMat = zeros(
            [5, self.data.shape[1], 2])  ## Later change 5 -> how many data are in the combo box.
        self.projView.view.projView.setImage(self.data[self.projViewElement, 0, :, :])

    def alignHotSpotY(self):
        '''
        loads variables for aligning hotspots in y direction only
        '''
        self.boxSize2 = self.boxSize / 2
        self.xPos = zeros(self.projections)
        self.yPos = zeros(self.projections)
        self.boxPos = zeros([self.projections, self.boxSize, self.boxSize])
        hotSpotSet = self.projViewControl.combo2.currentIndex()
        for i in arange(self.projections):

            self.yPos[i] = int(round(self.projView.view.posMat[hotSpotSet, i, 0]))
            self.xPos[i] = int(round(self.projView.view.posMat[hotSpotSet, i, 1]))

            if self.xPos[i] != 0 and self.yPos[i] != 0:
                if self.yPos[i] < self.boxSize2:
                    self.yPos[i] = self.boxSize2
                if self.yPos[i] > self.projView.view.data.shape[1] - self.boxSize2:
                    self.yPos[i] = self.projView.view.data.shape[1] - self.boxSize2
                if self.xPos[i] < self.boxSize2:
                    self.xPos[i] = self.boxSize2
                if self.xPos[i] > self.projView.view.data.shape[2] - self.boxSize2:
                    self.xPos[i] = self.projView.view.data.shape[2] - self.boxSize2
                # self.boxPos[i,:,:]=self.projView.data[i,self.xPos[i]-self.boxSize2:self.xPos[i]+self.boxSize2,self.yPos[i]-self.boxSize2:self.yPos[i]+self.boxSize2]
                self.boxPos[i, :, :] = self.projView.view.data[i,
                                       self.yPos[i] - self.boxSize2:self.yPos[i] + self.boxSize2,
                                       self.xPos[i] - self.boxSize2:self.xPos[i] + self.boxSize2]
        print self.boxPos.shape
        print self.xPos, self.yPos

        self.alignHotSpotY_next()

    def alignHotSpotY_next(self):
        '''
        save the position of hotspots
        and align by only in y directions.
        '''
        self.hotSpotX = zeros(self.projections)
        self.hotSpotY = zeros(self.projections)
        self.newBoxPos = zeros(self.boxPos.shape)
        self.newBoxPos[...] = self.boxPos[...]
        ### need to change x and y's
        firstPosOfHotSpot = 0
        add = 1
        for i in arange(self.projections):
            if self.xPos[i] == 0 and self.yPos[i] == 0:
                firstPosOfHotSpot += add
            if self.xPos[i] != 0 or self.yPos[i] != 0:
                print self.xPos[i], self.yPos[i]
                img = self.boxPos[i, :, :]
                print img.shape
                a, x, y, b, c = self.fitgaussian(img)
                self.hotSpotY[i] = x
                self.hotSpotX[i] = y
                yshift = int(round(self.boxSize2 - self.hotSpotY[i]))
                xshift = int(round(self.boxSize2 - self.hotSpotX[i]))
                self.newBoxPos[i, :, :] = np.roll(self.newBoxPos[i, :, :], xshift, axis=1)
                self.newBoxPos[i, :, :] = np.roll(self.newBoxPos[i, :, :], yshift, axis=0)
                ##                  subplot(211)
                ##                  plt.imshow(self.boxPos[i,:,:])
                ##                  subplot(212)
                ##                  plt.imshow(self.newBoxPos[i,:,:])
                ##                  show()
                add = 0

        add2 = 0
        for j in arange(self.projections):

            if self.xPos[j] != 0 and self.yPos[j] != 0:
                yyshift = int(round(self.boxSize2 - self.hotSpotY[j] - self.yPos[j] + self.yPos[firstPosOfHotSpot]))

                print yyshift
                self.data[:, j, :, :] = np.roll(self.data[:, j, :, :],
                                                yyshift, axis=1)
            ##                        for l in arange(self.data.shape[0]):
            ##                              if yyshift>0:
            ##                                    self.data[l,j,:yyshift,:]=ones(self.data[l,j,:yyshift,:].shape)*self.data[l,j,:yyshift,:].mean()/2
            ##                              if yyshift<0:
            ##                                    self.data[l,j,yyshift:,:]=ones(self.data[l,j,yyshift:,:].shape)*self.data[l,j,-yyshift:,:].mean()/2
            ##                              if xxshift>0:
            ##                                    self.data[l,j,:,:xxshift]=ones(self.data[l,j,:,:xxshift].shape)*self.data[l,j,:xxshift,:].mean()/2
            ##                              if xxshift<0:
            ##                                    self.data[l,j,:,xxshift:]=ones(self.data[l,j,:,xxshift:].shape)*self.data[l,j,-xxshift:,:].mean()/2

            if self.yPos[j] == 0:
                yyshift = 0

            self.yshift[j] += yyshift

        print "align done"

    def alignHotSpotPos1(self):
        '''
        save the position of hotspots
        and align by both x and y directions.
        '''
        for i in arange(self.projections - 1):
            print "shifted"

            self.data[:, i + 1, :, :] = np.roll(self.data[:, i + 1, :, :], int(
                round(self.projView.view.posMat[0, 0] - self.projView.view.posMat[i + 1, 0])), axis=2)
            self.data[:, i + 1, :, :] = np.roll(self.data[:, i + 1, :, :], int(
                round(self.projView.view.posMat[0, 1] - self.projView.view.posMat[i + 1, 1])), axis=1)

    def alignHotSpotPos2(self):
        '''
        save the position of hotspots
        and align by both x and y directions.
        '''
        for i in arange(self.projections - 1):
            self.data[:, i + 1, :, :] = np.roll(self.data[:, i + 1, :, :], int(
                round(self.projView.view.posMat[0, 1] - self.projView.view.posMat[i + 1, 1])), axis=1)
        x = self.theta
        self.fitfunc = lambda p, x: p[0] * sin(2 * pi / 360 * (x - p[1])) + p[2]
        self.errfunc = lambda p, x, y: self.fitfunc(p, x) - y
        p0 = [100, 100, 100]
        self.p1, success = optimize.leastsq(self.errfunc, p0[:], args=(x, self.projView.view.posMat[:, 0]))
        self.hotSpotPosDiff = self.fitfunc(self.p1, x) - self.projView.view.posMat[:, 0]

        for i in arange(self.projections):
            self.xshift[i] += int(self.hotSpotPosDiff[i])
            self.data[:, i, :, :] = np.roll(self.data[:, i, :, :], self.xshift[i], axis=2)
        self.lbl.setText("Alignment has been completed")

    def alignHotSpotPos3(self):
        '''
        save the position of hotspots
        and align by both x and y directions (self.alignHotSpotPos3_3)
        '''
        # self.projView.data2=self.data[7,:,:,:]
        self.boxSize2 = self.boxSize / 2
        self.xPos = zeros(self.projections)
        self.yPos = zeros(self.projections)
        self.boxPos = zeros([self.projections, self.boxSize, self.boxSize])
        hotSpotSet = self.projViewControl.combo2.currentIndex()
        for i in arange(self.projections):

            self.yPos[i] = int(round(self.projView.view.posMat[hotSpotSet, i, 0]))
            self.xPos[i] = int(round(self.projView.view.posMat[hotSpotSet, i, 1]))

            if self.xPos[i] != 0 and self.yPos[i] != 0:
                if self.yPos[i] < self.boxSize2:
                    self.yPos[i] = self.boxSize2
                if self.yPos[i] > self.projView.view.data.shape[1] - self.boxSize2:
                    self.yPos[i] = self.projView.view.data.shape[1] - self.boxSize2
                if self.xPos[i] < self.boxSize2:
                    self.xPos[i] = self.boxSize2
                if self.xPos[i] > self.projView.view.data.shape[2] - self.boxSize2:
                    self.xPos[i] = self.projView.view.data.shape[2] - self.boxSize2
                # self.boxPos[i,:,:]=self.projView.data[i,self.xPos[i]-self.boxSize2:self.xPos[i]+self.boxSize2,self.yPos[i]-self.boxSize2:self.yPos[i]+self.boxSize2]
                self.boxPos[i, :, :] = self.projView.view.data[i,
                                       self.yPos[i] - self.boxSize2:self.yPos[i] + self.boxSize2,
                                       self.xPos[i] - self.boxSize2:self.xPos[i] + self.boxSize2]
        print self.boxPos.shape
        print "x", self.xPos
        print "y", self.yPos

        ##            for i in arange(self.projections):
        ##                  j=Image.fromarray(self.boxPos[i,:,:].astype(np.float32))
        ##
        ##                  j.save("/Users/youngpyohong/Documents/Work/Python/2dfit/"+str(i)+".tif")

        self.alignHotSpotPos3_3()
        print "hotspot done"

    def alignHotSpotPos4(self):
        '''
        save the position of hotspots
        and align by both x and y directions (self.alignHotSpotPos3_4)
        '''
        # self.projView.data2=self.data[7,:,:,:]
        self.boxSize2 = self.boxSize / 2
        self.xPos = zeros(self.projections)
        self.yPos = zeros(self.projections)
        self.boxPos = zeros([self.projections, self.boxSize, self.boxSize])
        hotSpotSet = self.projViewControl.combo2.currentIndex()
        for i in arange(self.projections):

            self.yPos[i] = int(round(self.projView.view.posMat[hotSpotSet, i, 0]))
            self.xPos[i] = int(round(self.projView.view.posMat[hotSpotSet, i, 1]))

            if self.xPos[i] != 0 and self.yPos[i] != 0:
                if self.yPos[i] < self.boxSize2:
                    self.yPos[i] = self.boxSize2
                if self.yPos[i] > self.projView.view.data.shape[1] - self.boxSize2:
                    self.yPos[i] = self.projView.view.data.shape[1] - self.boxSize2
                if self.xPos[i] < self.boxSize2:
                    self.xPos[i] = self.boxSize2
                if self.xPos[i] > self.projView.view.data.shape[2] - self.boxSize2:
                    self.xPos[i] = self.projView.view.data.shape[2] - self.boxSize2
                # self.boxPos[i,:,:]=self.projView.data[i,self.xPos[i]-self.boxSize2:self.xPos[i]+self.boxSize2,self.yPos[i]-self.boxSize2:self.yPos[i]+self.boxSize2]
                self.boxPos[i, :, :] = self.projView.view.data[i,
                                       self.yPos[i] - self.boxSize2:self.yPos[i] + self.boxSize2,
                                       self.xPos[i] - self.boxSize2:self.xPos[i] + self.boxSize2]
        print self.boxPos.shape
        print self.xPos, self.yPos

        ##            for i in arange(self.projections):
        ##                  j=Image.fromarray(self.boxPos[i,:,:].astype(np.float32))
        ##
        ##                  j.save("/Users/youngpyohong/Documents/Work/Python/2dfit/"+str(i)+".tif")

        self.alignHotSpotPos3_4()
        print "hotspot done"

    def alignHotSpotPos3_3(self):
        '''
        align hotspots by fixing hotspots in one position
        '''
        self.hotSpotX = zeros(self.projections)
        self.hotSpotY = zeros(self.projections)
        self.newBoxPos = zeros(self.boxPos.shape)
        self.newBoxPos[...] = self.boxPos[...]
        ### need to change x and y's
        firstPosOfHotSpot = 0
        add = 1
        for i in arange(self.projections):
            if self.xPos[i] == 0 and self.yPos[i] == 0:
                firstPosOfHotSpot += add
            if self.xPos[i] != 0 or self.yPos[i] != 0:
                print self.xPos[i], self.yPos[i]
                img = self.boxPos[i, :, :]
                print img.shape
                a, x, y, b, c = self.fitgaussian(img)
                self.hotSpotY[i] = x
                self.hotSpotX[i] = y
                yshift = int(round(self.boxSize2 - self.hotSpotY[i]))
                xshift = int(round(self.boxSize2 - self.hotSpotX[i]))
                self.newBoxPos[i, :, :] = np.roll(self.newBoxPos[i, :, :], xshift, axis=1)
                self.newBoxPos[i, :, :] = np.roll(self.newBoxPos[i, :, :], yshift, axis=0)
                ##                  subplot(211)
                ##                  plt.imshow(self.boxPos[i,:,:])
                ##                  subplot(212)
                ##                  plt.imshow(self.newBoxPos[i,:,:])
                ##                  show()
                add = 0

        add2 = 0
        for j in arange(self.projections):

            if self.xPos[j] != 0 and self.yPos[j] != 0:
                yyshift = int(round(self.boxSize2 - self.hotSpotY[j] - self.yPos[j] + self.yPos[firstPosOfHotSpot]))
                xxshift = int(round(self.boxSize2 - self.hotSpotX[j] - self.xPos[j] + self.xPos[firstPosOfHotSpot]))
                print xxshift, yyshift
                self.data[:, j, :, :] = np.roll(np.roll(self.data[:, j, :, :], xxshift, axis=2),
                                                yyshift, axis=1)
            ##                        for l in arange(self.data.shape[0]):
            ##                              if yyshift>0:
            ##                                    self.data[l,j,:yyshift,:]=ones(self.data[l,j,:yyshift,:].shape)*self.data[l,j,:yyshift,:].mean()/2
            ##                              if yyshift<0:
            ##                                    self.data[l,j,yyshift:,:]=ones(self.data[l,j,yyshift:,:].shape)*self.data[l,j,-yyshift:,:].mean()/2
            ##                              if xxshift>0:
            ##                                    self.data[l,j,:,:xxshift]=ones(self.data[l,j,:,:xxshift].shape)*self.data[l,j,:xxshift,:].mean()/2
            ##                              if xxshift<0:
            ##                                    self.data[l,j,:,xxshift:]=ones(self.data[l,j,:,xxshift:].shape)*self.data[l,j,-xxshift:,:].mean()/2
            if self.xPos[j] == 0:
                xxshift = 0
            if self.yPos[j] == 0:
                yyshift = 0

            self.xshift[j] += xxshift
            self.yshift[j] += yyshift

        self.p1[2] = self.xPos[0]

        print "align done"

    def alignHotSpotPos3_4(self):
        '''
        align hotspots by fixing hotspots by fitting in a sine curve
        '''
        self.hotSpotX = zeros(self.projections)
        self.hotSpotY = zeros(self.projections)
        self.newBoxPos = zeros(self.boxPos.shape)
        self.newBoxPos[...] = self.boxPos[...]
        ### need to change x and y's
        firstPosOfHotSpot = 0
        add = 1
        for i in arange(self.projections):
            if self.xPos[i] == 0 and self.yPos[i] == 0:
                firstPosOfHotSpot += add
            if self.xPos[i] != 0 or self.yPos[i] != 0:
                print self.xPos[i], self.yPos[i]
                img = self.boxPos[i, :, :]
                print img.shape
                a, x, y, b, c = self.fitgaussian(img)
                self.hotSpotY[i] = x
                self.hotSpotX[i] = y
                yshift = int(round(self.boxSize2 - self.hotSpotY[i]))
                xshift = int(round(self.boxSize2 - self.hotSpotX[i]))
                self.newBoxPos[i, :, :] = np.roll(self.newBoxPos[i, :, :], xshift, axis=1)
                self.newBoxPos[i, :, :] = np.roll(self.newBoxPos[i, :, :], yshift, axis=0)
                ##                  subplot(211)
                ##                  plt.imshow(self.boxPos[i,:,:])
                ##                  subplot(212)
                ##                  plt.imshow(self.newBoxPos[i,:,:])
                ##                  show()
                add = 0

        for j in arange(self.projections):

            if self.xPos[j] != 0 and self.yPos[j] != 0:
                yyshift = int(round(self.boxSize2 - self.hotSpotY[j]))
                xxshift = int(round(self.boxSize2 - self.hotSpotX[j]))

            ##                        for l in arange(self.data.shape[0]):
            ##                              if yyshift>0:
            ##                                    self.data[l,j,:yyshift,:]=ones(self.data[l,j,:yyshift,:].shape)*self.data[l,j,:yyshift,:].mean()/2
            ##                              if yyshift<0:
            ##                                    self.data[l,j,yyshift:,:]=ones(self.data[l,j,yyshift:,:].shape)*self.data[l,j,-yyshift:,:].mean()/2
            ##                              if xxshift>0:
            ##                                    self.data[l,j,:,:xxshift]=ones(self.data[l,j,:,:xxshift].shape)*self.data[l,j,:xxshift,:].mean()/2
            ##                              if xxshift<0:
            ##                                    self.data[l,j,:,xxshift:]=ones(self.data[l,j,:,xxshift:].shape)*self.data[l,j,-xxshift:,:].mean()/2
            if self.xPos[j] == 0:
                xxshift = 0
            if self.yPos[j] == 0:
                yyshift = 0

            self.xshift[j] += xxshift
            self.yshift[j] += yyshift

        add2 = 0

        global hotspotXPos, hotspotYPos
        hotspotXPos = zeros(self.projections)
        hotspotYPos = zeros(self.projections)
        for i in arange(self.projections):
            hotspotYPos[i] = int(round(self.yPos[i]))
            hotspotXPos[i] = int(round(self.xPos[i]))
        self.hotspotProj = np.where(hotspotXPos != 0)[0]
        print self.hotspotProj
        ## temp

        ## xfit
        print self.hotspotProj
        global a1, b4
        a1 = self.theta
        b4 = self.hotspotProj
        theta = self.theta[self.hotspotProj]
        print "theta", theta
        self.com = hotspotXPos[self.hotspotProj]
        if self.projViewControl.combo2.currentIndex() == 0:
            self.fitCenterOfMass(x=theta)
        else:
            self.fitCenterOfMass2(x=theta)
        self.alignCenterOfMass2()

        ## yfit
        for i in self.hotspotProj:
            self.yshift[i] += int(hotspotYPos[self.hotspotProj[0]]) - int(hotspotYPos[i])
            self.data[:, i, :, :] = np.roll(self.data[:, i, :, :], self.yshift[i], axis=1)
            print int(hotspotYPos[0]) - int(hotspotYPos[i])

        self.recon.sld.setValue(self.p1[2])
        print "align done"

    # ==========================
    ## This is for Image processing tab
    def showImageProcess(self):
        '''
        loads window for image process
        '''
        self.tab_widget.removeTab(0)
        self.tab_widget.insertTab(0, self.createImageProcessWidget(), unicode("Image Process"))
        self.imgProcessControl.numb = len(self.channelname)
        for j in arange(self.imgProcessControl.numb):
            self.imgProcessControl.combo1.addItem(self.channelname[j])

        for k in arange(self.projections):
            self.imgProcessControl.combo2.addItem(str(k + 1))

        self.imgProcessControl.combo1.currentIndexChanged.connect(self.imgProcessProjShow)
        self.imgProcessControl.combo2.currentIndexChanged.connect(self.imgProcessProjShow)
        self.imgProcessControl.xUpBtn.clicked.connect(self.imgProcessBoxSizeChange)
        self.imgProcessControl.xDownBtn.clicked.connect(self.imgProcessBoxSizeChange)
        self.imgProcessControl.yUpBtn.clicked.connect(self.imgProcessBoxSizeChange)
        self.imgProcessControl.yDownBtn.clicked.connect(self.imgProcessBoxSizeChange)
        self.imgProcessControl.combo2.setVisible(False)
        self.imgProcessControl.bgBtn.clicked.connect(self.ipBg)
        self.imgProcessControl.delHotspotBtn.clicked.connect(self.ipDelHotspot)
        self.imgProcessControl.normalizeBtn.clicked.connect(self.ipNormalize)
        self.imgProcessControl.cutBtn.clicked.connect(self.ipCut)
        self.imgProcessControl.cutBtn.clicked.connect(self.updateReconBounds)
        self.imgProcessControl.gaussian33Btn.clicked.connect(self.gauss33)
        self.imgProcessControl.gaussian33Btn.clicked.connect(self.gauss55)
        self.imgProcessControl.captureBackground.clicked.connect(self.copyBg)
        self.imgProcessControl.setBackground.clicked.connect(self.setBg)
        self.imgProcessControl.deleteProjection.clicked.connect(self.removeFrame)
        self.imgProcessControl.testButton.clicked.connect(self.noise_analysis)
        self.imgProcessControl.shift_img_up.clicked.connect(self.shiftProjectionUp)
        self.imgProcessControl.shift_img_down.clicked.connect(self.shiftProjectionDown)
        self.imgProcessControl.shift_img_left.clicked.connect(self.shiftProjectionLeft)
        self.imgProcessControl.shift_img_right.clicked.connect(self.shiftProjectionRight)
        self.imgProcessControl.shift_all_up.clicked.connect(self.shiftDataUp)
        self.imgProcessControl.shift_all_down.clicked.connect(self.shiftDataDown)
        self.imgProcessControl.shift_all_left.clicked.connect(self.shiftDataLeft)
        self.imgProcessControl.shift_all_right.clicked.connect(self.shiftDataRight)

        self.imgProcess.sld.setRange(0, self.projections - 1)
        self.imgProcess.sld.valueChanged.connect(self.imageProcessLCDValueChanged)
        self.imgProcess.sld.valueChanged.connect(self.imgProcessProjChanged)
        self.testtest = pg.ImageView()

    def updateReconBounds(self):
        # ySize = self.imgProcessControl.ySize
        self.reconView.sld.setRange(0, self.y- 1)
        self.reconView.sld.setValue(0)
        self.reconView.lcd.display(0)

    def shiftProjectionUp(self):
        projection_index = self.imgProcess.sld.value()
        self.data[:,projection_index] = np.roll(self.data[:,projection_index],-1,axis=1)
        self.imgProcessProjChanged()

    def shiftProjectionDown(self):
        projection_index = self.imgProcess.sld.value() 
        self.data[:,projection_index] = np.roll(self.data[:,projection_index],1,axis=1)
        self.imgProcessProjChanged()

    def shiftProjectionLeft(self):
        projection_index = self.imgProcess.sld.value() 
        self.data[:,projection_index] = np.roll(self.data[:,projection_index],-1)
        self.imgProcessProjChanged()

    def shiftProjectionRight(self):
        projection_index = self.imgProcess.sld.value() 
        self.data[:,projection_index] = np.roll(self.data[:,projection_index],1)
        self.imgProcessProjChanged()

    def shiftDataUp(self):
        for i in range(self.projections):
            self.data[:,i] = np.roll(self.data[:,i],-1,axis=1)
        self.imgProcessProjChanged()

    def shiftDataDown(self):
        for i in range(self.projections):
            self.data[:,i] = np.roll(self.data[:,i],1,axis=1)
        self.imgProcessProjChanged()

    def shiftDataLeft(self):
        self.data = np.roll(self.data,-4)
        self.imgProcessProjChanged()

    def shiftDataRight(self):
        self.data = np.roll(self.data,4)
        self.imgProcessProjChanged()

    def imageProcessLCDValueChanged(self):
        index = self.imgProcess.sld.value()
        angle = round(self.theta[index])
        self.imgProcess.lcd.display(angle)
        self.projView.lcd.display(angle)
        self.projView.sld.setValue(index)

    def imgProcessProjChanged(self):
        element = self.imgProcessControl.combo1.currentIndex()
        self.imgProcessImg = self.data[element, self.imgProcess.sld.value(), :, :]
        self.imgProcess.view.projView.setImage(self.imgProcessImg)
        self.file_name_update(self.imgProcess)

    def file_name_update(self, view):
        try:
            view.file_name_title.setText(self.files[view.sld.value()])
        except:
            print 'bad index'

    def imgProcessProjShow(self):
        element = self.imgProcessControl.combo1.currentIndex()
        projection = self.imgProcessControl.combo2.currentIndex()
        self.imgProcessImg = self.data[element, projection, :, :]
        self.imgProcess.view.projView.setImage(self.imgProcessImg)

    def imgProcessBoxSizeChange(self):
        xSize = self.imgProcessControl.xSize / 2 * 2
        ySize = self.imgProcessControl.ySize / 2 * 2
        self.imgProcess.view.ROI.setSize([xSize, ySize])
        self.imgProcess.view.ROI.setPos([int(round(self.imgProcess.view.projView.iniX)) - xSize / 2,
                                        -int(round(self.imgProcess.view.projView.iniY)) - ySize / 2])
        self.imgProcess.view.xSize = xSize
        self.imgProcess.view.ySize = ySize

    def ipBg(self):
        element = self.imgProcessControl.combo1.currentIndex()
        projection =  self.imgProcess.sld.value()
        xSize = self.imgProcessControl.xSize
        ySize = self.imgProcessControl.ySize

        img = self.data[element, projection, int(round(self.imgProcess.view.projView.iniY)) - ySize / 2:int(
            round(self.imgProcess.view.projView.iniY)) + ySize / 2,
              int(round(self.imgProcess.view.projView.iniX)) - xSize / 2:int(
                  round(self.imgProcess.view.projView.iniX)) + xSize / 2]
        self.bg = np.average(img)
        print self.bg

    def copyBg(self):
        element = self.imgProcessControl.combo1.currentIndex()
        projection =  self.imgProcess.sld.value()
        xSize = self.imgProcessControl.xSize
        ySize = self.imgProcessControl.ySize

        self.imgCopy = self.data[element, projection,
                       int(round(self.imgProcess.view.projView.iniY)) - ySize / 2:
                       int(round(self.imgProcess.view.projView.iniY)) + ySize / 2,
                       int(round(self.imgProcess.view.projView.iniX)) - xSize / 2:
                       int(round(self.imgProcess.view.projView.iniX)) + xSize / 2]

        self.meanNoise = np.mean(self.imgCopy)
        self.stdNoise = np.std(self.imgCopy)

        return self.meanNoise, self.stdNoise

    def noise_analysis(self):

        meanNoise , stdNoise = self.copyBg()
        image_copy = self.imgCopy
        flattened = image_copy.reshape(np.size(image_copy))
        noise_generator1 = np.random.normal(meanNoise, stdNoise+0.00001, np.size(flattened))
        noise_generator = np.random.normal(meanNoise, stdNoise+0.00001, np.shape(image_copy))

        figure()
        plt.plot(np.array(np.ones(np.size(flattened), dtype=int)*meanNoise))
        plt.plot(flattened)
        plt.plot(noise_generator1)
        plt.legend(['Average Noise','Noise','Generated Noise'])

        figure()
        plt.imshow(noise_generator, cmap=gray(), interpolation='nearest')
        show()

        print meanNoise, stdNoise

    def setBg(self):
        element = self.imgProcessControl.combo1.currentIndex()
        # projection = self.imgProcessControl.combo2.currentIndex()
        projection = self.imgProcess.sld.value()
        xSize = self.imgProcessControl.xSize
        ySize = self.imgProcessControl.ySize
        frame_boundary = self.data[element, projection,
        int(round(self.imgProcess.view.projView.iniY)) - ySize / 2:
        int(round(self.imgProcess.view.projView.iniY)) + ySize / 2,
        int(round(self.imgProcess.view.projView.iniX)) - xSize / 2:
        int(round(self.imgProcess.view.projView.iniX)) + xSize / 2] > 0
        self.noise_generator = np.random.normal(self.meanNoise, self.stdNoise+0.00001, (ySize,xSize))*frame_boundary

        self.data[element, projection,
        int(round(self.imgProcess.view.projView.iniY)) - ySize / 2:
        int(round(self.imgProcess.view.projView.iniY)) + ySize / 2,
        int(round(self.imgProcess.view.projView.iniX)) - xSize / 2:
        int(round(self.imgProcess.view.projView.iniX)) + xSize / 2] = self.noise_generator
        self.imgProcessImg = self.data[element, projection, :, :]
        self.imgProcess.view.projView.setImage(self.imgProcessImg)

    def removeFrame(self):
        element = self.imgProcessControl.combo1.currentIndex()      #get channel index
        projection = self.imgProcess.sld.value()                    #get projection index
        self.data = np.delete(self.data,projection,1)               #remove one projection from every channel
        self.files = np.delete(self.files,projection,0)               #remove one projection from every channel
        self.theta = np.delete(self.theta,projection,0)               #remove one projection from every channel
        if projection>0:
            self.projections -=1
            projection -=1
        else:
            self.projections -=1
        self.imgProcess.sld.setRange(0, self.projections - 1)       #update slider range
        self.imgProcess.lcd.display(self.theta[projection])
        self.projView.sld.setRange(0, self.projections - 1)
        self.projView.lcd.display(self.theta[projection])
        self.imgProcess.sld.setValue(projection)
        self.projView.sld.setValue(projection)
        self.imgProcess.view.projView.setImage(self.imgProcessImg)

    def ipDelHotspot(self):
        '''
        delete hotspots by selecting the region and replace with
        desired value
        '''
        element = self.imgProcessControl.combo1.currentIndex()
        projection = self.imgProcessControl.combo2.currentIndex()
        xSize = self.imgProcessControl.xSize
        ySize = self.imgProcessControl.ySize
        img = self.data[element, projection, int(round(self.imgProcess.view.projView.iniY)) - ySize / 2:int(
            round(self.imgProcess.view.projView.iniY)) + ySize / 2,
              int(round(self.imgProcess.view.projView.iniX)) - xSize / 2:int(
                  round(self.imgProcess.view.projView.iniX)) + xSize / 2]
        self.data[element, projection, int(round(self.imgProcess.view.projView.iniY)) - ySize / 2:int(
            round(self.imgProcess.view.projView.iniY)) + ySize / 2,
        int(round(self.imgProcess.view.projView.iniX)) - xSize / 2:int(
            round(self.imgProcess.view.projView.iniX)) + xSize / 2] = ones(img.shape, dtype=img.dtype) * self.bg

        self.imgProcess.view.projView.setImage(self.data[element, projection, :, :])

    def ipNormalize(self):
        '''
        Normalize images
        '''
        element = self.imgProcessControl.combo1.currentIndex()
        projection = self.imgProcessControl.combo2.currentIndex()
        normData = self.data[element, :, :, :]
        for i in arange(normData.shape[0]):
            temp = normData[i, :, :][...]
            tempMax = temp.max()
            tempMin = temp.min()
            temp = (temp - tempMin) / tempMax * 10000
            self.data[element, i, :, :] = temp

    def ipCut(self):
        '''
        cut images
        '''
        element = self.imgProcessControl.combo1.currentIndex()
        projection = self.imgProcessControl.combo2.currentIndex()
        xSize = self.imgProcessControl.xSize
        ySize = self.imgProcessControl.ySize
        print xSize, ySize
        img = self.data[element, projection, int(round(self.imgProcess.view.projView.iniY)) - ySize / 2:\
                int(round(self.imgProcess.view.projView.iniY)) + ySize / 2,\
                int(round(self.imgProcess.view.projView.iniX)) - xSize / 2:\
                int(round(self.imgProcess.view.projView.iniX)) + xSize / 2]
        print img.shape, round(self.imgProcess.view.projView.iniX), round(self.imgProcess.view.projView.iniY)
        self.temp_data = zeros([len(self.channelname), self.projections, img.shape[0], img.shape[1]])
        print self.data.shape
        for i in arange(self.projections):
            for j in arange(len(self.channelname)):
                self.temp_data[j, i, :, :] = self.data[j, i,
                int(round(self.imgProcess.view.projView.iniY)) - ySize / 2:\
                int(round(self.imgProcess.view.projView.iniY)) + ySize / 2,\
                int(round(self.imgProcess.view.projView.iniX)) - xSize / 2:\
                int(round(self.imgProcess.view.projView.iniX)) + xSize / 2]
        print "done"
        self.data = self.temp_data
        self.x = xSize
        self.y = ySize
        self.sino.sld.setRange(1, self.y)
        self.sino.sld.setValue(1)
        self.sino.lcd.display(1)

    def ipWiener(self):
        '''
        applies weiner filter on tomographic data of chosen element
        '''
        element = self.imgProcessControl.combo1.currentIndex()
        for i in arange(self.projections):
            img = self.data[element, i, :, :]
            img[np.where(img == 0)] = 10 ** (-8)
            img_fin = wiener(img)
            self.data[element, i, :, :] = img_fin

    def gauss2D(self, shape=(3, 3), sigma=0.5):
        """
        2D gaussian mask - should give the same result as MATLAB's
        fspecial('gaussian',[shape],[sigma])
        """
        m, n = [(ss - 1.) / 2. for ss in shape]
        y, x = np.ogrid[-m:m + 1, -n:n + 1]
        h = np.exp(-(x * x + y * y) / (2. * sigma * sigma))
        h[h < np.finfo(h.dtype).eps * h.max()] = 0
        sumh = h.sum()
        if sumh != 0:
            h /= sumh
        return h

    def gauss33(self):
        result = self.gauss2D(shape=(3, 3), sigma=1.3)
        return result

    def gauss55(self):
        result = self.gauss2D(shape=(5, 5), sigma=1.3)
        return result

    # ==========================
    ## Gaussian fit from wiki.scipy.org/Cookbook/FittingData
    def gaussian(self, height, center_x, center_y, width_x, width_y):
        """Returns a gaussian function with the given parameters"""
        width_x = float(width_x)
        width_y = float(width_y)
        return lambda x, y: height * exp(-(((center_x - x) / width_x) ** 2 + ((center_y - y) / width_y) ** 2) / 2)

    def moments(self, data):
        """Returns (height, x, y, width_x, width_y)
        the gaussian parameters of a 2D distribution by calculating its
        moments """
        total = data.sum()
        X, Y = indices(data.shape)
        x = (X * data).sum() / total
        y = (Y * data).sum() / total
        col = data[:, int(y)]
        width_x = sqrt(abs((arange(col.size) - y) ** 2 * col).sum() / col.sum())
        row = data[int(x), :]
        width_y = sqrt(abs((arange(row.size) - x) ** 2 * row).sum() / row.sum())
        height = data.max()
        return height, x, y, width_x, width_y

    def fitgaussian(self, data):
        """Returns (height, x, y, width_x, width_y)
        the gaussian parameters of a 2D distribution found by a fit"""
        params = self.moments(data)
        errorfunction = lambda p: ravel(self.gaussian(*p)(*indices(data.shape)) - data)
        p, success = optimize.leastsq(errorfunction, params)
        return p

    # ==========================
    def export_data(self):
        '''
        export data into h5 files
        '''
        a = h5py.File("export_data.h5")
        print np.where(self.data == inf)

        a.create_dataset("data", data=self.data, compression="gzip")
        a.create_dataset("theta", data=self.theta, compression="gzip")
        a.close()

    # ==========================

    def runTransReconstruct(self):
        '''
        load variables to reconstruction controller window
        '''
        self.recon.numb = len(self.channelname)
        for j in arange(self.recon.numb):
            self.recon.combo.addItem(self.channelname[j])
        self.recon.show()
        self.recon.btn.setText("Reconstruction")
        self.recon.btn.clicked.connect(self.reconstruct)
        self.recon.save.clicked.connect(self.saveRecTiff)
        self.recon.reconvalue = 1

    def reconMultiply(self):
        '''
        multiply reconstruction by 10
        '''
        self.rec = self.rec * 10
        self.updateRecon()

    def reconDivide(self):
        '''
        divide reconstuction by 10
        '''
        self.rec = self.rec / 10
        self.updateRecon()

    def updateRecon(self):
        '''
        update image as slider moves

        Variables
        ----------
        self.recon: ndarray
              3D volume reconstruction
        '''
        self.file_name_update(self.reconView)
        self.reconProjNumb = self.reconView.sld.value()
        self.recon.maxText.setText(str(self.rec[self.reconProjNumb, :, :].max()))
        self.recon.minText.setText(str(self.rec[self.reconProjNumb, :, :].min()))
        self.reconView.view.projView.setImage(self.rec[self.reconProjNumb, :, :])

    def runReconstruct(self):
        '''
        load window for reconstruction window
        '''
        self.tab_widget.removeTab(3)
        self.tab_widget.insertTab(3, self.createReconWidget(), unicode("Reconstruction"))
        self.recon.numb = len(self.channelname)
        for j in arange(self.recon.numb):
            self.recon.combo.addItem(self.channelname[j])
        self.recon.show()
        self.recon.lcd.setText(str(self.p1[2]))
        self.recon.btn.clicked.connect(self.reconstruct)
        self.recon.save.clicked.connect(self.saveRecTiff)
        self.recon.reconvalue = 0
        self.recon.mulBtn.clicked.connect(self.reconMultiply)
        self.recon.divBtn.clicked.connect(self.reconDivide)
        self.recon.cbox.clicked.connect(self.cboxClicked)
        self.reconView.sld.setRange(0, self.y- 1)
        self.reconView.sld.valueChanged.connect(self.reconView.lcd.display)
        self.reconView.sld.valueChanged.connect(self.updateRecon)
        self.recon.threshBtn.clicked.connect(self.threshold)

    def threshold(self):
        '''
        set threshhold for reconstruction
        '''
        threshValue = float(self.recon.threshLe.text())
        self.rec[np.where(self.rec <= threshValue)] = 0  # np.min(self.rec)

    def reconstruct(self):
        '''
        load data for reconstruction and load variables for reconstruction
        make it sure that data doesn't have infinity or nan as one of
        entries
        '''
        self.recon.lbl.setText("Reconstruction is currently running")
        self.reconelement = self.recon.combo.currentIndex()
        self.recData = self.data[self.reconelement, :, :, :]
        self.recData[self.recData == inf] = 0.00001
        self.recData[np.isnan(self.recData)] = 0.00001
        # self.recData = tomopy.normalize_bg(self.recData)

        self.recCenter = np.array(float(self.recon.lcd.text()), dtype=float32)
        beta = float(self.recon.beta.text())
        delta = float(self.recon.delta.text())
        num_iter = int(self.recon.iters.text())
        print beta, delta, num_iter

        if self.recon.cbox.isChecked():
            self.recCenter = None
        print "working fine"

        if self.recon.method.currentIndex() == 0:
            self.rec = tomopy.recon(self.recData, self.theta * np.pi / 180, algorithm='mlem', center=self.recCenter,
                                    num_iter=num_iter)
        elif self.recon.method.currentIndex() == 1:
            self.rec = tomopy.recon(self.recData, self.theta, algorithm='gridrec',
                                    emission=True)
        elif self.recon.method.currentIndex() == 2:
            self.rec = tomopy.recon(self.recData, self.theta * np.pi / 180, algorithm='art',
                                    num_iter=num_iter)
        elif self.recon.method.currentIndex() == 3:
            self.rec = tomopy.recon(self.recData, self.theta * np.pi / 180, algorithm='pml_hybrid',
                                    center=self.recCenter,
                                    reg_par=np.array([beta, delta], dtype=np.float32), num_iter=num_iter)
        elif self.recon.method.currentIndex() == 4:
            self.rec = tomopy.recon(self.recData, self.theta * np.pi / 180, algorithm='pml_quad', center=self.recCenter,
                                    reg_par=np.array([beta, delta], dtype=np.float32), num_iter=num_iter)

        self.rec = tomopy.remove_nan(self.rec)
        self.reconProjNumb = self.projView.sld.value()
        self.reconView.view.projView.setImage(self.rec[self.reconProjNumb, :, :])
        self.reconView.setWindowTitle("Slices of reconstructed model")
        self.recon.lbl.setText("Done")
        self.recon.save.setHidden(False)

    def cboxClicked(self):
        if self.recon.cbox.isChecked():
            self.recon.lcd.setEnabled(True)
        else:
            self.recon.lcd.setEnabled(False)

    def circular_mask(self):
        '''
        circular mask on 3d reconstruction

        Variables:
        -----------

        self.rec: ndarray
              3D reconstruction
        '''
        self.rec = tomopy.circ_mask(self.rec, axis=0)

    def saveRecTiff(self):
        '''
        saves 3D volume reconstruion into tiff files

        Variables:
        -----------

        self.rec: ndarray
              3D reconstruction

        '''
        try:
            global debugging
            self.savedir = QtGui.QFileDialog.getSaveFileName()
            self.savedir = str(self.savedir)
            if self.savedir == "":
                raise IndexError
            print self.savedir
            self.circular_mask()  ### temporary
            tomopy.write_tiff_stack(self.rec, fname=self.savedir)
        except IndexError:
            print "type the header name"

    # =============================

    def reorder_matrix(self):
        '''
        rearrange data so that data is in the order of angle not
        chronological order.

        Variables
        -----------
        self.theta: ndarray
              list of angles
        self.data: ndarray
              4D tomographic data [element,projections,y,x]
        '''
        argsorted = argsort(self.theta)
        print argsorted, self.theta[argsorted]
        self.data = self.data[:, argsorted, :, :]
        self.projView.view.data = self.data[self.projViewElement, :, :, :]
        print "sorting done"

    # =============================

    def selectImageTag(self):
        '''
        load select image tag window.
        one may choose tag so that data can be read at correct
        part of h5 files.

        Variables
        ----------
        self.fileNames: ndarray
              list of file names
        '''
        self.sit = AlignWindow()
        self.sit.setWindowTitle("Seletect Image Tag from h5 file")
        self.sit.data = h5py.File(self.fileNames[0])
        self.sit.firstColumn = self.sit.data.items()
        self.sit.firstColumnNum = len(self.sit.firstColumn)
        for i in arange(self.sit.firstColumnNum):
            self.sit.combo.addItem(self.sit.firstColumn[i][0])
        print self.sit.combo.currentIndex()

        self.sit.combo.setCurrentIndex(i)
        for i in arange(30):
            self.sit.method.removeItem(0)
        self.sit.secondColumnName = self.sit.firstColumn[self.sit.combo.currentIndex()][0]

        self.sit.secondColumn = self.sit.data[self.sit.secondColumnName].items()
        self.sit.secondColumnNum = len(self.sit.secondColumn)
        for j in arange(self.sit.secondColumnNum):
            self.sit.method.addItem(self.sit.secondColumn[j][0])

        self.sit.combo.currentIndexChanged.connect(self.selectImageTag_image)
        self.sit.btn.setText("Set")
        self.sit.btn2.setVisible(False)
        self.sit.btn.clicked.connect(self.setImageTag)

        self.sit.show()

    def selectImageTag_image(self):
        '''
        update child tags when parent tag has been changed
        '''
        for i in arange(30):
            self.sit.method.removeItem(0)
        self.sit.secondColumnName = self.sit.firstColumn[self.sit.combo.currentIndex()][0]

        self.sit.secondColumn = self.sit.data[self.sit.secondColumnName].items()
        self.sit.secondColumnNum = len(self.sit.secondColumn)
        for j in arange(self.sit.secondColumnNum):
            self.sit.method.addItem(self.sit.secondColumn[j][0])

        self.sit.method.setHidden(False)

    def setImageTag(self):
        '''
        set the name of tag that you are interested in
        '''
        self.ImageTag = str(self.sit.combo.currentText())
        self.lbl.setText("Image Tag has been set to \"" + self.ImageTag + "\"")
        print "Image Tag has been set to \"", self.ImageTag, "\""
        self.sit.setVisible(False)

    # ==============================

    def selectElement(self):
        '''
        loads select element window
        '''

        try:
            self.channelnameTemp = list(self.f[0][self.ImageTag]["images_names"])
            self.dataTag = "images"
            self.channels, self.y, self.x = self.f[0][self.ImageTag]["images"].shape
        except KeyError:
            try:
                self.dataTag = "data"
                self.channelnameTemp = list(self.f[0][self.ImageTag]["channel_names"])
                self.channels, self.y, self.x = self.f[0][self.ImageTag]["data"].shape
            except KeyError:
                self.dataTag = "XRF_roi"
                self.channelnameTemp1 = self.f[0][self.ImageTag]["channel_names"]

                self.channelnameTemp2 = self.f[0][self.ImageTag]["scaler_names"]
                self.channels1, self.y, self.x = self.f[0][self.ImageTag]["XRF_roi"].shape
                self.channels = self.channels1 + len(self.channelnameTemp2)
                self.channelnameTemp = list(self.channelnameTemp1) + list(self.channelnameTemp2)

        self.element = QSelect(self.channels)
        for i in arange(len(self.channelnameTemp)):
            self.element.button[i].setText(self.channelnameTemp[i])
            self.element.button[i].setChecked(True)
        self.element.setWindowTitle("Select Element")
        self.element.setVisible(False)
        self.element.btn2.setText("Deselect All")
        self.element.btn.setText("set Element")
        self.element.btn.clicked.connect(self.setElement)
        self.element.btn2.clicked.connect(self.deselectAllElement)
        self.element.btn3.setVisible(False)
        self.element.btn4.setVisible(False)

        for i in range(self.channels):
            for j in range(len(self.fileNames)):
                self.f[i]["MAPS"]["XRF_roi"][j] = np.nan_to_num(self.f[i]["MAPS"]["XRF_roi"][j])

    def deselectAllElement(self):
        '''
        deselect all the checkboxes in selectElement window
        '''
        for i in arange(len(self.channelnameTemp)):
            self.element.button[i].setText(self.channelnameTemp[i])
            self.element.button[i].setChecked(False)

    def setElement(self):
        '''
        set elements of interest so that we don't have to
        save all the data in memory

        Variables
        -----------
        self.channelnameTem: pndarray
              list of names of channels
        '''
        y = zeros(len(self.channelnameTemp), dtype=bool)
        k = arange(y.shape[0])
        for i in arange(len(self.channelnameTemp)):
            y[i] = self.element.button[i].isChecked()
        self.channelname = [self.channelnameTemp[f] for f in k if y[f]]
        self.channelnamePos = zeros(len(self.channelname))
        for i in arange(len(self.channelname)):
            self.channelnamePos[i] = self.channelnameTemp.index(self.channelname[i])
        self.element.setVisible(False)

    def selectElementShow(self):
        self.element.setVisible(True)

    def selectFilesShow(self):
        self.filecheck.setVisible(True)
        # self.fcheck.setVisible(True)

    def selectBeamline(self, message=""):
        self.conf = ConfigurationWindow()
        if type(message) == str:
            self.conf.lbl3.setText(message)
        self.conf.show()
        self.conf.btn.clicked.connect(self.beamline)

    def beamline(self):
        bnp = self.conf.button.isChecked()
        twoide = self.conf.button2.isChecked()
        thetaposbnp = self.conf.txtfield.text()
        thetapos2ide = self.conf.txtfield2.text()

        if bnp == 0 and twoide == 0:
            self.conf.hide()
            self.selectBeamline("please select a beamline")
        elif bnp == 0 and twoide == 1:
            self.thetaPos = int(thetapos2ide)
            self.conf.hide()
            self.openfile()
        elif bnp == 1 and twoide == 0:
            self.thetaPos = int(thetaposbnp)
            self.conf.hide()
            self.openfile()
        elif bnp == 1 and twoide == 1:
            self.conf.hide()
            self.selectBeamline("please select only one beamline")

    def openfile(self):
        '''
        opens multiple h5 files.
        '''
        self.fileNames, self.theta, self.f = [],[],[]
        try:
            fileNametemp = QtGui.QFileDialog.getOpenFileNames(self, "Open File", QtCore.QDir.currentPath(), filter="h5 (*.h5)")
            self.fileNames = str(fileNametemp.join("\n")).split("\n")
            if self.fileNames == [""]: 
                raise IndexError
            self.fileNames = np.array(self.fileNames)

            for i in range(len(self.fileNames)):
                self.f.append(h5py.File(os.path.abspath(self.fileNames[i]),"r"))
                tmp = string.rfind(self.f[i]["MAPS"]["extra_pvs_as_csv"][self.thetaPos], ",")
                thetatmp = round(float(self.f[i]["MAPS"]["extra_pvs_as_csv"][self.thetaPos][tmp+1:]))
                self.theta = np.append(self.theta,thetatmp)

            self.selectFiles()

        except IndexError, AttributeError:
            print "no file has been selected, IndexError"
        except IOError:
            print "no file has been selected, IOError"

    def selectFiles(self):
        '''
        load select files window
        Window contains checkboxes along with name of the file and angle

        Variables
        -----------
        self.fileNames: ndarray
              list of name of the files
        self.thetaPos: number
              index where the angle information is saved in
              extra_pvs_as_csv
        '''
        numfiles = len(self.fileNames)
        self.filecheck = QSelect(numfiles)
        files = []
        degree_sign = u'\N{DEGREE SIGN}'
        for i in arange(len(self.fileNames)):
            onlyfilenameIndex = self.fileNames[i].rfind("/")
            files.append(self.fileNames[i][onlyfilenameIndex + 1:])
            self.filecheck.button[i].setText(self.fileNames[i][onlyfilenameIndex + 1:].split("_")[-1] + " (" + str(self.theta[i]) + degree_sign + ")")
            self.filecheck.button[i].setChecked(True)
        self.files = np.array(files)
        self.ImageTag = self.f[1].items()[-1][0]
        self.lbl.setText("Image Tag has been set to \"" + self.ImageTag + "\"")
        self.filecheck.setWindowTitle("Select files")
        self.optionMenu.setEnabled(True)
        self.filecheck.btn2.setVisible(True)
        self.filecheck.show()
        self.filecheck.btn.clicked.connect(self.convert)
        self.filecheck.btn2.clicked.connect(self.selectImageTag)
        self.filecheck.btn3.clicked.connect(self.selectElementShow)
        self.filecheck.btn4.clicked.connect(self.sortData)
        self.selectElement()

    def sortData(self):
        sortedindx = np.argsort(self.theta)
        self.fileNames = self.fileNames[sortedindx]
        self.files = self.files[sortedindx]
        self.theta = self.theta[sortedindx]
        self.selectFiles()

    def convert(self):
        '''
        runs couple of functions to load data into memory
        '''
        self.afterConversionMenu.setDisabled(False)
        self.convert2array()
        self.imgProcess.file_name_title.setText(self.files[self.imgProcess.sld.value()])
        self.projView.file_name_title.setText(self.files[self.imgProcess.sld.value()])
        self.reconView.file_name_title.setText(self.files[self.imgProcess.sld.value()])
        self.imgProcessControl.combo1.setCurrentIndex(1)
        self.imgProcessControl.combo1.setCurrentIndex(0)
        self.projViewControl.combo.setCurrentIndex(1)
        self.projViewControl.combo.setCurrentIndex(0)
        self.filecheck.setVisible(False)
        # self.fcheck.setVisible(False)

        # self.x.show()
    def openTiffFolder(self):
        '''
        opens the folder that contains tiff files and read file names.
        also save the name of text file that contains angle information
        '''
        pass1 = False
        try:
            tiffFolderName = QtGui.QFileDialog.getExistingDirectory(self, "Open Tiff Folder",
                                                                    QtCore.QDir.currentPath())
            file_name_array = [f for f in os.listdir(tiffFolderName) if string.find(f, "tif") != -1]
            file_name_array = [tiffFolderName + "/" + f for f in file_name_array]

            self.tiffNames = file_name_array

            pass1 = True
        except IndexError:
            print "no folder has been selected"
        except OSError:
            print "no folder has been selected"
        if pass1 == True:
            try:
                angleTxt = QtGui.QFileDialog.getOpenFileName(self, "Open Angle Txt File",
                                                             QtCore.QDir.currentPath(), filter="txt (*.txt)")
                print str(angleTxt)
                self.angleTxt = angleTxt
                self.convertTiff2Array()
            except IndexError:
                print "no file has been selected"
            except OSError:
                print "no file has been selected"

    def convertTiff2Array(self):
        '''
        read tiff files and angle information. save in memory afterwards.

        Variables
        -----------
        self.tiffNames: ndarray
              list of names of image files
        self.angleTxt: QString
              name of the text file that contains angle information
        '''
        self.projections = len(self.tiffNames)
        self.y, self.x = np.asarray(Image.open(str(self.tiffNames[0])), dtype=float32).shape
        self.channelname = list()
        self.channelname.append("tiff")
        self.channelname.append("dummy")
        self.data = zeros([1, self.projections, self.y, self.x])
        self.theta = zeros(self.projections)
        f = open(str(self.angleTxt), 'r')
        read = f.readlines()

        for i in arange(self.projections):
            tempy, tempx = np.asarray(Image.open(str(self.tiffNames[i])), dtype=float32).shape
            if tempy > self.y:
                self.y = tempy
            if tempx > self.x:
                self.x = tempx
        self.data = zeros([1, self.projections, self.y, self.x])
        for i in arange(self.projections):
            tempy, tempx = np.asarray(Image.open(str(self.tiffNames[i])), dtype=float32).shape
            self.data[0, i, :tempy, :tempx] = np.asarray(Image.open(str(self.tiffNames[i])), dtype=float32)[...]
            thetaPos = read[i].find(",")
            self.theta[i] = float(read[i][thetaPos + 1:])
        self.p1 = [100, 100, self.data.shape[3] / 2]

        self.xshift = zeros(self.projections, int)
        self.yshift = zeros(self.projections, int)
        self.alignmentMenu.setEnabled(True)
        self.tab_widget.setEnabled(True)
        self.afterConversionMenu.setDisabled(False)

        self.oldData = zeros(self.data.shape)
        self.oldData[...] = self.data[...]

        self.showImageProcess()
        self.showSaveHotSpotPos()
        self.projView.view.hotSpotSetNumb = 0
        self.showSinogram()
        self.sinogram()
        self.runReconstruct()

        self.selectedFiles = list()
        for i in arange(self.projections):
            self.selectedFiles.append(str(self.tiffNames[i]))

        self.projView.view.hotSpotSetNumb = 0
        self.tab_widget.setCurrentIndex(0)

        self.updateImages()

    def convert2array(self):
        '''
        read all the necessary informations from h5 files and save in memory

        Variables
        -----------
        self.fileNames: ndarray
              list of file names
        '''
        self.setElement()
        y = zeros(len(self.fileNames), dtype=bool)
        k = arange(y.shape[0])
        for i in arange(len(self.fileNames)):
            y[i] = self.filecheck.button[i].isChecked()
            # y[i] = self.fcheck.button[i].isChecked()

        self.selectedFiles = [self.fileNames[f] for f in k if y[f] == True]

        ### From first data retrieve channel names, size of the image.
        try:
            self.dataTag = "images"
            self.channels, self.y, self.x = self.f[0][self.ImageTag]["images"].shape
        except KeyError:
            try:
                self.dataTag = "data"
                self.channels, self.y, self.x = self.f[0][self.ImageTag]["data"].shape
            except KeyError:
                self.dataTag = "XRF_roi"
                self.channels1, self.y, self.x = self.f[0][self.ImageTag]["XRF_roi"].shape
                self.channels = self.channels1 + len(self.channelnameTemp2)
        self.projections = len(self.selectedFiles)
        self.theta = zeros(self.projections)
        self.xshift = zeros(self.projections, int)
        self.yshift = zeros(self.projections, int)
        self.channels = len(self.channelname)

        #### check the size of the images
        x, y = 0, 0
        for i in arange(self.projections):
            dummy, tempY, tempX = self.f[i][self.ImageTag][self.dataTag][...].shape
            if tempX > x: x = tempX
            if tempY > y: y = tempY
        self.x = x
        self.y = y

        if self.dataTag != "XRF_roi":
            self.data = zeros([self.channels, self.projections, self.y, self.x])
            for i in arange(self.projections):
                file_name = os.path.abspath(self.selectedFiles[i])
                f = h5py.File(file_name, "r")
                thetatemp = f["MAPS"]["extra_pvs_as_csv"][self.thetaPos]
                self.theta[i] = float(thetatemp[thetatemp.rfind(",") + 1:])
                for j in arange(len(self.channelnamePos)):
                    pos = self.channelnamePos[j]
                    imgY, imgX = f[self.ImageTag][self.dataTag][0, :, :].shape
                    dy = (y - imgY) / 2
                    dx = (x - imgX) / 2
                    temp_img = f[self.ImageTag][self.dataTag][pos, :, :]
                    temp_img[np.where(temp_img == 0)] = True
                    self.data[j, i, dy:imgY + dy, dx:imgX + dx] = temp_img
                print i + 1, "projection(s) has/have been converted"
            print "worked"

        if self.dataTag == "XRF_roi":
            self.data = zeros([self.channels, self.projections, self.y, self.x])
            for i in arange(self.projections):
                f = h5py.File(os.path.abspath(self.selectedFiles[i]), "r")
                thetatemp = f["MAPS"]["extra_pvs_as_csv"][self.thetaPos]
                self.theta[i] = float(thetatemp[thetatemp.rfind(",") + 1:])
                for j in arange(len(self.channelnamePos)):
                    if self.channelnamePos[j] < len(list(self.channelnameTemp1)):
                        pos = self.channelnamePos[j]
                        imgY, imgX = f[self.ImageTag][self.dataTag][0, :, :].shape
                        dy = (y - imgY) / 2
                        dx = (x - imgX) / 2
                        temp_img = f[self.ImageTag][self.dataTag][pos, :, :]
                        temp_img[np.where(temp_img == 0)] = True
                        self.data[j, i, dy:imgY + dy, dx:imgX + dx] = temp_img
                    else:
                        pos = self.channelnamePos[j] - len(list(self.channelnameTemp1))
                        imgY, imgX = f[self.ImageTag]["scalers"][0, :, :].shape
                        dy = (y - imgY) / 2
                        dx = (x - imgX) / 2
                        temp_img = f[self.ImageTag]["scalers"][pos, :, :]
                        temp_img[np.where(temp_img == 0)] = True
                        self.data[j, i, dy:imgY + dy, dx:imgX + dx] = temp_img
                print i + 1, "projection(s) has/have been converted"
            print "worked"

        self.data[isnan(self.data)] = 0.0001
        self.data[self.data == inf] = 0.0001
        self.p1 = [100, 100, self.data.shape[3] / 2]

        self.alignmentMenu.setEnabled(True)
        self.tab_widget.setEnabled(True)

        self.oldData = zeros(self.data.shape)
        self.oldData[...] = self.data[...]
        global datadata
        datadata = self.oldData

        self.showImageProcess()
        self.showSaveHotSpotPos()
        self.projView.view.hotSpotSetNumb = 0
        self.showSinogram()
        self.sinogram()

        self.runReconstruct()
        self.tab_widget.setCurrentIndex(0)

        self.updateImages()

    def saveThetaTxt(self):
        '''
        export angle data into text file

        self.theta: ndarray
              list of angles
        '''
        try:
            self.alignFileName = QtGui.QFileDialog.getSaveFileName()
            if string.rfind(str(self.alignFileName), ".txt") == -1:
                self.alignFileName = str(self.alignFileName) + ".txt"
            print str(self.alignFileName)
            f = open(self.alignFileName, "w")
            for i in arange(self.projections):
                onlyfilenameIndex = self.selectedFiles[i].rfind("/")
                print self.selectedFiles[i]
                f.writelines(self.selectedFiles[i][onlyfilenameIndex + 1:-3] + ", " + str(self.theta[i]) + "\n")

            f.close()
        except IOError:
            print "choose file please"

    #####!!!! just temp need to be fixed
    def saveImage(self):
        '''
        export projections into tif images

        Variables
        -----------
        self.data: ndarray
              4D tomographic data [elements, projections,y,x]
        self.channelname: ndarray
              list of channel names
        self.selectedFiles: ndarray
              list of the names of the files that are selected
        '''
        self.saveImageDir = QtGui.QFileDialog.getExistingDirectory()
        print self.saveImageDir
        for j in arange(self.data.shape[0]):
            path = str(self.saveImageDir) + "/" + self.channelname[j]
            try:
                os.makedirs(path)
            except OSError:
                path = path
            for i in arange(self.data.shape[1]):
                temp_img = self.data[j, i, :, :]
                temp = Image.fromarray(temp_img.astype(np.float32))
                index = string.rfind(self.selectedFiles[i], "/")
                temp.save(path + self.selectedFiles[i][index:-3] + ".tif")

    def multiplier(self):
        '''
        mutliplies whole data by 10
        '''
        self.data = 10 * self.data
        self.updateImages()

    def divider(self):
        '''
        divides whole data by 10
        '''
        self.data = self.data * 0.1
        self.updateImages()

    def normalize(self):
        '''
        normalize data

        Variables
        -----------
        self.projection.combo.currentIndex(): number
              indicates the index of the element of interest
        self.data: ndarray
              4d tomographic data [element,projections,y,x]
        '''
        self.normElement = self.projection.combo.currentIndex()
        normData = self.data[self.normElement, :, :, :]
        for i in arange(normData.shape[0]):
            print normData.dtype
            temp = normData[i, :, :][...]
            tempMax = temp.max()
            tempMin = temp.min()
            temp = (temp - tempMin) / tempMax
            self.data[self.normElement, i, :, :] = temp
        self.updateImages()

    def showSinogram(self):
        '''
        loads sinogram tab
        '''
        # self.sino = QSelect2()
        # self.sino.setWindowTitle("Sinogram Window")
        self.tab_widget.removeTab(2)
        self.tab_widget.insertTab(2, self.createSinoWidget(), unicode("Sinogram"))

        self.sino.numb = len(self.channelname)
        for j in arange(self.sino.numb):
            self.sino.combo.addItem(self.channelname[j])
        self.sino.show()
        self.sino.btn.clicked.connect(self.runCenterOfMass2)
        self.sino.btn2.clicked.connect(self.sinoShift)
        self.sino.sld.setRange(1, self.y)
        self.sino.lcd.display(1)
        self.sino.sld.valueChanged.connect(self.sino.lcd.display)
        self.sino.sld.valueChanged.connect(self.sinogram)
        self.sinoView.show()

    def sinogram(self):
        '''
        load variables and image for sinogram window

        Variables
        -----------
        self.thickness: number
              thickness of y of each projections
        self.sino.combo.currentIndex(): number
              indicates the index of the element
        self.data: ndarray
              4d tomographic data [element, projections, y,x]
        '''
        self.file_name_update(self.sino)
        self.thickness = 10
        self.sinoelement = self.sino.combo.currentIndex()
        sinodata = self.data[self.sinoelement, :, :, :]
        self.sinogramData = zeros([sinodata.shape[0] * self.thickness, sinodata.shape[2]], dtype=float32)

        for i in arange(self.projections):
            self.sinogramData[i * self.thickness:(i + 1) * self.thickness, :] = sinodata[i,
            self.sino.sld.value()-1,:]

        global sinofig

        sinofig = self.sinogramData
        self.sinogramData[isinf(self.sinogramData)] = 0.001
        self.sinoView.view.projView.setImage(self.sinogramData)
        self.sinoView.view.projView.setRect(QtCore.QRect(round(self.theta[0]), 0, round(self.theta[-1])- round(self.theta[0]), self.sinogramData.shape[1]))

        self.sinoView.view.projData = self.sinogramData
        self.sinoView.view.getShape()

    def saveSinogram(self):
        '''
        export sinogram tif image

        Variables
        -----------
        self.sinogramData: ndarray
              sinogram image
        '''
        j = Image.fromarray(self.sinogramData.astype(np.float32))
        j.save("sinogram.tif")

    def sinoShift(self):
        '''
        shift images and record in data array

        Variables
        -----------
        self.data: ndarray
              4D tomographic data [element,projections,y,x]
        self.sinoView.view.regShift: ndarray
              horizontal shift registered by manually shifting on sinogram
              winodow.
        '''
        for i in arange(self.projections):
            self.data[:, i, :, :] = np.roll(self.data[:, i, :, :], self.sinoView.view.regShift[i], axis=2)

    def updateImages(self):
        '''
        reload images with new data and variables.
        '''
        self.projView.view.projView.update()
        self.imgProcess.view.projView.updateImage()
        self.sinoView.view.projView.updateImage()

    def alignmentDone(self):
        '''
        send message that alignment has been done
        '''
        self.lbl.setText("Alignment has been completed")

    ####==============
    def readConfigFile(self):
        '''
        Align center of Mass
        Variables
        ------------
        self.ImageTag: ndarray
              Difference of center of mass of first projections and center
              of other projections
        self.thetaPos: number
              record the position where angle is recorded in extra pvs as csv
        '''

        try:
            fileName = QtGui.QFileDialog.getOpenFileName(self, "Select config file",
                                                         QtCore.QDir.currentPath(), "TXT (*.txt)")
            ##### for future reference "All File (*);;CSV (*.csv *.CSV)"
            print fileName
            f = open(fileName, 'r')
            l = f.readlines()
            for i in arange(len(l)):
                ## image_tag
                if string.find(l[i], "Image_Tag") != -1:
                    self.ImageTag = l[i + 1][:-1]
                ## theta postion from extra pvs as csv
                if string.find(l[i], "Theta position") != -1:
                    print l[i + 1][:-1]
                    self.thetaPos = int(l[i + 1][:-1])
            # self.selectFiles()
            self.lbl.setText("configuration added. Step 2) open h5 files")
        except IOError:
            print "choose file please"

################
#######!!!!!!!!! Windows
####===============

class AlignWindow(QtGui.QWidget):
    def __init__(self):
        super(AlignWindow, self).__init__()
        self.initUI()

    def initUI(self):
        self.combo = QtGui.QComboBox(self)
        self.method = QtGui.QComboBox(self)

        self.btn = QtGui.QPushButton('Click2')
        self.btn2 = QtGui.QPushButton("Click3")
        vb = QtGui.QVBoxLayout()
        vb.addWidget(self.combo)
        vb.addWidget(self.method)
        vb.addWidget(self.btn)
        vb.addWidget(self.btn2)
        self.setLayout(vb)

class QSelect(QtGui.QWidget):

    def __init__(self, labels):
        super(QSelect, self).__init__()
        self.numlabels = labels
        self.initUI()

    def initUI(self):
        names = list()
        list_sqrt = np.sqrt(self.numlabels)
        columns = np.ceil(list_sqrt/1.5)
        rows = np.ceil(list_sqrt*1.5)

        for i in arange(self.numlabels):
            names.append("")
        self.grid = QtGui.QGridLayout()
        self.lbl = QtGui.QLabel()
        self.lbl2 = QtGui.QLabel()
        self.lbl.setText("closing this window won't affect your selection of the files")
        self.lbl2.setText("You should convert the files in order to generate sinogram or reconstructed data")
        self.btn = QtGui.QPushButton('Save Data in Memory')
        self.btn2 = QtGui.QPushButton("set Image Tag")
        self.btn3 = QtGui.QPushButton("set Element")
        self.btn4 = QtGui.QPushButton("Sort data by angle")

        j = 0
        pos = list()
        for y in arange(columns):
            for x in arange(rows):
                pos.append((x, y))

        self.button = list()
        for i in names:
            self.button.append(QtGui.QCheckBox(i))
            self.grid.addWidget(self.button[j], pos[j][0], pos[j][1])
            j += 1
        self.setLayout(self.grid)

        self.vb = QtGui.QVBoxLayout()
        self.vb2 = QtGui.QVBoxLayout()

        self.vb.addWidget(self.lbl, rows+2)
        self.vb.addWidget(self.lbl2, rows+3)

        hb = QtGui.QHBoxLayout()
        hb.addWidget(self.btn2)
        hb.addWidget(self.btn3)
        hb.addWidget(self.btn4)

        self.vb2.addLayout(hb)
        self.vb2.addWidget(self.btn)

        self.grid.addLayout(self.vb, rows+1, 0, 1, 7)
        self.grid.addLayout(self.vb2, rows+3, 1, 1, 3)

        self.move(100, 100)
        self.setWindowTitle('Calculator')

####==================
class QSelect2(QtGui.QWidget):

    def __init__(self):
        super(QSelect2, self).__init__()
        self.initUI()

    def initUI(self):
        self.combo = QtGui.QComboBox(self)
        self.combo.setMinimumSize(212,25)
        self.sld = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        self.sld.setMaximumSize(212,25)
        self.lcd = QtGui.QLCDNumber(self)
        self.lcd.setMaximumSize(212,50)
        self.btn = QtGui.QPushButton('center of mass')
        self.btn.setMaximumSize(212,25)
        self.btn2 = QtGui.QPushButton("shift data")
        self.btn2.setMaximumSize(212,25)
        self.btn3 = QtGui.QPushButton("X 10")
        self.btn3.setMaximumSize(212,25)
        self.btn4 = QtGui.QPushButton("/ 10")
        self.btn4.setMaximumSize(212,25)

        hb = QtGui.QHBoxLayout()
        hb.addWidget(self.btn3)
        hb.addWidget(self.btn4)
        self.btn3.setVisible(False)
        self.btn4.setVisible(False)
        self.lbl = QtGui.QLabel("")
        vb = QtGui.QVBoxLayout()
        vb.addWidget(self.combo)
        vb.addWidget(self.btn)
        vb.addWidget(self.btn2)
        vb.addWidget(self.lcd)
        vb.addWidget(self.sld)
        vb.addWidget(self.lbl)
        vb.addLayout(hb)
        self.setLayout(vb)

class QSelect3(QtGui.QWidget):

    def __init__(self):
        super(QSelect3, self).__init__()
        self.initUI()

    def initUI(self):
        self.combo = QtGui.QComboBox(self)
        self.combo.setMinimumSize(212,25)
        self.method = QtGui.QComboBox(self)
        self.method.setMaximumSize(212,25)
        self.methodname = ["mlem", "gridrec", "art", "pml_hybrid", "pml_quad"]
        self.btn = QtGui.QPushButton('Reconstruction')
        self.btn.setMaximumSize(212,25)
        self.save = QtGui.QPushButton("Save tiff files")
        self.save.setMaximumSize(212,25)
        self.save.setHidden(True)

        self.cbox = QtGui.QCheckBox("")
        self.lcd = QtGui.QLineEdit("0")
        self.lcd.setMaximumSize(100,25)
        self.lcd.setEnabled(False)
        self.lbl2 = QtGui.QLabel("Center")

        self.threshLbl = QtGui.QLabel("threshold")
        self.threshLbl.setMaximumSize(75,25)
        self.threshLe = QtGui.QLineEdit("")
        self.threshLe.setMaximumSize(50,25)
        self.threshBtn = QtGui.QPushButton("Apply")
        self.threshBtn.setMaximumSize(75,25)

        # this is empty space
        self.lbl = QtGui.QLabel('')
        self.lbl.setMaximumSize(212,25)
        self.sld = QtGui.QSlider(QtCore.Qt.Horizontal, self)

        centerBox = QtGui.QHBoxLayout()
        centerBox.addWidget(self.cbox)
        centerBox.addWidget(self.lbl2)
        centerBox.addWidget(self.lcd)

        self.mulBtn = QtGui.QPushButton("x 10")
        self.mulBtn.setMaximumSize(100,25)
        self.divBtn = QtGui.QPushButton("/ 10")
        self.divBtn.setMaximumSize(100,25)

        mdBox = QtGui.QHBoxLayout()
        mdBox.addWidget(self.mulBtn)
        mdBox.addWidget(self.divBtn)

        self.maxLbl = QtGui.QLabel("Max")
        self.maxLbl.setMaximumSize(100,25)
        self.minLbl = QtGui.QLabel("Min")
        self.minLbl.setMaximumSize(100,25)
        self.betaName = QtGui.QLabel("Beta")
        self.betaName.setMaximumSize(100,25)
        self.deltaName = QtGui.QLabel("Delta")
        self.deltaName.setMaximumSize(100,25)
        self.itersName = QtGui.QLabel("Iteration")
        self.itersName.setMaximumSize(100,25)
        self.maxText = QtGui.QLineEdit('0')
        self.maxText.setMaximumSize(100,25)
        self.minText = QtGui.QLineEdit('0')
        self.minText.setMaximumSize(100,25)
        self.iters = QtGui.QLineEdit("10")
        self.iters.setMaximumSize(100,25)
        self.beta = QtGui.QLineEdit("1")
        self.beta.setMaximumSize(100,25)
        self.delta = QtGui.QLineEdit("0.01")
        self.delta.setMaximumSize(100,25)

        maxBox = QtGui.QHBoxLayout()
        minBox = QtGui.QHBoxLayout()
        maxBox.addWidget(self.maxLbl)
        maxBox.addWidget(self.maxText)
        minBox.addWidget(self.minLbl)
        minBox.addWidget(self.minText)

        betaBox = QtGui.QHBoxLayout()
        deltaBox = QtGui.QHBoxLayout()
        itersBox = QtGui.QHBoxLayout()
        threshBox = QtGui.QHBoxLayout()
        betaBox.addWidget(self.betaName)
        betaBox.addWidget(self.beta)
        deltaBox.addWidget(self.deltaName)
        deltaBox.addWidget(self.delta)
        itersBox.addWidget(self.itersName)
        itersBox.addWidget(self.iters)
        threshBox.addWidget(self.threshLbl)
        threshBox.addWidget(self.threshLe)
        threshBox.addWidget(self.threshBtn)

        for k in arange(len(self.methodname)):
            self.method.addItem(self.methodname[k])
        vb = QtGui.QVBoxLayout()
        vb.addWidget(self.combo)
        vb.addWidget(self.method)
        vb.addWidget(self.btn)
        vb.addWidget(self.save)
        vb.addLayout(centerBox)
        vb.addLayout(threshBox)
        vb.addWidget(self.sld)
        vb.addWidget(self.lbl)
        vb.addLayout(mdBox)
        vb.addLayout(maxBox)
        vb.addLayout(minBox)
        vb.addLayout(itersBox)
        vb.addLayout(betaBox)
        vb.addLayout(deltaBox)
        self.setLayout(vb)

class QSelect4(QtGui.QWidget):

    def __init__(self):
        super(QSelect4, self).__init__()

        self.initUI()

    def initUI(self):
        self.sld = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        self.sld.setMinimumSize(212,25)
        self.sld.setMaximumSize(212,25)
        self.lcd = QtGui.QLCDNumber(self)
        self.lcd.setMaximumSize(212,50)
        self.combo = QtGui.QComboBox(self)
        self.combo.setMaximumSize(212,25)
        self.combo2 = QtGui.QComboBox(self)
        self.combo2.setMaximumSize(212,25)
        self.combo3 = QtGui.QComboBox(self)
        self.combo3.setMaximumSize(212,25)
        self.lbl1 = QtGui.QLabel("Set the size of the hotspot")
        self.lbl1.setMaximumSize(212,25)
        self.lbl3 = QtGui.QLabel()
        self.lbl3.setMaximumSize(212,50)
        self.lbl3.setText("Set a group number of the \nhot spot")
        for i in arange(5):
            self.combo2.addItem(str(i + 1))
        self.btn = QtGui.QPushButton("Hotspots to a line")
        self.btn.setMaximumSize(212,25)
        self.btn2 = QtGui.QPushButton("Hotspots to a sine curve")
        self.btn2.setMaximumSize(212,25)
        self.btn3 = QtGui.QPushButton("set y")
        self.btn3.setMaximumSize(212,25)
        self.btn4 = QtGui.QPushButton("Clear hotspot data")
        self.btn4.setMaximumSize(212,25)
        
        vb = QtGui.QVBoxLayout()
        vb.addWidget(self.combo)
        vb.addWidget(self.lbl1)
        vb.addWidget(self.lcd)
        vb.addWidget(self.sld)
        vb.addWidget(self.combo3)

        hb1 = QtGui.QVBoxLayout()
        hb1.addWidget(self.lbl3, 0)
        hb1.addWidget(self.combo2)

        vb.addLayout(hb1)
        vb.addWidget(self.btn)
        vb.addWidget(self.btn2)
        vb.addWidget(self.btn3)
        vb.addWidget(self.btn4)
        self.setLayout(vb)

class ConfigurationWindow(QtGui.QWidget):
    def __init__(self):
        super(ConfigurationWindow, self).__init__()
        self.initUI()
        
    def initUI(self):
        self.grid = QtGui.QGridLayout()
        self.setLayout(self.grid)
        self.lbl1 = QtGui.QLabel("Select beamline")
        self.lbl2 = QtGui.QLabel("Enter theta position pv if other than default")
        self.lbl3 = QtGui.QLabel("")
        self.lbl4 = QtGui.QLabel("NOTE: PV for 2-IDE data processed before Feb 2018 is 657")
        self.btn = QtGui.QPushButton("Okay")
        self.txtfield = QtGui.QLineEdit("8")
        self.txtfield2 = QtGui.QLineEdit("663")
        self.button = QtGui.QCheckBox("Bionanoprobe")
        self.button2 = QtGui.QCheckBox("2-IDE")
        self.setWindowTitle('Configuration')
        self.btn.setAutoRepeat(True)

        vb = QtGui.QVBoxLayout()
        vb.addWidget(self.lbl1,1)
        vb.addWidget(self.button,2)
        vb.addWidget(self.button2,3)
        vb2 = QtGui.QVBoxLayout()
        vb2.addWidget(self.lbl2,1)
        vb2.addWidget(self.txtfield,2)
        vb2.addWidget(self.txtfield2,3)
        vb3 = QtGui.QVBoxLayout()
        vb3.addWidget(self.lbl3)
        vb3.addWidget(self.lbl4)
        vb4 = QtGui.QVBoxLayout()
        vb4.addWidget(self.btn)

        self.grid.addLayout(vb,0,0,2,1)
        self.grid.addLayout(vb2,0,1,2,2)
        self.grid.addLayout(vb3,4,0,2,3)
        self.grid.addLayout(vb4,6,1,1,1)

class imageProcess(QtGui.QWidget):
    def __init__(self):
        super(imageProcess, self).__init__()

        self.initUI()

    def initUI(self):
        self.xSize = 20
        self.ySize = 20

        self.xUpBtn = QtGui.QPushButton("x: +")
        self.xUpBtn.setMaximumSize(75,25)
        self.xUpBtn.clicked.connect(self.xUp)
        self.xDownBtn = QtGui.QPushButton("x: -")
        self.xDownBtn.setMaximumSize(75,25)
        self.xDownBtn.clicked.connect(self.xDown)
        self.yUpBtn = QtGui.QPushButton("y: +")
        self.yUpBtn.setMaximumSize(75,25)
        self.yUpBtn.clicked.connect(self.yUp)
        self.yDownBtn = QtGui.QPushButton("y: -")
        self.yDownBtn.setMaximumSize(75,25)
        self.yDownBtn.clicked.connect(self.yDown)
        self.bgBtn = QtGui.QPushButton("Bg Value")
        self.bgBtn.setMaximumSize(100,25)
        self.delHotspotBtn = QtGui.QPushButton("Delete HS")
        self.delHotspotBtn.setMaximumSize(100,25)
        self.normalizeBtn = QtGui.QPushButton("Normalize")
        self.normalizeBtn.setMaximumSize(100,25)
        self.cutBtn = QtGui.QPushButton("Cut")
        self.cutBtn.setMaximumSize(100,25)
        self.gaussian33Btn = QtGui.QPushButton("3*3 gauss")
        self.gaussian33Btn.setMaximumSize(100,25)
        self.gaussian55Btn = QtGui.QPushButton("5*5 gauss")
        self.gaussian55Btn.setMaximumSize(100,25)
        self.captureBackground = QtGui.QPushButton("copy Bg")
        self.captureBackground.setMaximumSize(100,25)
        self.setBackground = QtGui.QPushButton("Set Bg")
        self.setBackground.setMaximumSize(100,25)
        self.deleteProjection = QtGui.QPushButton("Delete Frame")
        self.deleteProjection.setMaximumSize(100,25)
        self.testButton = QtGui.QPushButton("test btn")
        self.testButton.setMaximumSize(100,25)
        self.shift_img_left = QtGui.QPushButton("shft img left")
        self.shift_img_left.setMaximumSize(100,25)
        self.shift_img_right = QtGui.QPushButton("shft img right")
        self.shift_img_right.setMaximumSize(100,25)
        self.shift_img_up = QtGui.QPushButton("shft img up")
        self.shift_img_up.setMaximumSize(100,25)
        self.shift_img_down = QtGui.QPushButton("shft img down")
        self.shift_img_down.setMaximumSize(100,25)

        self.shift_all_left = QtGui.QPushButton("shft all left")
        self.shift_all_left.setMaximumSize(100,25)
        self.shift_all_right = QtGui.QPushButton("shft all right")
        self.shift_all_right.setMaximumSize(100,25)
        self.shift_all_up = QtGui.QPushButton("shft all up")
        self.shift_all_up.setMaximumSize(100,25)
        self.shift_all_down = QtGui.QPushButton("shift all down")
        self.shift_all_down.setMaximumSize(100,25)

        self.xSizeTxt = QtGui.QLineEdit(str(self.xSize))
        self.xSizeTxt.setMaximumSize(50,25)
        self.ySizeTxt = QtGui.QLineEdit(str(self.ySize))
        self.ySizeTxt.setMaximumSize(50,25)
        self.combo1 = QtGui.QComboBox()
        self.combo1.setMaximumSize(212,25)
        self.combo2 = QtGui.QComboBox()
        self.combo2.setMaximumSize(212,25)

        hb1 = QtGui.QHBoxLayout()
        hb1.addWidget(self.xUpBtn)
        hb1.addWidget(self.xDownBtn)
        hb1.addWidget(self.xSizeTxt)
        
        hb2 = QtGui.QHBoxLayout()
        hb2.addWidget(self.yUpBtn)
        hb2.addWidget(self.yDownBtn)
        hb2.addWidget(self.ySizeTxt)

        hb3 = QtGui.QHBoxLayout()
        hb3.addWidget(self.shift_img_up)

        hb4 = QtGui.QHBoxLayout()
        hb4.addWidget(self.shift_img_left)
        hb4.addWidget(self.shift_img_right)

        hb5 = QtGui.QHBoxLayout()
        hb5.addWidget(self.shift_img_down)

        hb6 = QtGui.QHBoxLayout()
        hb6.addWidget(self.shift_all_up)

        hb7 = QtGui.QHBoxLayout()
        hb7.addWidget(self.shift_all_left)
        hb7.addWidget(self.shift_all_right)

        hb8 = QtGui.QHBoxLayout()
        hb8.addWidget(self.shift_all_down)

        hb9 = QtGui.QHBoxLayout()
        hb9.addWidget(self.bgBtn, )
        hb9.addWidget(self.delHotspotBtn)

        hb10 = QtGui.QHBoxLayout()
        hb10.addWidget(self.normalizeBtn)
        hb10.addWidget(self.cutBtn)

        hb11 = QtGui.QHBoxLayout()
        hb11.addWidget(self.gaussian33Btn)
        hb11.addWidget(self.gaussian55Btn)

        hb12 = QtGui.QHBoxLayout()
        hb12.addWidget(self.captureBackground)
        hb12.addWidget(self.setBackground)

        hb13 = QtGui.QHBoxLayout()
        hb13.addWidget(self.deleteProjection)
        hb13.addWidget(self.testButton)

        vb1 = QtGui.QVBoxLayout()
        vb1.addLayout(hb1)
        vb1.addLayout(hb2)

        vb2 = QtGui.QVBoxLayout()
        vb2.addLayout(hb3)
        vb2.addLayout(hb4)
        vb2.addLayout(hb5)
        vb2.addLayout(hb6)
        vb2.addLayout(hb7)
        vb2.addLayout(hb8)
        vb2.addLayout(hb9)
        vb2.addLayout(hb10)
        vb2.addLayout(hb11)
        vb2.addLayout(hb12)
        vb2.addLayout(hb13)

        vb3 = QtGui.QVBoxLayout()
        vb3.addWidget(self.combo1)
        vb3.addWidget(self.combo2)
        vb3.addLayout(vb1)
        vb3.addLayout(vb2)

        self.setLayout(vb3)

    def changeXSize(self):
        self.xSize = int(self.xSizeTxt.text())

    def changeYSize(self):
        self.ySize = int(self.ySizeTxt.text())

    def xUp(self):
        self.changeXSize()
        self.changeYSize()
        self.xSize += 2
        self.xSizeTxt.setText(str(self.xSize))

    def xDown(self):
        self.changeXSize()
        self.changeYSize()
        self.xSize -= 2
        self.xSizeTxt.setText(str(self.xSize))

    def yUp(self):
        self.changeXSize()
        self.changeYSize()
        self.ySize += 2
        self.ySizeTxt.setText(str(self.ySize))

    def yDown(self):
        self.changeXSize()
        self.changeYSize()
        self.ySize -= 2
        self.ySizeTxt.setText(str(self.ySize))


class IView(pg.GraphicsLayoutWidget):

    def __init__(self):
        super(IView, self).__init__()

        self.initUI()
        self.hotSpotNumb = 0

    def initUI(self):
        self.show()
        self.p1 = self.addPlot(enableMouse=False, rowspan=1, colspan=1)
        self.projView = MyImageItem.ImageItem()
        self.projView.rotate(0)
        self.p1.addItem(self.projView)

    def keyPressEvent(self, ev):

        if ev.key() == QtCore.Qt.Key_Right:
            self.getMousePos()
            self.shiftnumb = 1
            self.shift()
            self.projView.setImage(self.copy)
            self.regShift[self.numb2] += self.shiftnumb

        if ev.key() == QtCore.Qt.Key_Left:
            self.getMousePos()
            self.shiftnumb = -1
            self.shift()
            self.projView.setImage(self.copy)
            self.regShift[self.numb2] += self.shiftnumb

    def getMousePos(self):
        numb = self.projView.iniY
        self.numb2 = int(numb / 10)

    def shift(self):
        self.copy = self.projData
        self.copy[self.numb2 * 10:self.numb2 * 10 + 10, :] = np.roll(self.copy[self.numb2 * 10:self.numb2 * 10 + 10, :],
                                                                     self.shiftnumb, axis=1)

    def getShape(self):
        self.regShift = zeros(self.projData.shape[0], dtype=int)

class IView2(pg.GraphicsLayoutWidget):

    def __init__(self):
        super(IView2, self).__init__()

        self.initUI()
        self.boxSize = 20
        self.hotSpotNumb = 0
        self.xSize = 20
        self.ySize = 20

    def initUI(self):
        self.show()
        self.p1 = self.addPlot(enableMouse=False, rowspan=1, colspan=1)
        self.projView = MyImageItem.ImageItem()
        self.projView.rotate(-90)
        self.projView.iniX = 0
        self.projView.iniY = 0
        self.ROI = pg.ROI([self.projView.iniX, self.projView.iniY], [20, 20])
        self.p1.addItem(self.projView)
        self.p1.addItem(self.ROI)

    def mouseReleaseEvent(self, ev):
        self.ROI.setPos([self.projView.iniX - self.xSize / 2, -self.projView.iniY - self.ySize / 2])

    def keyPressEvent(self, ev):
        if ev.key() == QtCore.Qt.Key_N:
            if self.hotSpotNumb < self.data.shape[0]:
                print "n"
                print "Total projections", self.data.shape[
                    0], "current position", self.hotSpotNumb + 1, "group number", self.hotSpotSetNumb + 1
                self.posMat[self.hotSpotSetNumb, self.hotSpotNumb, 0] = self.projView.iniY
                self.posMat[self.hotSpotSetNumb, self.hotSpotNumb, 1] = self.projView.iniX
                print self.projView.iniX, self.projView.iniY

                self.hotSpotNumb += 1
                if self.hotSpotNumb < self.data.shape[0]:
                    self.projView.setImage(self.data[self.hotSpotNumb, :, :])
                else:
                    print "This is the last projection"

        if ev.key() == QtCore.Qt.Key_S:
            self.posMat[self.hotSpotSetNumb, self.hotSpotNumb, 0] = 0
            self.posMat[self.hotSpotSetNumb, self.hotSpotNumb, 1] = 0
            if self.hotSpotNumb < self.data.shape[0] - 1:
                self.hotSpotNumb += 1
                self.projView.setImage(self.data[self.hotSpotNumb, :, :])

class SinoWidget(pg.QtGui.QWidget):
    def __init__(self):
        super(SinoWidget, self).__init__()
        self.initUI()

    def initUI(self):
        self.show()
        hb1 = QtGui.QHBoxLayout()
        self.view = IView()
        self.hist = pg.HistogramLUTWidget()
        self.hist.setImageItem(self.view.projView)
        self.hist.setMinimumSize(120,120)
        self.hist.setMaximumWidth(120)
        hb1.addWidget(self.view)
        hb1.addWidget(self.hist, 10)
        self.setLayout(hb1)

class IView3(QtGui.QWidget):
    def __init__(self):
        super(IView3, self).__init__()

        self.initUI()

    def initUI(self):
        self.show()
        hb3 = QtGui.QHBoxLayout()
        self.file_name_title = QtGui.QLabel("_")
        lbl1 = QtGui.QLabel("x pos:")
        lbl1.setAlignment(QtCore.Qt.AlignRight)
        self.lbl2 = QtGui.QLabel("")
        self.lbl2.setMaximumSize(50,25)
        self.lbl2.setAlignment(QtCore.Qt.AlignRight)
        lbl3 = QtGui.QLabel("y pos:")
        lbl3.setAlignment(QtCore.Qt.AlignRight)
        self.lbl4 = QtGui.QLabel("")
        self.lbl4.setAlignment(QtCore.Qt.AlignRight)
        self.lbl4.setMaximumSize(50,25)
        self.lbl5 = QtGui.QLabel("Angle")
        self.lbl5.setMaximumSize(75, 25)
        btn1 = QtGui.QPushButton("position")
        hb3.addWidget(self.file_name_title)
        hb3.addWidget(lbl1)
        hb3.addWidget(self.lbl2)
        hb3.addWidget(lbl3)
        hb3.addWidget(self.lbl4)
        hb3.addWidget(btn1)

        btn1.clicked.connect(self.updatePanel)

        hb2 = QtGui.QHBoxLayout()
        hb1 = QtGui.QHBoxLayout()
        vb1 = QtGui.QVBoxLayout()
        self.view = IView2()
        self.sld = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        self.lcd = QtGui.QLCDNumber(self)
        self.hist = pg.HistogramLUTWidget()
        self.hist.setImageItem(self.view.projView)
        self.hist.setMinimumSize(120,102)
        self.hist.setMaximumWidth(120)

        hb2.addWidget(self.lbl5)
        hb2.addWidget(self.lcd)
        hb2.addWidget(self.sld)
        vb1.addLayout(hb3)
        vb1.addWidget(self.view)
        vb1.addLayout(hb2)
        hb1.addLayout(vb1)
        hb1.addWidget(self.hist, 10)
        self.setLayout(hb1)

    def keyPressEvent(self, ev):
        if ev.key() == QtCore.Qt.Key_N:
            self.sld.setValue(self.sld.value + 1)

    def updatePanel(self):
        self.lbl2.setText(str(np.round(self.view.data.projView.iniX,4)))
        self.lbl4.setText(str(np.round(self.view.data.projView.iniY,4)))

#########################
def main():
    app = QtGui.QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
