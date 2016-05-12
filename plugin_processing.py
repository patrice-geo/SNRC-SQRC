# -*- coding: utf-8 -*-

from PyQt4.QtCore import QTimer

import ogr
import os


class MainProcess:

    def __init__(self, dockwidget, iface, ManageUI, Initialization, plugin_dir):
        self.dockwidget = dockwidget
        self.iface = iface
        self.ManageUI = ManageUI
        self.Initialization = Initialization
        self.plugin_dir = plugin_dir



    # This is a simple timer to delay actions.
    # Using the timer avoids triggering actions instantly thus giving a more fluid feeling to the plugin
    def timed_action(self, ms, method):
        self.timer = QTimer()
        # Setting the interval of the timer, using the value specified in argument
        self.timer.setInterval(ms)   # 1000 ms = 1 seconds
        # The timer is single shot (stops after one repetition)
        self.timer.setSingleShot(True)
        # Listen to the signal emitted when the timer has finished. Call the method specified in argument when this signal is emitted.
        self.timer.timeout.connect(method)
        # Start the timer
        self.timer.start()




    # This method handles the "search box" (either municipality or coordinate).
    # This method is called on every changes in the "search box" (when signal textChanges is emitted)
    def mun_search(self):
        text_to_search = self.dockwidget.munLineEdit.text().lower()
        self.dockwidget.munListWidget.clear()
        if (len(text_to_search) >= 4):

            # "Auto-complete" feature when searching for a municipality. It populates the ListWidget with the results
            if (self.ManageUI.get_checked_top_radio_btn() == "municipality"):
                for i in self.Initialization.mun_list:
                    if (text_to_search in i[0:len(text_to_search)].lower()) or (text_to_search in i.lower()):
                        self.dockwidget.munListWidget.addItem(i)

            # Search for a coordinate instead if "coordinate" radio button is selected
            if (self.ManageUI.get_checked_top_radio_btn() == "coordinate"):
                try:
                    # Transform the coordinate from the user-specified input CRS to the MapCanvas CRS
                    self.ManageUI.transform_coordinates()
                except:
                    pass

                self.get_intersects_geom()






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









    ###############################
    ########################
    #Inutile
    #
    def get_feuillet_number(self):
        self.dockwidget.feuilListWidget.clear()

        # print selected_item
        self.get_intersects_geom()

    ################
    ###############



