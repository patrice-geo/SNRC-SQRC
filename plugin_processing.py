# -*- coding: utf-8 -*-

from PyQt4.QtCore import QTimer

import gdal, ogr
import os

class MainProcess():

    def __init__(self, dockwidget, iface, ManageUI, Initialization, plugin_dir):
        self.dockwidget = dockwidget
        self.iface = iface
        self.ManageUI = ManageUI
        self.Initialization = Initialization
        self.plugin_dir = plugin_dir


    def timed_action(self, ms, method):
        self.timer = QTimer()
        self.timer.setInterval(ms)   # 1000 ms = 1 secondes
        self.timer.setSingleShot(True)
        # Quand le timer fini, appeller la fonction pour effacer
        self.timer.timeout.connect(method)
        self.timer.start()



    # This method searches for the text in the LineEdit (search box) in the municipality list.
    def mun_search(self):
        text_to_search = self.dockwidget.munLineEdit.text().lower()
        self.dockwidget.munListWidget.clear()
        if (len(text_to_search) >= 4):

            print "mun search"
            print self.ManageUI.get_checked_top_radio_btn()

            # Auto-complete feature when searching for a municipality. It populates the ListWidget with the results
            if (self.ManageUI.get_checked_top_radio_btn() == "municipality"):
                for i in self.Initialization.mun_list:
                    if (text_to_search in i[0:len(text_to_search)].lower()) or (text_to_search in i.lower()):
                        self.dockwidget.munListWidget.addItem(i)


            if (self.ManageUI.get_checked_top_radio_btn() == "coordinate"):
                self.get_intersects_geom()




    # Here, I can use the geometries already fetched. They are in a list mun_list_geom, or something.
    # I wrote all of this to replace an old method that made QGIS crash.
    # Apparently, I need to .clone() the geometry

    def get_intersects_geom(self):

        # Default value for geom
        geom = None
        # Clear the "Feuillets" listWidget
        self.dockwidget.feuilListWidget.clear()

        if (self.ManageUI.get_checked_top_radio_btn() == "municipality"):
            #print self.mun_geom_list

            # Get Driver
            ogrDriverMun = ogr.GetDriverByName('ESRI Shapefile')
            # Open the input SQRC feuillet shapefile
            feuil_ds = ogrDriverMun.Open(self.plugin_dir + os.sep + "in_data" + os.sep + "mun.shp")
            # Get the layer from the shapefile
            munLayer = feuil_ds.GetLayer()

            for munFeature in munLayer:
                mun_name = munFeature.GetField("mus_nm_mun")
                if (mun_name == self.ManageUI.get_selected_mun()):
                    geom = munFeature.GetGeometryRef().Clone()         # .Clone() avoids QGIS from crashing...


        if (self.ManageUI.get_checked_top_radio_btn() == "coordinate"):

            # Clear the "Municipality" listWidget
            self.dockwidget.munListWidget.clear()

            # Create a geometry from the selected point
            geom = ogr.Geometry(ogr.wkbPoint)

            try:
                # Get the search box text and "split" it
                splitted = str(self.dockwidget.munLineEdit.text()).split(',')

                # Add a point in the geometry
                geom.AddPoint(float(splitted[0]), float(splitted[1]))
            except:
                return



            # Get the intersecting municipality
            # Get Driver
            ogrDriverMun = ogr.GetDriverByName('ESRI Shapefile')
            # Open the input SQRC feuillet shapefile
            feuil_ds = ogrDriverMun.Open(self.plugin_dir + os.sep + "in_data" + os.sep + "mun.shp")
            # Get the layer from the shapefile
            munLayer = feuil_ds.GetLayer()

            for munFeature in munLayer:
                #mun_name = munFeature.GetField("mus_nm_mun")
                munGeom = munFeature.GetGeometryRef().Clone()         # .Clone() avoids QGIS from crashing...
                if (geom.Intersects(munGeom)):

                    self.dockwidget.munListWidget.addItem(munFeature.GetField("mus_nm_mun"))



        if (self.ManageUI.get_checked_top_radio_btn() == "extent"):

            # Get the extent as a WktPolygon
            self.extentWktPolygon = self.iface.mapCanvas().extent().asWktPolygon()

            # Clear the "Municipality" listWidget
            self.dockwidget.munListWidget.clear()

            # Create the extent polygon
            geom = ogr.CreateGeometryFromWkt(self.extentWktPolygon)

            # Get Driver
            ogrDriverMun = ogr.GetDriverByName('ESRI Shapefile')
            # Open the input SQRC feuillet shapefile
            feuil_ds = ogrDriverMun.Open(self.plugin_dir + os.sep + "in_data" + os.sep + "mun.shp")
            # Get the layer from the shapefile
            munLayer = feuil_ds.GetLayer()

            for munFeature in munLayer:
                #mun_name = munFeature.GetField("mus_nm_mun")
                munGeom = munFeature.GetGeometryRef().Clone()         # .Clone() avoids QGIS from crashing...
                if (geom.Intersects(munGeom)):

                    self.dockwidget.munListWidget.addItem(munFeature.GetField("mus_nm_mun"))



        # Get Driver
        ogrDriverFeuil = ogr.GetDriverByName('ESRI Shapefile')


        if (self.dockwidget.SNRCRadioButton.isChecked()):

            # Open the input SQRC feuillet shapefile
            feuilSNRC_ds = ogrDriverFeuil.Open(self.plugin_dir + os.sep + "in_data" + os.sep + "nts_snrc_50k.shp")
            # Get the layer from the shapefile
            feuilSNRCLayer = feuilSNRC_ds.GetLayer()

            for feuilSNRCFeature in feuilSNRCLayer:
                feuilSNRC_num = feuilSNRCFeature.GetField("nts_snrc")
                feuilSNRCGeom = feuilSNRCFeature.GetGeometryRef()

                if (self.ManageUI.get_checked_top_radio_btn() == "municipality"):
                    if (geom != None):
                        if geom.Intersects(feuilSNRCGeom):
                            self.dockwidget.feuilListWidget.addItem(feuilSNRC_num)

                if (self.ManageUI.get_checked_top_radio_btn() == "coordinate"):
                    if geom.Intersects(feuilSNRCGeom):
                        self.dockwidget.feuilListWidget.addItem(feuilSNRC_num)

                if (self.ManageUI.get_checked_top_radio_btn() == "extent"):
                    if geom.Intersects(feuilSNRCGeom):
                        self.dockwidget.feuilListWidget.addItem(feuilSNRC_num)



        if (self.dockwidget.SQRCRadioButton.isChecked()):

            # Open the input SQRC feuillet shapefile
            feuilSQRC_ds = ogrDriverFeuil.Open(self.plugin_dir + os.sep + "in_data" + os.sep + "index_SQRC_20k.shp")
            # Get the layer from the shapefile
            feuilSQRCLayer = feuilSQRC_ds.GetLayer()


            for feuilSQRCFeature in feuilSQRCLayer:
                feuilSQRC_num = feuilSQRCFeature.GetField("feuille")
                feuilSQRCGeom = feuilSQRCFeature.GetGeometryRef()

                if (self.ManageUI.get_checked_top_radio_btn() == "municipality"):
                    if (geom != None):
                        if geom.Intersects(feuilSQRCGeom):
                            self.dockwidget.feuilListWidget.addItem(feuilSQRC_num)

                if (self.ManageUI.get_checked_top_radio_btn() == "coordinate"):
                    if geom.Intersects(feuilSQRCGeom):
                        self.dockwidget.feuilListWidget.addItem(feuilSQRC_num)

                if (self.ManageUI.get_checked_top_radio_btn() == "extent"):
                    if geom.Intersects(feuilSQRCGeom):
                        self.dockwidget.feuilListWidget.addItem(feuilSQRC_num)


       # del ogrDriverMun, ogrDriverFeuil, feuilSQRC_num, feui










    def get_feuillet_number(self):
        self.dockwidget.feuilListWidget.clear()

        # print selected_item
        self.get_intersects_geom()






