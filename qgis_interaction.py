# -*- coding: utf-8 -*-

import ogr, gdal
import os

class InterractionQgis:

    def __init__(self, dockwidget, iface, ManageUI, plugin_dir ):
        self.dockwidget = dockwidget
        self.iface = iface
        self.ManageUI = ManageUI
        self.plugin_dir = plugin_dir


    # Add the selected feuillet geometry to the QGIS layer list (by double clicking)
    def add_feuil_geom_to_qgis(self):
        # Get Driver
        ogrDriverFeuil = ogr.GetDriverByName('ESRI Shapefile')
        # Open the input SQRC feuillet shapefile
        if (self.ManageUI.get_checked_bottom_radio_btn() == "SQRC"):
            feuil_ds = ogrDriverFeuil.Open(self.plugin_dir + os.sep + "in_data" + os.sep + "index_SQRC_20k.shp")
        # Open the input SQRC feuillet shapefile
        if (self.ManageUI.get_checked_bottom_radio_btn() == "SNRC"):
            feuil_ds = ogrDriverFeuil.Open(self.plugin_dir + os.sep + "in_data" + os.sep + "nts_snrc_50k.shp")
        # Get the layer from the shapefile
        feuilLayer = feuil_ds.GetLayer()
        self.selected_feuil = self.dockwidget.feuilListWidget.currentItem().text()


        for feuilFeature in feuilLayer:
            if (self.ManageUI.get_checked_bottom_radio_btn() == "SQRC"):
                feuil_num = feuilFeature.GetField("feuille")
            if (self.ManageUI.get_checked_bottom_radio_btn() == "SNRC"):
                feuil_num = feuilFeature.GetField("nts_snrc")

            if (feuil_num == self.selected_feuil):
                feuilGeom = feuilFeature.GetGeometryRef().Clone()         # .Clone() avoids QGIS from crashing...

        # Delete the datasource if exists
        if os.path.exists(self.plugin_dir + os.sep + "out_data" + os.sep + str(self.selected_feuil) + ".shp"):
            ogrDriverFeuil.DeleteDataSource(self.plugin_dir + os.sep + "out_data" + os.sep + str(self.selected_feuil) + ".shp")

        # Create the shapefile
        feuilOutDataSource = ogrDriverFeuil.CreateDataSource(self.plugin_dir + os.sep + "out_data" + os.sep + str(self.selected_feuil) + ".shp")
        feuilOutLayer = feuilOutDataSource.CreateLayer(str(self.selected_feuil), geom_type=ogr.wkbPolygon)

        # Add an ID field
        idField = ogr.FieldDefn("id", ogr.OFTInteger)
        feuilOutLayer.CreateField(idField)

        # Add a municipality field
        feuilField = ogr.FieldDefn("feuillet", ogr.OFTString)
        feuilOutLayer.CreateField(feuilField)

        # Create the feature and set values
        feuilFeatureDefn = feuilOutLayer.GetLayerDefn()
        feuilOutFeature = ogr.Feature(feuilFeatureDefn)
        feuilOutFeature.SetGeometry(feuilGeom)
        feuilOutFeature.SetField("id", 1)
        feuilOutFeature.SetField("feuillet", "1")
        feuilOutLayer.CreateFeature(feuilOutFeature)

        # Add layer to QGIS interface
        self.iface.addVectorLayer(self.plugin_dir + os.sep + "out_data" + os.sep + str(self.selected_feuil) + ".shp", str(self.selected_feuil), "ogr")






    # Add the selected municipality geometry to the QGIS layer list (by double clicking)
    def add_mun_geom_to_qgis(self):
        # Get Driver
        ogrDriverMun = ogr.GetDriverByName('ESRI Shapefile')
        # Open the input SQRC feuillet shapefile
        mun_ds = ogrDriverMun.Open(self.plugin_dir + os.sep + "in_data" + os.sep + "mun.shp")
        # Get the layer from the shapefile
        munLayer = mun_ds.GetLayer()

        for munFeature in munLayer:
            mun_name = munFeature.GetField("mus_nm_mun")
            if (mun_name == self.ManageUI.get_selected_mun()):
                munGeom = munFeature.GetGeometryRef().Clone()         # .Clone() avoids QGIS from crashing...


        # Delete the datasource if exists
        if os.path.exists(self.plugin_dir + os.sep + "out_data" + os.sep + str(self.ManageUI.get_selected_mun()) + ".shp"):
            ogrDriverMun.DeleteDataSource(self.plugin_dir + os.sep + "out_data" + os.sep + self.ManageUI.get_selected_mun() + ".shp")


        # Create the shapefile
        munOutDataSource = ogrDriverMun.CreateDataSource(self.plugin_dir + os.sep + "out_data" + os.sep + self.ManageUI.get_selected_mun() + ".shp")
        munOutLayer = munOutDataSource.CreateLayer(str(self.ManageUI.get_selected_mun()), geom_type=ogr.wkbPolygon)

        # Add an ID field
        idField = ogr.FieldDefn("id", ogr.OFTInteger)
        munOutLayer.CreateField(idField)

        # Add a municipality field
        munField = ogr.FieldDefn("municipality", ogr.OFTString)
        munOutLayer.CreateField(munField)

        # Create the feature and set values
        munFeatureDefn = munOutLayer.GetLayerDefn()
        munOutFeature = ogr.Feature(munFeatureDefn)
        munOutFeature.SetGeometry(munGeom)
        munOutFeature.SetField("id", 1)
        munOutLayer.CreateFeature(munOutFeature)

        # Add layer to QGIS interface
        self.iface.addVectorLayer(self.plugin_dir + os.sep + "out_data" + os.sep + self.ManageUI.get_selected_mun() + ".shp", self.ManageUI.get_selected_mun(), "ogr")

        del ogrDriverMun
