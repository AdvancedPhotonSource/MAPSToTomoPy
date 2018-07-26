# -*- coding: utf-8 -*-
# !/usr/bin/python

import sys
import os
from sys import platform
import numpy as np
import pyqtgraph as pg
from pyqtgraph import QtGui, QtCore
import MyImageItem
from pylab import *

'''general Notes:
Iview1-3 generate graphics such as the projections,
sinograms and the graphic on the right edge on all of the tabs 
i.e IView3 is responsible for the graph on the right edge. 

Qselect1-4 are responsible for the base button layouts 

the widgets in the Example class calls Qselect and either renames buttons 
or hides them completely based on the required task for that tab. 

Current issues: 
1) expanding main window doesnt expand graphs proportionally 
'''

class Example(QtGui.QMainWindow):
	def __init__(self):
		super(Example, self).__init__()
		self.initUI()
	def initUI(self):

		exitAction = QtGui.QAction('Exit', self)
		exitAction.triggered.connect(self.close)
		exitAction.setShortcut('Ctrl+Q')

		closeAction = QtGui.QAction('Quit', self)
		closeAction.triggered.connect(sys.exit)
		closeAction.setShortcut('Ctrl+X')

		openFileAction = QtGui.QAction('Open File', self)
		openFileAction.triggered.connect(self.openfile)

		selectElementAction = QtGui.QAction('Select Element', self)
		selectElementAction.triggered.connect(self.selectElement)

		selectFilesAction = QtGui.QAction('Select Files', self)
		selectFilesAction.triggered.connect(self.selectFilesShow)

		xCorAction = QtGui.QAction("Cross Correlation", self)
		xCorAction.triggered.connect(self.CrossCorrelation_test)
		
		phaseXCorAction = QtGui.QAction("Phase Correlation", self)
		phaseXCorAction.triggered.connect(self.CrossCorrelation_test)

		runCenterOfMassAction = QtGui.QAction("run center of mass action", self)
		runCenterOfMassAction.triggered.connect(self.centerOfMassWindow)

		matcherAction = QtGui.QAction("match template", self)
		matcherAction.triggered.connect(self.match_window)
		
		configurationAction = QtGui.QAction("Configuration Window", self)
		configurationAction.triggered.connect(self.configurationWindow)

		openTiffFolderAction = QtGui.QAction("Open Tiff Folder", self)
		# openTiffFolderAction.triggered.connect(self.openTiffFolder)
		sinogramAction = QtGui.QAction('Sinogram', self)
		# sinogramAction.triggered.connect(self.sinogram)
		saveImageAction = QtGui.QAction('Save Projections', self)
		# saveImageAction.triggered.connect(self.saveImage)
		saveThetaTxtAction = QtGui.QAction("Save Theta Postion as txt", self)
		# saveThetaTxtAction.triggered.connect(self.saveThetaTxt)
		convertAction = QtGui.QAction('Save data in memory', self)
		# convertAction.triggered.connect(self.convert)
		saveSinogramAction = QtGui.QAction('Save Sinogram', self)
		# saveSinogramAction.triggered.connect(self.saveSinogram)
		runReconstructAction = QtGui.QAction("Reconstruction", self)
		# runReconstructAction.triggered.connect(self.runReconstruct)
		selectImageTagAction = QtGui.QAction("Select Image Tag", self)
		# selectImageTagAction.triggered.connect(self.selectImageTag)
		alignFromTextAction = QtGui.QAction("Alignment from Text", self)
		# alignFromTextAction.triggered.connect(self.alignFromText)
		alignFromText2Action = QtGui.QAction("Alignment from Text2", self)
		# alignFromText2Action.triggered.connect(self.alignFromText2)
		saveAlignToTextAction = QtGui.QAction("Save Alignment information to text", self)
		# saveAlignToTextAction.triggered.connect(self.saveAlignToText)
		restoreAction = QtGui.QAction("Restore", self)
		# restoreAction.triggered.connect(self.restore)
		readConfigAction = QtGui.QAction("Read configuration file", self)
		# readConfigAction.triggered.connect(self.readConfigFile)
		alignCenterOfMassAction = QtGui.QAction("Align by fitting center of mass position into sine curve", self)
		# alignCenterOfMassAction.triggered.connect(self.alignCenterOfMass)
		exportDataAction = QtGui.QAction("export data", self)
		# exportDataAction.triggered.connect(self.export_data)
		runTransRecAction = QtGui.QAction("Transmission Recon", self)
		# runTransRecAction.triggered.connect(self.runTransReconstruct)
		saveHotSpotPosAction = QtGui.QAction("Save Hot Spot Pos", self)
		# saveHotSpotPosAction.triggered.connect(self.saveHotSpotPos)
		alignHotSpotPosAction = QtGui.QAction("Align Hot Spot pos", self)
		# alignHotSpotPosAction.triggered.connect(self.alignHotSpotPos1)
		reorderAction = QtGui.QAction("Reorder", self)
		# reorderAction.triggered.connect(self.reorder_matrix)
		wienerAction = QtGui.QAction("Wiener", self)
		# wienerAction.triggered.connect(self.ipWiener)
		reorderAction = QtGui.QAction("Reorder", self)
		# reorderAction.triggered.connect(self.reorder_matrix)
		externalImageRegAction = QtGui.QAction("External Image Registaration", self)
		# externalImageRegAction.triggered.connect(self.externalImageReg)
		
		self.frame = QtGui.QFrame()
		self.vl = QtGui.QVBoxLayout()

		self.tab_widget = QtGui.QTabWidget()
		self.tab_widget.addTab(self.createImageProcessWidget(), unicode("Image Process"))
		self.tab_widget.addTab(self.createSaveHotspotWidget(),unicode("Alignment"))
		self.tab_widget.addTab(self.createSinoWidget(), unicode("Sinogram"))
		self.tab_widget.addTab(self.createReconWidget(), unicode("Reconstruction"))
		self.tab_widget.currentChanged.connect(self.tab1manual)

		self.vl.addWidget(self.tab_widget)
		self.vl.addWidget(self.createMessageWidget())

		self.frame.setLayout(self.vl)
		self.setCentralWidget(self.frame)
		self.tab_widget.setDisabled(False)

		## Top menu bar [file   Convert Option    Alignment   After saving in memory]
		menubar = self.menuBar()
		self.fileMenu = menubar.addMenu('&File')
		self.fileMenu.addAction(configurationAction)
		self.fileMenu.addAction(readConfigAction)
		self.fileMenu.addAction(openFileAction)
		self.fileMenu.addAction(openTiffFolderAction)
		self.fileMenu.addAction(exitAction)
		self.fileMenu.addAction(closeAction)

		self.optionMenu = menubar.addMenu('Convert Option')
		self.optionMenu.addAction(selectFilesAction)
		self.optionMenu.addAction(selectImageTagAction)
		self.optionMenu.addAction(selectElementAction)
		self.optionMenu.addAction(convertAction)
		self.optionMenu.setDisabled(False)

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
		self.alignmentMenu.setDisabled(False)

		self.afterConversionMenu = menubar.addMenu('After saving data in memory')
		self.afterConversionMenu.addAction(saveImageAction)
		self.afterConversionMenu.addAction(saveThetaTxtAction)
		self.afterConversionMenu.addAction(saveSinogramAction)
		self.afterConversionMenu.addAction(reorderAction)
		self.afterConversionMenu.setDisabled(False)

		add =0
		if platform == "win32":
		    add = 50
		self.setGeometry(add,add, 1100+add,500+add)
		self.setWindowTitle('Maps_To_Tomopy')    
		self.show()

	def tab1manual(self):
		'''tab1manual: Displays instructions for how to use the manual hotspot alignment tool
		in the message box.
		'''
		if self.tab_widget.currentIndex() == 1:
		    self.lbl.setText('click hotspot, press N to advance frame or press S to skip frame')
		else:
		    self.lbl.setText("")
	def createMessageWidget(self):
		'''create message box widget. return group
		'''
		GridStartVal = '2'
		vbox = QtGui.QVBoxLayout()
		hbox = QtGui.QHBoxLayout()
		hbox2 = QtGui.QHBoxLayout()
		self.lbl = QtGui.QLineEdit("Step 1) Open configuration file", self)
		self.lbl2 = QtGui.QLineEdit()
		self.lbl2.setText(os.getcwd())
		self.directoryButton = QtGui.QPushButton("Change Directory")
		hbox.addWidget(QtGui.QLabel("Message"))
		hbox.addWidget(self.lbl)
		hbox2.addWidget(QtGui.QLabel("Set Directory"))
		hbox2.addWidget(self.lbl2)
		hbox2.addWidget(self.directoryButton)
		vbox.addLayout(hbox)
		vbox.addLayout(hbox2)
		messageGroup = QtGui.QGroupBox("Message Box")
		messageGroup.setLayout(vbox)

		if self.tab_widget.currentIndex() == 1:
			self.lbl.setText("click hotspot, press n or press S to skip frame")
		else: self.lbl.setText("")
		return messageGroup

	## bottom menu bar [Image Process   Hotspot    Sinogram   Reconstruction]
	def createImageProcessWidget(self):
		'''create an Image process group. returns the group
		'''
		self.imgProcessControl = imageProcess()
		self.imgProcess = IView3()

		imgProcessBox = QtGui.QHBoxLayout()
		imgProcessBox.addWidget(self.imgProcessControl)
		imgProcessBox.addWidget(self.imgProcess, 10)
		imgProcessGroup = QtGui.QGroupBox("Image Process")
		imgProcessGroup.setLayout(imgProcessBox)
		return imgProcessGroup

	def createSaveHotspotWidget(self):
		'''create a saving hotspot position group. returns the group
		'''
		self.projViewControl = QSelect4()
		self.projView = IView3()

		self.boxSize = 20
		projViewBox = QtGui.QHBoxLayout()
		projViewBox.addWidget(self.projViewControl)
		projViewBox.addWidget(self.projView, 10)
		projViewGroup = QtGui.QGroupBox(" HotSpot")
		projViewGroup.setLayout(projViewBox)
		return projViewGroup   

	def createSinoWidget(self):
		'''create a sinogram group for sinogram tab. returns sinogram group
		'''
		self.sino = QSelect2()
		self.sinoView = SinoWidget()

		sinoBox = QtGui.QHBoxLayout()
		sinoBox.addWidget(self.sino)
		sinoBox.addWidget(self.sinoView, 10)
		sinoGroup = QtGui.QGroupBox("Sinogram")
		sinoGroup.setLayout(sinoBox)
		return sinoGroup

	def createReconWidget(self):
		'''create a reconstruction group for reconstruction tab. returns reconstruction group
		'''
		self.recon = QSelect3()
		self.recon.sld.setVisible(False)
		self.reconView = IView3()

		self.reconView.view.ROI.setVisible(False)
		reconBox = QtGui.QHBoxLayout()
		reconBox.addWidget(self.recon)
		reconBox.addWidget(self.reconView, 10)
		reconGroup = QtGui.QGroupBox("Reconstruction")
		reconGroup.setLayout(reconBox)
		return reconGroup

	def createProjWidget(self):
		'''create a projection group for projection tab. returns projection group
		'''
		self.projection = QSelect2()
		self.projectionView = pg.ImageView()

		projectionBox = QtGui.QHBoxLayout()
		projectionBox.addWidget(self.projection)
		projectionBox.addWidget(self.projectionView, 10)
		projectionGroup = QtGui.QGroupBox("Projections")
		projectionGroup.setLayout(projectionBox)
		return projectionGroup

	def configurationWindow(self):
		self.conf = QtGui.QWidget()
		self.conf.grid = QtGui.QGridLayout()
		self.conf.setLayout(self.conf.grid)
		self.conf.lbl1 = QtGui.QLabel("Select beamline")
		self.conf.lbl2 = QtGui.QLabel("Enter PV if other than default")
		self.conf.lbl3 = QtGui.QLabel("NOTE: PV for 2-IDE data processed before Feb 2018 is 657")
		self.conf.btn = QtGui.QPushButton("Okay")
		self.conf.txtfield = QtGui.QLineEdit("8")
		self.conf.txtfield2 = QtGui.QLineEdit("663")
		self.conf.button = QtGui.QCheckBox("Bionanoprobe")
		self.conf.button2 = QtGui.QCheckBox("2-IDE")

		vb = QtGui.QVBoxLayout()
		vb.addWidget(self.conf.lbl1,1)
		vb.addWidget(self.conf.button,2)
		vb.addWidget(self.conf.button2,3)
		vb2 = QtGui.QVBoxLayout()
		vb2.addWidget(self.conf.lbl2,1)
		vb2.addWidget(self.conf.txtfield,2)
		vb2.addWidget(self.conf.txtfield2,3)
		vb3 = QtGui.QVBoxLayout()
		vb3.addWidget(self.conf.lbl3)
		vb3.addWidget(self.conf.btn)

		self.conf.grid.addLayout(vb,0,0,2,1)
		self.conf.grid.addLayout(vb2,0,1,2,1)
		self.conf.grid.addLayout(vb3,4,0,2,2)
		self.conf.setWindowTitle('Configuration')
		self.conf.show()
		

	def centerOfMassWindow(self):
		''' Creates the window for alignment with center of mass 
		'''
		self.comer = QSelect3()
		self.comer.setWindowTitle("Center of Mass window")
		self.comer.btn.setText("Center of Mass")
		self.comer.method.setVisible(False)
		self.comer.save.setVisible(True)
		self.comer.btn.clicked.connect(self.runCenterOfMass)
		self.comer.save.setText("Restore")
		self.comer.show()

	def showImageProcess(self):
		'''loads window for image process
		'''
		self.tab_widget.removeTab(0)
		self.tab_widget.insertTab(0, self.createImageProcessWidget(), unicode("Image Process"))
		self.testtest = pg.ImageView()

	def showSinogram(self):
		'''loads sinogram tab
		'''
		self.tab_widget.removeTab(2)
		self.tab_widget.insertTab(2, self.createSinoWidget(), unicode("Sinogram"))
		self.sino.show()
		self.sino.btn.setText("center of mass")
		self.sino.lcd.display(5)
		self.sino.sld.valueChanged.connect(self.sino.lcd.display)
		self.sinoView.show()

	#Dummy functions needed to display toolbar dropdown menus 
	def openfile(self):
		self.selectFiles()

	def selectFiles(self):
		self.filecheck = QSelect()
		self.filecheck.setWindowTitle("Select files")
		self.optionMenu.setEnabled(True)
		self.filecheck.btn2.setVisible(True)
		self.filecheck.btn2.clicked.connect(self.selectImageTag)
		self.filecheck.btn3.clicked.connect(self.selectElementShow)
		self.selectElement()

	def selectElement(self):
		self.element = QSelect()
		self.element.setWindowTitle("Select Element")
		self.element.setVisible(False)
		self.element.btn2.setText("Deselect All")
		self.element.btn.setText("set Element")
		self.element.btn3.setVisible(False)

	def selectImageTag(self):
		self.sit = AlignWindow()
		self.sit.setWindowTitle("Seletect Image Tag from h5 file")
		self.sit.btn.setText("Set")
		self.sit.btn2.setVisible(False)
		self.sit.btn.clicked.connect(self.setImageTag)

	def selectFilesShow(self):
		self.filecheck.setVisible(True)

	def selectElementShow(self):
		self.element.setVisible(True)

	def convert(self):
		self.afterConversionMenu.setDisabled(False)

	def CrossCorrelation_test(self):
		self.xcor = AlignWindow()
		self.xcor.setWindowTitle("CrossCorrelation Window")
		self.xcor.btn.setText("Cross Correlation")
		self.xcor.btn2.setText("Restore")      
		self.xcor.btn.clicked.connect(self.xCor)
		self.xcor.method.setVisible(False)
		self.xcor.show()

	def match_window(self):
		self.matcher = AlignWindow()
		self.matcher.setWindowTitle("Match template window")
		self.matcher.btn.setText("Match Template")
		self.matcher.btn2.setText("Restore")
		self.matcher.show()

	def xCor(self):
		self.alignmentDone()

	def runCenterOfMass(self):
		self.centerOfMass()
		self.lbl.setText("Center of Mass: ")

	def openTiffFolder(self): pass
	def sinogram(self): pass
	def saveImage(self): pass
	def saveThetaTxt(self): pass
	def convert(self): pass
	def saveSinogram(self): pass
	def runReconstruct(self): pass
	def selectImageTag(self): pass
	def alignFromTex(self): pass
	def alignFromText2(self): pass
	def saveAlignToText(self): pass
	def restore(self): pass
	def readConfigFile(self): pass
	def alignCenterOfMass(self): pass
	def export_data(self): pass
	def runTransReconstruct(self): pass
	def saveHotSpotPos(self): pass
	def alignHotSpotPos1(self): pass
	def alignHotSpotPos2(self): pass
	def alignHotSpotPos3(self): pass
	def alignHotSpotPos3_3(self): pass
	def alignHotSpotPos3_4(self): pass
	def alignHotSpotPos4(self): pass
	def ipWiener(self): pass
	def reorder_matrix(self): pass
	def externalImageReg(self): pass

	def fitCenterOfMass(self, ang): pass
	#!!!!!!!!!! there are two functions with same name in MAPSToTomoPy
	# def fitCenterOfMass(self, x): 
	def fitCenterOfMass2(self, x): pass
	def centerOfMass(self): pass
	def runCenterOfMass2(self): pass
	def alignCenterOfMass(self): pass
	def alignCenterOfMass2(self): pass
	def prexCor(self): pass
	def phasecorrelate(self, a, b): pass
	def xcorrelate(self, a, b): pass
	def match(self): pass
	def edgegauss(self, imagey, sigma=4): pass
	def showSaveHotSpotPos(self): pass
	def clearHotSpotData(self): pass
	def hotspotProjChanged(self): pass
	def hotSpotProjChanged(self): pass
	def boxSizeChange(self): pass
	def hotSpotSetChanged(self): pass
	def nextHotSpotPos(self): pass
	def alignHotSpotY(self): pass
	def alignHotSpotPos1(self): pass
	def imgProcessProjChanged(self): pass
	def file_name_update(self, view): pass
	def imgProcessProjShow(self): pass
	def imgProcessBoxSizeChange(self): pass
	def ipBg(self): pass
	def ipDelHotspot(self): pass
	def ipNormalize(self): pass
	def ipCut(self): pass
	def gauss2D(self, shape=(3, 3), sigma=0.5): pass
	def gauss55(self): pass
	def gauss33(self): pass
	def gaussian(self, height, center_x, center_y, width_x, width_y): pass
	def moments(self, data): pass
	def fitgaussian(self, data): pass
	def reconMultiply(self): pass
	def reconDivide(self): pass
	def updateRecon(self): pass
	def threshold(self): pass
	def reconstruct(self): pass
	def cboxClicked(self): pass
	def circular_mask(self): pass
	def saveRecTiff(self): pass
	def selectImageTag_image(self): pass
	def setImageTag(self): pass
	def deselectAllElement(self): pass
	def setElement(self): pass
	def SendNumFiles(self): pass
	def convertTiff2Array(self): pass
	def convert2array(self): pass
	def multiplier(self): pass
	def divider(self): pass
	def normalize(self): pass
	def sinoShift(self): pass
	def updateImages(self): pass











