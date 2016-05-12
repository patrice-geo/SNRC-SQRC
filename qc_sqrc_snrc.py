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
from PyQt4.QtGui import QAction, QIcon, QCursor

# Initialize Qt resources from file resources.py
import resources

# Import the code for the DockWidget
from qc_sqrc_snrc_dockwidget import SQRCSNRCDockWidget
import os.path

import qgis
import ogr


# Importing classes
from initializing import Initialization
from manage_ui import ManageUI
from plugin_processing import MainProcess
from qgis_interaction import InterractionQgis
from get_point_map_tool import GetPointMapTool


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
        ################################################################################

        self.municipality_text = ""
        self.coordinate_text = ""
        self.selected_item = ""


        ### Initializing the plugin ###

        # Initializing classes
        self.Initialization = Initialization(self.plugin_dir, self.iface)
        self.ManageUI = ManageUI(self.dockwidget, self.Initialization, self.iface)
        self.MainProcess = MainProcess(self.dockwidget, self.iface, self.ManageUI, self.Initialization, self.plugin_dir)


        self.InterractionQgis = InterractionQgis(self.dockwidget, self.iface, self.ManageUI, self.plugin_dir, self.Initialization)

        self.Initialization.set_gdal_encoding()
        self.Initialization.list_names_and_geoms()
        self.Initialization.list_feuilSQRC_names_and_geoms()
        self.Initialization.list_feuilSNRC_names_and_geoms()
        self.Initialization.restore_gdal_encoding()


        ### Setting a few default values ###
        self.dockwidget.SQRCRadioButton.setChecked(True)
        self.dockwidget.munRadioButton.setChecked(True)

        self.coord_captured = True

        # Setting the UI elements
        self.ManageUI.adjust_ui_elements(self.ManageUI.get_checked_top_radio_btn())



        ### Listen to UI signals ###
        self.dockwidget.munLineEdit.textChanged.connect(self.mun_text_changed)
        self.dockwidget.munListWidget.currentItemChanged.connect(self.mun_current_changed)
        self.dockwidget.munListWidget.itemDoubleClicked.connect(self.mun_double_clicked)
        self.dockwidget.feuilListWidget.itemDoubleClicked.connect(self.feuil_double_clicked)

        self.dockwidget.coordToolButton.clicked.connect(self.coordToolButton_clicked)
        self.dockwidget.crsToolButton.clicked.connect(self.crsToolButton_clicked)

        self.dockwidget.munRadioButton.toggled.connect(self.munRadioButton_toggled)
        self.dockwidget.coordRadioButton.toggled.connect(self.coordRadioButton_toggled)
        self.dockwidget.extRadioButton.toggled.connect(self.extRadioButton_toggled)

        self.dockwidget.SNRCRadioButton.toggled.connect(self.SNRCRadioButton_toggled)
        self.dockwidget.SQRCRadioButton.toggled.connect(self.SQRCRadioButton_toggled)

        # Listen to mapCanvas signals
        self.iface.mapCanvas().destinationCrsChanged.connect(self.mapcanvas_crs_changed)
        self.iface.mapCanvas().scaleChanged.connect(self.canvas_clicked)        # Supposed to be a mouse click event



        ################################################################################
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




    ###############################################
    ###     Callback methods for UI signals     ###
    ###############################################

    # When the LineEdit (search box) text changes.
    def mun_text_changed(self):
        # Call the method to search through all municipalities
        self.MainProcess.timed_action(500, self.MainProcess.mun_search)



    # When double clicking an item in the municipality ListWidget
    def mun_double_clicked(self):
        self.InterractionQgis.add_mun_geom_to_qgis()




    # When double clicking an item in the feuillet ListWidget
    def feuil_double_clicked(self):
        self.InterractionQgis.add_feuil_geom_to_qgis()




    # When the selection changes in the municipality ListWidget
    def mun_current_changed(self):

        try:
            if (str(self.dockwidget.munListWidget.currentItem().text()).strip != "") and (self.dockwidget.munListWidget.currentItem().text() != None):
                self.ManageUI.selected_item = self.ManageUI.get_selected_mun()
        except:
            return

        # If "municipality" is selected, get the map index for the selected municipality
        if (self.ManageUI.get_checked_top_radio_btn() == "municipality"):
            self.MainProcess.timed_action(500, self.MainProcess.get_feuillet_number)








    # When the Municipality radio button is toggled
    def munRadioButton_toggled(self):
        # Verify if the radio button is checked or not
        if (self.dockwidget.munRadioButton.isChecked()):
            # Set the GUI elements for the selected radio button
            self.ManageUI.adjust_ui_elements(self.ManageUI.get_checked_top_radio_btn())
            #self.MainProcess.timed_action(1000, self.MainProcess.get_intersects_geom)
        else:
            self.ManageUI.municipality_text = self.dockwidget.munLineEdit.text()




    # When the Coordinates radio button is toggled
    def coordRadioButton_toggled(self):
        # Verify if the radio button is checked or not
        if (self.dockwidget.coordRadioButton.isChecked()):
            # Set the GUI elements for the selected radio button
            self.ManageUI.adjust_ui_elements(self.ManageUI.get_checked_top_radio_btn())
            # When "coordinate" is selected, don't wait for an item selection and get the map index
            self.MainProcess.timed_action(1000, self.MainProcess.get_intersects_geom)
        else:
            self.ManageUI.coordinate_text = self.dockwidget.munLineEdit.text()




    # When the Extent radio button is toggled
    def extRadioButton_toggled(self):
        # Verify if the radio button is checked or not
        if (self.dockwidget.extRadioButton.isChecked()):
            # Set the GUI elements for the selected radio button
            self.ManageUI.adjust_ui_elements(self.ManageUI.get_checked_top_radio_btn())
            self.MainProcess.timed_action(1000, self.MainProcess.get_intersects_geom)








    # When coordToolButton is clicked
    def coordToolButton_clicked(self):
        self.coordinate_capture()
        # self.ManageUI.start_coord_capture()



    # When map canvas is clicked
    def canvas_clicked(self):

        if (self.ManageUI.get_checked_top_radio_btn() == "extent"):
            self.MainProcess.timed_action(1000, self.MainProcess.get_intersects_geom)

        if (self.ManageUI.get_checked_top_radio_btn() == "coordinate") and (self.ManageUI.coord_captured == False):
            self.ManageUI.stop_coord_capture()






    # When CRS is changed is QGIS
    def mapcanvas_crs_changed(self):
        self.dockwidget.epsgLabel.setText("EPSG: " + self.Initialization.get_project_epsg())




    # When the SNRCRadioButton is toggled
    def SNRCRadioButton_toggled(self):
        if (self.dockwidget.SNRCRadioButton.isChecked()):
            if (self.ManageUI.get_checked_top_radio_btn() == "extent"):
                self.MainProcess.timed_action(1000, self.MainProcess.get_feuillet_number)
            else:
                try:
                    self.ManageUI.selected_item = self.dockwidget.munListWidget.currentItem().text()
                    self.MainProcess.timed_action(1000, self.MainProcess.get_feuillet_number)
                except:
                    self.MainProcess.timed_action(1000, self.MainProcess.get_feuillet_number)






    # When the SQRCRadioButton is toggled
    def SQRCRadioButton_toggled(self):
        if (self.dockwidget.SQRCRadioButton.isChecked()):
            if (self.ManageUI.get_checked_top_radio_btn() == "extent"):
                self.MainProcess.timed_action(1000, self.MainProcess.get_feuillet_number)
            else:
                try:
                    self.ManageUI.selected_item = self.dockwidget.munListWidget.currentItem().text()
                    self.MainProcess.timed_action(1000, self.MainProcess.get_feuillet_number)
                except:
                    self.MainProcess.timed_action(1000, self.MainProcess.get_feuillet_number)





    def crsToolButton_clicked(self):
        self.ManageUI.select_input_crs()










    def coordinate_capture(self):

        self.ManageUI.set_to_map_crs()
        # Get the current MapTool to set it back after the coordinate is captured. This is done in the CanvasReleaseEvent in the GetPointMapTool.
        self.currentMapTool = self.iface.mapCanvas().mapTool()
        # Intance of the MapTool object to capture the point
        self.GetPointMapTool = GetPointMapTool(self.iface.mapCanvas(), self.iface, self.dockwidget, self.currentMapTool)
        # Set the MapTool to capture the point
        self.iface.mapCanvas().setMapTool(self.GetPointMapTool)
        # Write the captured point in the "search box"
        self.dockwidget.munLineEdit.setText(self.GetPointMapTool.coordCaptured)







