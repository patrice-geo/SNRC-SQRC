# -*- coding: utf-8 -*-

from PyQt4.QtGui import QCursor
from PyQt4.QtCore import *

class ManageUI:

    municipality_text = ""
    coordinate_text = ""
    captured_coordinate = ""
    selected_item = ""
    coord_captured = ""

    def __init__(self, dockwidget, Initialization, iface):
        self.dockwidget = dockwidget
        self.Initialization = Initialization
        self.iface = iface




    # Give information about which top radio button is checked (municipalité, coordonnées or extent)
    def get_checked_top_radio_btn(self):
        if (self.dockwidget.munRadioButton.isChecked()):
            return "municipality"
        elif (self.dockwidget.coordRadioButton.isChecked()):
            return "coordinate"
        elif (self.dockwidget.extRadioButton.isChecked()):
            return "extent"
        else:
            return None




    # Give information about which bottom radio button is checked (SQRC or SNRC)
    def get_checked_bottom_radio_btn(self):
        if (self.dockwidget.SNRCRadioButton.isChecked()):
            return "SNRC"
        elif (self.dockwidget.SQRCRadioButton.isChecked()):
            return "SQRC"
        else:
            return None





    def get_selected_mun(self):
        try:
            return self.dockwidget.munListWidget.currentItem().text()
        except:
            return None





    # Make elements invisible, depending on which radio button is checked
    def adjust_ui_elements(self, checked_button):
        self.dockwidget.munListWidget.clear()
        self.dockwidget.feuilListWidget.clear()

        self.dockwidget.munLineEdit.clear()

        if (checked_button == "municipality"):
            self.dockwidget.coordToolButton.setEnabled(False)
            self.dockwidget.crsToolButton.hide()
            self.dockwidget.epsgLabel.hide()
            self.dockwidget.searchLabel.setText(u"Rechercher une municipalité")
            self.dockwidget.munLineEdit.setEnabled(True)
            self.dockwidget.munListWidget.setEnabled(True)
            self.dockwidget.munLineEdit.setText(self.municipality_text)
        if (checked_button == "coordinate"):
            self.dockwidget.coordToolButton.setEnabled(True)
            self.dockwidget.crsToolButton.show()
            self.dockwidget.epsgLabel.show()
            self.dockwidget.searchLabel.setText(u"Rechercher une coordonnée")
            self.dockwidget.munLineEdit.setEnabled(True)
            self.dockwidget.epsgLabel.setText(self.Initialization.get_project_epsg())
            self.dockwidget.munListWidget.setEnabled(True)
            self.dockwidget.munLineEdit.setText(self.coordinate_text)
        if (checked_button == "extent"):
            self.dockwidget.coordToolButton.setEnabled(False)
            self.dockwidget.crsToolButton.hide()
            self.dockwidget.epsgLabel.hide()
            self.dockwidget.searchLabel.setText(u"Rechercher une municipalité")
            self.dockwidget.munLineEdit.setEnabled(False)
            self.dockwidget.munListWidget.setEnabled(True)










    # Change EPSG code label according to the selected CRS
    def change_epsg(self):
        pass






    def start_coord_capture(self):
        self.coord_captured = False
        self.previous_cursor = self.iface.mapCanvas().cursor()
        cursor = QCursor(Qt.CrossCursor)
        self.iface.mapCanvas().setCursor(cursor)




    def stop_coord_capture(self):
        self.coord_captured = True



        # Set the cursor to the original shape
        #cursor = QCursor(self.previous_cursor)
        #self.iface.mapCanvas().setCursor(cursor)

        # Get the mouse XY position
        mouse_coordinates = self.iface.mapCanvas().mouseLastXY()


        self.point = self.iface.mapCanvas().getCoordinateTransform().toMapCoordinates(mouse_coordinates)


        # Get the CRS coordinates from the XY mouse position
        self.captured_coordinate = str(self.iface.mapCanvas().getCoordinateTransform().toMapCoordinates(mouse_coordinates))

        # Remove '(' and ')' from the coordinate string
        self.captured_coordinate = self.captured_coordinate.strip("(")
        self.captured_coordinate = self.captured_coordinate.strip(")")

        # Write coordinate into the search box
        self.dockwidget.munLineEdit.setText(str(self.captured_coordinate))