'''Qselect1-4 used for base button layout'''

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
	def __init__(self):
		super(QSelect, self).__init__()
		self.initUI()

	def initUI(self):
		names = list()
		for i in arange(130):
			names.append("")
		self.grid = QtGui.QGridLayout()
		self.lbl = QtGui.QLabel()
		self.lbl2 = QtGui.QLabel()
		self.lbl.setText("closing this window won't affect your selection of the files")
		self.lbl2.setText("You should convert the files in order to generate sinogram or reconstructed data")
		self.btn = QtGui.QPushButton('Save Data in Memory', self)
		self.btn2 = QtGui.QPushButton("set Image Tag", self)
		self.btn3 = QtGui.QPushButton("set Element", self)

		j = 0
		pos = list()
		for y in arange(13):
			for x in arange(10):
				pos.append((x, y))

		self.button = list()
		for i in names:
			self.button.append(QtGui.QCheckBox(i))
			self.grid.addWidget(self.button[j], pos[j][0], pos[j][1])
			j = j + 1
		self.setLayout(self.grid)

		self.vb = QtGui.QVBoxLayout()
		self.vb2 = QtGui.QVBoxLayout()

		self.vb.addWidget(self.lbl, 11)
		self.vb.addWidget(self.lbl2, 12)

		hb = QtGui.QHBoxLayout()
		hb.addWidget(self.btn2)
		hb.addWidget(self.btn3)
		self.vb2.addLayout(hb)
		self.vb2.addWidget(self.btn)

		self.grid.addLayout(self.vb, 11, 0, 1, 10)
		self.grid.addLayout(self.vb2, 13, 3, 1, 2)

		self.move(100, 100)
		self.setWindowTitle('Calculator')
		self.show()

