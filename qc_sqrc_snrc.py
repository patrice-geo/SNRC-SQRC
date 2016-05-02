# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SQRCSNRC
                                 A QGIS plugin
 Search for a city name in Quebec, Canada and get the SQRC/SNRC map number
                              -------------------
        begin                : 2016-04-30
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Patrice Pineault
        email                : patrice.pineault@usherbrooke.ca
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, Qt
from PyQt4.QtGui import QAction, QIcon
# Initialize Qt resources from file resources.py
import resources

# Import the code for the DockWidget
from qc_sqrc_snrc_dockwidget import SQRCSNRCDockWidget
import os.path


import ogr, osr



class SQRCSNRC:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface

        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)

        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'SQRCSNRC_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Quebec SQRC-SNRC')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'SQRCSNRC')
        self.toolbar.setObjectName(u'SQRCSNRC')

        #print "** INITIALIZING SQRCSNRC"

        self.pluginIsActive = False
        self.dockwidget = SQRCSNRCDockWidget()


        ################################################################################
        ################################################################################

        self.dockwidget.munLineEdit.textChanged.connect(self.mun_text_changed)
        self.dockwidget.munListWidget.currentItemChanged.connect(self.mun_current_changed)
        self.dockwidget.munListWidget.itemDoubleClicked.connect(self.mun_double_clicked)
        self.dockwidget.feuilListWidget.itemDoubleClicked.connect(self.feuil_double_clicked)

        self.list_names_and_geoms()
        self.list_feuil_names_and_geoms()

        self.dockwidget.SNRCRadioButton.setChecked(True)



        ################################################################################
        ################################################################################



    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('SQRCSNRC', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action


    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/SQRCSNRC/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Quebec SNRC-SQRC'),
            callback=self.run,
            parent=self.iface.mainWindow())

    #--------------------------------------------------------------------------

    def onClosePlugin(self):
        """Cleanup necessary items here when plugin dockwidget is closed"""

        #print "** CLOSING SQRCSNRC"

        # disconnects
        self.dockwidget.closingPlugin.disconnect(self.onClosePlugin)

        # remove this statement if dockwidget is to remain
        # for reuse if plugin is reopened
        # Commented next statement since it causes QGIS crashe
        # when closing the docked window:
        # self.dockwidget = None

        self.pluginIsActive = False


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""

        #print "** UNLOAD SQRCSNRC"

        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Quebec SQRC-SNRC'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    #--------------------------------------------------------------------------

    def run(self):
        """Run method that loads and starts the plugin"""

        if not self.pluginIsActive:
            self.pluginIsActive = True

            #print "** STARTING SQRCSNRC"

            # dockwidget may not exist if:
            #    first run of plugin
            #    removed on close (see self.onClosePlugin method)
            if self.dockwidget == None:
                # Create the dockwidget (after translation) and keep reference
                self.dockwidget = SQRCSNRCDockWidget()

            # connect to provide cleanup on closing of dockwidget
            self.dockwidget.closingPlugin.connect(self.onClosePlugin)

            # show the dockwidget
            # TODO: fix to allow choice of dock location
            self.iface.addDockWidget(Qt.LeftDockWidgetArea, self.dockwidget)
            self.dockwidget.show()



    # This method is called when the LineEdit text changes (textChanged signal).
    def mun_text_changed(self):
        # Call the method to search through all municipalities
        self.mun_search()





    # This method is called only when initializing the plugin in QGIS.
    def list_names_and_geoms(self):

        # Set the driver for OGR (using .shp as input files)
        ogrDriverMun = ogr.GetDriverByName('ESRI Shapefile')

        # Open the input municipality shapefile
        mun_ds = ogrDriverMun.Open(self.plugin_dir + os.sep + u"in_data" + os.sep + "mun.shp")
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



    def list_feuil_names_and_geoms(self):
        # Set the driver for OGR (using .shp as input files)
        ogrDriverFeuil = ogr.GetDriverByName('ESRI Shapefile')
        # Open the input SQRC feuillet shapefile
        feuil_ds = ogrDriverFeuil.Open(self.plugin_dir + os.sep + u"in_data" + os.sep + "index_SQRC_20k.shp")
        # Get the layer from the shapefile
        feuilLayer = feuil_ds.GetLayer()

        # Get Spatial reference system from municipality shapefile
        feuilLayer_proj = feuilLayer.GetSpatialRef


        # Initializing variables to get all municipality names and geometries from the feature
        i = 0
        self.feuil_geom_list = []
        self.feuil_num_list = []

        # Iterate through features of the layer
        for feuilFeature in feuilLayer:
            # Get the municipality name
            feuil_num = feuilFeature.GetField("feuille")
            # Get the municipality geometry
            feuilGeom = feuilFeature.GetGeometryRef()

            # If the municipality name is not already in the municipality list, then add it
            if (feuil_num not in self.feuil_num_list):
                # Municipality name list
                self.feuil_num_list.append(str(feuil_num))
                # Municipality list with geometries
                self.feuil_geom_list.append(feuilGeom)


        #del ogrDriverFeuil





    # This method searches for the text in the LineEdit (search box) in the municipality list.
    def mun_search(self):
        text_to_search = self.dockwidget.munLineEdit.text().lower()
        self.dockwidget.munListWidget.clear()
        if (len(text_to_search) >= 4):

            # Auto-complete feature when searching for a municipality. It populates the ListWidget with the results
            for i in self.mun_list:
                if (text_to_search in i[0:len(text_to_search)].lower()) or (text_to_search in i.lower()):
                    self.dockwidget.munListWidget.addItem(i)





    # Here, I can use the geometries already fetched. They are in a list mun_list_geom, or something.
    # I wrote all of this to replace an old method that made QGIS crash.
    # Apparently, I need to .clone() the geometry

    def get_intersects_geom(self):
        #print self.mun_geom_list

        # Get Driver
        ogrDriverMun = ogr.GetDriverByName('ESRI Shapefile')
        # Open the input SQRC feuillet shapefile
        feuil_ds = ogrDriverMun.Open(self.plugin_dir + os.sep + "in_data" + os.sep + "mun.shp")
        # Get the layer from the shapefile
        munLayer = feuil_ds.GetLayer()

        for munFeature in munLayer:
            mun_name = munFeature.GetField("mus_nm_mun")
            if (mun_name == self.selected_item):
                munGeom = munFeature.GetGeometryRef().Clone()         # .Clone() avoids QGIS from crashing...




        # Get Driver
        ogrDriverFeuil = ogr.GetDriverByName('ESRI Shapefile')
        # Open the input SQRC feuillet shapefile
        feuil_ds = ogrDriverFeuil.Open(self.plugin_dir + os.sep + "in_data" + os.sep + "index_SQRC_20k.shp")


        # Get the layer from the shapefile
        feuilLayer = feuil_ds.GetLayer()


        for feuilFeature in feuilLayer:
            feuil_num = feuilFeature.GetField("feuille")
            feuilGeom = feuilFeature.GetGeometryRef()

            if munGeom.Intersects(feuilGeom):

                self.dockwidget.feuilListWidget.addItem(feuil_num)

        del ogrDriverMun, ogrDriverFeuil, feuil_num







    def mun_double_clicked(self):
        self.add_mun_geom_to_qgis()




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
            if (mun_name == self.selected_item):
                munGeom = munFeature.GetGeometryRef().Clone()         # .Clone() avoids QGIS from crashing...


        # Create the shapefile

        munOutDataSource = ogrDriverMun.CreateDataSource(self.plugin_dir + os.sep + "out_data" + os.sep + str(self.selected_item) + ".shp")
        munOutLayer = munOutDataSource.CreateLayer(str(self.selected_item), geom_type=ogr.wkbPolygon)

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
        self.iface.addVectorLayer(self.plugin_dir + os.sep + "out_data" + os.sep + self.selected_item + ".shp", self.selected_item, "ogr")




    def feuil_double_clicked(self):
        self.add_feuil_geom_to_qgis()




    # Add the selected feuillet geometry to the QGIS layer list (by double clicking)
    def add_feuil_geom_to_qgis(self):
        # Get Driver
        ogrDriverFeuil = ogr.GetDriverByName('ESRI Shapefile')
        # Open the input SQRC feuillet shapefile
        feuil_ds = ogrDriverFeuil.Open(self.plugin_dir + os.sep + "in_data" + os.sep + "index_SQRC_20k.shp")
        # Get the layer from the shapefile
        feuilLayer = feuil_ds.GetLayer()
        self.selected_feuil = self.dockwidget.feuilListWidget.currentItem().text()


        for feuilFeature in feuilLayer:
            feuil_num = feuilFeature.GetField("feuille")
            if (feuil_num == self.selected_feuil):
                feuilGeom = feuilFeature.GetGeometryRef().Clone()         # .Clone() avoids QGIS from crashing...


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








    def mun_current_changed(self):
        self.get_feuillet_number()





    def get_feuillet_number(self):
        self.dockwidget.feuilListWidget.clear()
        self.selected_item = self.dockwidget.munListWidget.currentItem().text()
        #print selected_item
        self.get_intersects_geom()



    def get_checked_radio_button(self):
        if (self.dockwidget.SNRCRadioButton.isChecked()):
            #return self.dockwidget.SNRCRadioButton
            return "SNRC"
        elif (self.dockwidget.SQRCRadioButton.isChecked()):
            #return self.dockwidget.SQRCRadioButton
            return "SQRC"
        else:
            return None


    def get_feuillet_geom(self, feuillet):
        if (self.get_checked_radio_button() == "SNRC"):
            pass
        if (self.get_checked_radio_button() == "SQRC"):
            pass




    def add_mun_to_list(self):
        pass















