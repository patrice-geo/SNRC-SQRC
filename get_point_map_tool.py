# -*- coding: utf-8 -*-

from PyQt4 import Qt
from PyQt4.QtGui import QColor
from PyQt4.QtCore import SIGNAL



from qgis.gui import QgsMapTool, QgsMapToolEmitPoint, QgsRubberBand
from qgis.core import QgsPoint, QGis


class GetPointMapTool(QgsMapToolEmitPoint):

    coordCaptured = ""

    def __init__(self, canvas, iface, dockwidget, currentMapTool):
        self.canvas = canvas
        self.iface = iface
        self.currentMapTool = currentMapTool
        self.dockwidget = dockwidget
        QgsMapToolEmitPoint.__init__(self, self.canvas)
        self.rubberBand = QgsRubberBand(self.canvas, QGis.Point)
        self.rubberBand.setColor(QColor(255,5,5))
        self.rubberBand.setWidth(1)
        self.reset()

    def reset(self):
        self.startPoint = self.endPoint = None
        self.isEmittingPoint = False
        self.rubberBand.reset(QGis.Polygon)

    def canvasPressEvent(self, e):
        self.point = self.toMapCoordinates(e.pos())
        self.isEmittingPoint = True
        self.showPoint(self.point)

    def canvasReleaseEvent(self, e):
        self.isEmittingPoint = False
        self.coordCaptured = self.pointdef()
        if self.coordCaptured is not None:
            print "Point:", self.coordCaptured
            self.coordCaptured = str(self.coordCaptured).strip("(")
            self.coordCaptured = str(self.coordCaptured).strip(")")
            self.dockwidget.munLineEdit.setText(self.coordCaptured)


        self.iface.mapCanvas().setMapTool(self.currentMapTool)

    def canvasMoveEvent(self, e):
        if not self.isEmittingPoint:
            return

        self.endPoint = self.toMapCoordinates(e.pos())
       # self.showRect(self.startPoint, self.endPoint)

    def showPoint(self, point):
        self.rubberBand.reset(QGis.Polygon)


        point1 = QgsPoint(point.x(), point.y())


        self.rubberBand.addPoint(point1, False)

        self.rubberBand.show()

    def pointdef(self):

        return QgsPoint(self.point)