class QSelect2(QtGui.QWidget):

	def __init__(self):
		super(QSelect2, self).__init__()
		self.initUI()

	def initUI(self):
		self.sld = QtGui.QSlider(QtCore.Qt.Horizontal, self)
		self.lcd = QtGui.QLCDNumber(self)
		self.combo = QtGui.QComboBox(self)
		self.btn = QtGui.QPushButton('Click2')
		self.btn.setText("Sinogram")
		self.btn2 = QtGui.QPushButton("shift data")
		self.btn3 = QtGui.QPushButton("X 10")
		self.btn4 = QtGui.QPushButton("/ 10")
		hb = QtGui.QHBoxLayout()
		hb.addWidget(self.btn3)
		hb.addWidget(self.btn4)
		self.btn3.setVisible(False)
		self.btn4.setVisible(False)
		self.lbl = QtGui.QLabel()
		self.lbl.setText("")
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
		self.method = QtGui.QComboBox(self)
		self.btn = QtGui.QPushButton('Click2')
		self.save = QtGui.QPushButton("Save tiff files")
		self.save.setHidden(True)
		self.btn.setText("Sinogram")
		self.sld = QtGui.QSlider(QtCore.Qt.Horizontal, self)
		self.lcd = QtGui.QLineEdit("0")
		self.lbl = QtGui.QLabel()
		self.cbox = QtGui.QCheckBox("")
		self.lbl2 = QtGui.QLabel("Center")
		self.lbl.setText("")

		self.threshLbl = QtGui.QLabel("threshold")
		self.threshLe = QtGui.QLineEdit("")
		self.threshBtn = QtGui.QPushButton("Apply")

		centerBox = QtGui.QHBoxLayout()
		centerBox.addWidget(self.cbox)
		centerBox.addWidget(self.lbl2)
		centerBox.addWidget(self.lcd)
		self.lcd.setEnabled(False)
		self.methodname = ["mlem", "gridrec", "art", "pml_hybrid", "pml_quad"]

		self.mulBtn = QtGui.QPushButton("x 10")
		self.divBtn = QtGui.QPushButton("/ 10")
		mdBox = QtGui.QHBoxLayout()
		mdBox.addWidget(self.mulBtn)
		mdBox.addWidget(self.divBtn)

		self.maxLbl = QtGui.QLabel("Max")
		self.minLbl = QtGui.QLabel("Min")
		self.maxText = QtGui.QLineEdit()
		self.minText = QtGui.QLineEdit()

		maxBox = QtGui.QHBoxLayout()
		minBox = QtGui.QHBoxLayout()
		maxBox.addWidget(self.maxLbl)
		maxBox.addWidget(self.maxText)
		minBox.addWidget(self.minLbl)
		minBox.addWidget(self.minText)

		self.betaName = QtGui.QLabel("Beta")
		self.deltaName = QtGui.QLabel("Delta")
		self.itersName = QtGui.QLabel("Iteration")
		self.beta = QtGui.QLineEdit("1")
		self.delta = QtGui.QLineEdit("0.01")
		self.iters = QtGui.QLineEdit("10")

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
		self.lcd = QtGui.QLCDNumber(self)
		self.combo = QtGui.QComboBox(self)
		self.combo2 = QtGui.QComboBox(self)
		self.combo3 = QtGui.QComboBox(self)
		self.lbl1 = QtGui.QLabel("Set the size of the hotspot")
		self.lbl3 = QtGui.QLabel()
		self.lbl3.setText("Set a group number of the hot spot")
		for i in arange(5):
		    self.combo2.addItem(str(i + 1))
		self.btn = QtGui.QPushButton("Hotspots to a line")
		self.btn2 = QtGui.QPushButton("Hotspots to a sine curve")
		self.btn3 = QtGui.QPushButton("set y")
		self.btn4 = QtGui.QPushButton("Clear hotspot data")

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

