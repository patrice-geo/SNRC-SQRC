# -*- coding: utf-8 -*-

import gdal, ogr
import os


class Initialization:

    def __init__(self, plugin_dir, iface):
        self.plugin_dir = plugin_dir
        self.iface = iface




    # GDAL Config options
    def set_gdal_encoding(self):
        self.gdal_encoding = gdal.GetConfigOption('SHAPE_ENCODING')
        gdal.SetConfigOption('SHAPE_ENCODING', 'LATIN1')



    def restore_gdal_encoding(self):
        gdal.SetConfigOption('SHAPE_ENCODING', self.gdal_encoding)









    # This method is called only when initializing the plugin in QGIS.
    def list_names_and_geoms(self):

        # Set the driver for OGR (using .shp as input files)
        ogrDriverMun = ogr.GetDriverByName('ESRI Shapefile')

        # Open the input municipality shapefile
        mun_ds = ogrDriverMun.Open(self.plugin_dir + os.sep + "in_data" + os.sep + "mun.shp")
        # Get the layer from the shapefile
        munLayer = mun_ds.GetLayer()

        # Get Spatial reference system from municipality shapefile
        munLayer_proj = munLayer.GetSpatialRef


        # Initializing variables to get all municipality names and geometries from the feature
        i = 0
        self.mun_geom_list = []
        self.mun_list = []

        # Iterate through features of the layer
        for munFeature in munLayer:
            # Get the municipality name
            mun_name = munFeature.GetField("mus_nm_mun")

            # Get the municipality geometry
            munGeom = munFeature.GetGeometryRef()
            # If the municipality name is not already in the municipality list, then add it
            if (mun_name.lower() not in self.mun_list):
                # Municipality name list
                self.mun_list.append(str(mun_name))
                # Municipality list with geometries
                self.mun_geom_list.append([mun_name, munGeom])


        #del ogrDriverMun









    def list_feuilSQRC_names_and_geoms(self):
        # Set the driver for OGR (using .shp as input files)
        ogrDriverFeuil = ogr.GetDriverByName('ESRI Shapefile')
        # Open the input SQRC feuillet shapefile
        feuilSQRC_ds = ogrDriverFeuil.Open(self.plugin_dir + os.sep + "in_data" + os.sep + "index_SQRC_20k.shp")
        # Get the layer from the shapefile
        feuilSQRCLayer = feuilSQRC_ds.GetLayer()

        # Get Spatial reference system from municipality shapefile
        feuilSQRCLayer_proj = feuilSQRCLayer.GetSpatialRef


        # Initializing variables to get all municipality names and geometries from the feature
        i = 0
        self.feuilSQRC_geom_list = []
        self.feuilSQRC_num_list = []

        # Iterate through features of the layer
        for feuilSQRCFeature in feuilSQRCLayer:
            # Get the municipality name
            feuilSQRC_num = feuilSQRCFeature.GetField("feuille")
            # Get the municipality geometry
            feuilSQRCGeom = feuilSQRCFeature.GetGeometryRef()

            # If the municipality name is not already in the municipality list, then add it
            if (feuilSQRC_num not in self.feuilSQRC_num_list):
                # Municipality name list
                self.feuilSQRC_num_list.append(str(feuilSQRC_num))
                # Municipality list with geometries
                self.feuilSQRC_geom_list.append(feuilSQRCGeom)


        #del ogrDriverFeuil










    def list_feuilSNRC_names_and_geoms(self):
        # Set the driver for OGR (using .shp as input files)
        ogrDriverFeuil = ogr.GetDriverByName('ESRI Shapefile')
        # Open the input SQRC feuillet shapefile
        feuilSNRC_ds = ogrDriverFeuil.Open(self.plugin_dir + os.sep + u"in_data" + os.sep + "nts_snrc_50k.shp")
        # Get the layer from the shapefile
        feuilSNRCLayer = feuilSNRC_ds.GetLayer()

        # Get Spatial reference system from municipality shapefile
        feuilLayer_proj = feuilSNRCLayer.GetSpatialRef


        # Initializing variables to get all municipality names and geometries from the feature
        self.feuilSNRC_geom_list = []
        self.feuilSNRC_num_list = []

        # Iterate through features of the layer
        for feuilSNRCFeature in feuilSNRCLayer:
            # Get the municipality name
            feuilSNRC_num = feuilSNRCFeature.GetField("nts_snrc")
            # Get the municipality geometry
            feuilSNRCGeom = feuilSNRCFeature.GetGeometryRef()

            # If the municipality name is not already in the municipality list, then add it
            if (feuilSNRC_num not in self.feuilSNRC_num_list):
                # Municipality name list
                self.feuilSNRC_num_list.append(str(feuilSNRC_num))
                # Municipality list with geometries
                self.feuilSNRC_geom_list.append(feuilSNRCGeom)


        #del ogrDriverFeuil











    # Get current project EPSG code
    def get_project_epsg(self):
        canvas = self.iface.mapCanvas()
        mapRenderer = canvas.mapRenderer()

        srs = mapRenderer.destinationCrs()

        return str(srs.authid())




