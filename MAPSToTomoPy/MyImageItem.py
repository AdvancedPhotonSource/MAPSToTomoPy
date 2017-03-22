import pyqtgraph

class ImageItem (pyqtgraph.ImageItem):
    def __init__(self):
        pyqtgraph.ImageItem.__init__(self)

    def mousePressEvent(self, ev):
        #print 'My mousePressEvent'
        self.iniY=ev.pos().x()
        self.iniX=ev.pos().y()
        self.moving="True"

    def mouseReleaseEvent(self, ev):
        #print 'My mouseReleaseEvent'
        self.finalY=ev.pos().x()
        self.finalX=ev.pos().y()
        self.difX=self.finalX-self.iniX
        self.difY=self.finalY-self.iniY
        self.moving="False"

    def mouseMoveEvent(self, ev):
        #print 'My mouseMoveEvent'
        self.movingY=ev.pos().x()
        self.movingX=ev.pos().y()

    def mouseDragEvent(self, ev):
        #print 'My mouseDragEvent'
        pass