class imageProcess(QtGui.QWidget):
	def __init__(self):
		super(imageProcess, self).__init__()
		self.initUI()

	def initUI(self):
		self.xSize = 20
		self.ySize = 20

		self.bgBtn = QtGui.QPushButton("Bg Value")
		self.delHotspotBtn = QtGui.QPushButton("Delete HS")
		self.normalizeBtn = QtGui.QPushButton("Normalize")
		self.cutBtn = QtGui.QPushButton("Cut")
		self.gaussian33Btn = QtGui.QPushButton("3*3 gauss")
		self.gaussian55Btn = QtGui.QPushButton("5*5 gauss")
		self.xUpBtn = QtGui.QPushButton("x: +")
		self.xUpBtn.clicked.connect(self.xUp)
		self.xDownBtn = QtGui.QPushButton("x: -")
		self.xDownBtn.clicked.connect(self.xDown)
		self.yUpBtn = QtGui.QPushButton("y: +")
		self.yUpBtn.clicked.connect(self.yUp)
		self.yDownBtn = QtGui.QPushButton("y: -")
		self.yDownBtn.clicked.connect(self.yDown)

		self.xSizeLbl = QtGui.QLabel("x Size")
		self.ySizeLbl = QtGui.QLabel("y Size")

		self.xSizeTxt = QtGui.QLineEdit(str(self.xSize))
		self.ySizeTxt = QtGui.QLineEdit(str(self.ySize))

		self.combo1 = QtGui.QComboBox()
		self.combo2 = QtGui.QComboBox()

		hb1 = QtGui.QHBoxLayout()
		hb1.addWidget(self.xUpBtn)
		hb1.addWidget(self.xDownBtn)
		hb2 = QtGui.QHBoxLayout()
		hb2.addWidget(self.xSizeLbl)
		hb2.addWidget(self.xSizeTxt)
		hb3 = QtGui.QHBoxLayout()
		hb3.addWidget(self.yUpBtn)
		hb3.addWidget(self.yDownBtn)
		hb4 = QtGui.QHBoxLayout()
		hb4.addWidget(self.ySizeLbl)
		hb4.addWidget(self.ySizeTxt)

		vb1 = QtGui.QVBoxLayout()
		vb1.addLayout(hb1)
		vb1.addLayout(hb2)
		vb2 = QtGui.QVBoxLayout()
		vb2.addLayout(hb3)
		vb2.addLayout(hb4)
		xSG = QtGui.QGroupBox("x Size")
		xSG.setLayout(vb1)
		ySG = QtGui.QGroupBox("y Size")
		ySG.setLayout(vb2)
		vb3 = QtGui.QVBoxLayout()
		vb3.addWidget(self.combo1)
		vb3.addWidget(self.combo2)
		vb3.addWidget(xSG)
		vb3.addWidget(ySG)

		hb6 = QtGui.QHBoxLayout()
		hb6.addWidget(self.bgBtn, stretch=0)
		hb6.addWidget(self.delHotspotBtn, stretch=0)

		hb7 = QtGui.QHBoxLayout()
		hb7.addWidget(self.normalizeBtn, stretch=0)
		hb7.addWidget(self.cutBtn, stretch=0)

		hb8 = QtGui.QHBoxLayout()
		hb8.addWidget(self.gaussian33Btn, stretch=0)
		hb8.addWidget(self.gaussian55Btn, stretch=0)

		vb3.addLayout(hb6)
		vb3.addLayout(hb7)
		vb3.addLayout(hb8)

		self.setLayout(vb3)

	def changeXSize(self):
		self.xSize = int(self.xSizeTxt.text())

	def changeYSize(self):
		self.ySize = int(self.ySizeTxt.text())

	def xUp(self):
		self.changeXSize()
		self.changeYSize()
		self.xSize += 1
		self.xSizeTxt.setText(str(self.xSize))

	def xDown(self):
		self.changeXSize()
		self.changeYSize()
		self.xSize -= 1
		self.xSizeTxt.setText(str(self.xSize))

	def yUp(self):
		self.changeXSize()
		self.changeYSize()
		self.ySize += 1
		self.ySizeTxt.setText(str(self.ySize))

	def yDown(self):
		self.changeXSize()
		self.changeYSize()
		self.ySize -= 1
		self.ySizeTxt.setText(str(self.ySize))

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
		hb1.addWidget(self.view)
		hb1.addWidget(self.hist, 10)
		self.setLayout(hb1)

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

class QSelectTEST(QtGui.QWidget):
	def __init__(self):
		super(QSelectTEST, self).__init__()
		self.initUI()

	def initUI(self):
		pass














'''Iview1-3 used to display projections, sinogram and grapg on right edge'''

class IView(pg.GraphicsLayoutWidget):
    def __init__(self):
        super(IView, self).__init__()

        self.initUI()
        self.hotSpotNumb = 0

    def initUI(self):
        self.show()
        self.p1 = self.addPlot()
        self.projView = MyImageItem.ImageItem()
        self.projView.rotate(-90)
        self.p1.addItem(self.projView)

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
        self.p1 = self.addPlot()
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
        ##            if ev.key() == QtCore.Qt.Key_M:
        ##                  self.ROI.setPos([self.projView.iniX-10,self.projView.iniY-10])
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

class IView3(QtGui.QWidget):
    def __init__(self):
        super(IView3, self).__init__()
        self.initUI()

    def initUI(self):
        self.show()
        hb3 = QtGui.QHBoxLayout()
        self.file_name_title = QtGui.QLabel("_")
        lbl1 = QtGui.QLabel("x pos")
        self.lbl2 = QtGui.QLabel("")
        lbl3 = QtGui.QLabel("y pos")
        self.lbl4 = QtGui.QLabel("")
        btn1 = QtGui.QPushButton("position")
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

        hb2.addWidget(self.lcd)
        hb2.addWidget(self.sld)
        vb1.addWidget(self.file_name_title)
        vb1.addLayout(hb3)
        vb1.addWidget(self.view)
        vb1.addLayout(hb2)
        hb1.addLayout(vb1)
        hb1.addWidget(self.hist, 10)
        self.setLayout(hb1)

    def keyPressEvent(self, ev):
        if ev.key() == QtCore.Qt.Key_N:
            self.sld.setValue(self.sld.value + 1)
            print "Yes"

    def updatePanel(self):
        self.lbl2.setText(str(self.view.projView.iniX))
        self.lbl4.setText(str(self.view.projView.iniY))

def main():
    app = QtGui.QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
