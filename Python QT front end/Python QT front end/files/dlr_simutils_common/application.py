import sys
import argparse
import signal
import pathlib
import logging



import qtpy
from qtpy import QtCore, QtGui, QtWidgets

import dlr_simutils_common.core.logging

from .gui import application_settings_widget
from .gui import conductor_info_widget
from .gui.conductor_info_widget import ConductorInfoWidget




from .gui import about_dialog

from .core import conductor_definition


logger = logging.getLogger(__name__)

class ApplicationSettings(QtCore.QObject):
    stylePluginChanged = QtCore.Signal(str, name="stylePluginChanged")
    thirdPartyThemeChanged = QtCore.Signal(str, name="thirdPartyThemeChanged")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.settings = QtCore.QSettings()
        self.settings.beginGroup("ApplicationSettings")

        self._stylePlugin = self.settings.value("stylePlugin", "", str)
        self._thirdPartyTheme = self.settings.value("thirdPartyTheme", "", str)

    def getStylePlugin(self):
        return self._stylePlugin

    def setStylePlugin(self, value):
        self._stylePlugin = value
        self.settings.setValue("stylePlugin", self._stylePlugin)

        self.stylePluginChanged.emit(self._stylePlugin)
        logger.info("At next restart, the following style plugin will be used: %s", self._stylePlugin)

    stylePlugin = QtCore.Property(str, getStylePlugin, setStylePlugin, notify=stylePluginChanged)

    def getThirdPartyTheme(self):
        return self._thirdPartyTheme

    def setThirdPartyTheme(self, theme):
        self._thirdPartyTheme = theme
        self.settings.setValue("thirdPartyTheme", self._thirdPartyTheme)

        self.thirdPartyThemeChanged.emit(self._thirdPartyTheme)

    thirdPartyTheme = QtCore.Property(bool, getThirdPartyTheme, setThirdPartyTheme, notify=thirdPartyThemeChanged)




class ApplicationWindow(QtWidgets.QMainWindow):


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)



        # Application settings proxy
        self.applicationSettings = ApplicationSettings()

        # Connect signals
        self.applicationSettings.stylePluginChanged.connect(self.setStylePlugin)
        self.applicationSettings.thirdPartyThemeChanged.connect(self.setThirdPartyTheme)

        # Application settings dialog
        self.applicationSettingsDialog = application_settings_widget.ApplicationSettingsDialog(
            parent=self,
            modal=False,
        )

        interfaceSettingsWidget = self.applicationSettingsDialog.interfaceSettingsWidget
        interfaceSettingsWidget.stylePluginChanged.connect(self.applicationSettings.setStylePlugin)
        interfaceSettingsWidget.thirdPartyThemeChanged.connect(self.applicationSettings.setThirdPartyTheme)
        interfaceSettingsWidget.stylePlugin = self.applicationSettings.stylePlugin
        interfaceSettingsWidget.thirdPartyTheme = self.applicationSettings.thirdPartyTheme

        # Conductor definitions
        self._conductorDefinitionsPath = pathlib.Path(__file__).parent.parent / "conductor-types"
        self._conductorDefinitions = {}

        self._conductorType = None

        # *** UI ***
        # window title: overridden by child implementation
        self.setWindowTitle("DLR simulation utility application")

        # ** Menu bar ***
        menuBar = self.menuBar()


        ''' new change from standard'''
        # File menu
        menu = menuBar.addMenu("File")
        action = menu.addAction("Application settings ...")
        action.triggered.connect(self.onShowSettingsDialog)
        action = menu.addAction("Save as JSON")   #new change from standard
        action.triggered.connect(self.on_save_as_json_triggered)
        action = menu.addAction("Save as XLSX")   #new change from standard
        action = menu.addAction("Load from JSON")  # new change from standard
        action.triggered.connect(self.on_Load_from_json_triggered)
        menu.addSeparator()
        action = menu.addAction("Exit")
        action.triggered.connect(QtCore.QCoreApplication.quit)
        action = menuBar.addAction("About...")
        action.triggered.connect(self.onShowAboutDialog)

        # ** Additional dialogs and external widgets **
        # Conductor information window
        self.conductorInfoWidget = conductor_info_widget.ConductorInfoWidget(parent=self)

        # Load conductor definitions
        QtCore.QTimer.singleShot(0, self.updateConductorDefinitions)

    def updateConductorDefinitions(self):

        '''
        try:
            self._conductorDefinitions = conductor_definition.load_conductor_definitions(
                self._conductorDefinitionsPath
            )
        except Exception as e:
            logger.error("Failed to load conductor definitions!", exc_info=True)
            QtWidgets.QMessageBox.warning(
                self,
                "Error",
                f"Failed to load conductor definitions!\nError message: {e}",
            )
            return

        self.onConductorDefinitionsUpdated()'''

    # These two methods are overridden by child implementations, in order to update the widgets.
    def onConductorDefinitionsUpdated(self):
        pass

    def onConductorTypeChanged(self):
        pass



    def on_save_as_json_triggered(self):
        pass

    def on_Load_from_json_triggered(self)  :

        pass


        
        


    def onShowConductorInfo(self):
        # Show the information in separate window
        self.conductorInfoWidget.raise_()
        self.conductorInfoWidget.show()

    def onShowSettingsDialog(self):
        self.applicationSettingsDialog.show()
        self.applicationSettingsDialog.raise_()

    def onShowAboutDialog(self):
        dialog = about_dialog.AboutDialog(parent=self)
        dialog.exec_()

    @staticmethod
    def setStylePlugin(pluginName):
        if not pluginName:
            return

        logger.info("Changing Qt style plugin: %r", pluginName)
        app = QtWidgets.QApplication.instance()
        style = app.setStyle(pluginName)
        if style is None:
            validStyles = ', '.join(QtWidgets.QStyleFactory.keys())
            logger.warning("Invalid style %r! Valid styles: %r", pluginName, validStyles)

    @staticmethod
    def setThirdPartyTheme(themeName):
        logger.info("Changing 3rd party theme: %r!", themeName)
        try:
            app = QtWidgets.QApplication.instance()
            if themeName == 'qdarkstyle':
                import qdarkstyle
                app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyside2'))

                # Work-around for dark theme detection in our About dialog; set the text color to white, as we cannot
                # retrieve it from stylesheet...
                palette = app.palette()
                palette.setColor(
                    QtGui.QPalette.Normal,
                    QtGui.QPalette.WindowText,
                    QtCore.Qt.white,
                )
                app.setPalette(palette)
            elif themeName == 'qtmodern-dark':
                import qtmodern.styles
                qtmodern.styles.dark(app)
            elif themeName == 'qtmodern-light':
                import qtmodern.styles
                qtmodern.styles.light(app)
            else:
                app.setStyleSheet(None)
        except Exception:
            logger.warning("Failed to change 3rd party theme to %r!", themeName, exc_info=True)







def main(
    application_window_type,
    application_name,
    application_description,
    application_version,
    root_dir=pathlib.Path('.'),
):
    # Command-line parser
    parser = argparse.ArgumentParser(description=application_description)
    dlr_simutils_common.core.logging.parser_add_logging_arguments(parser)  # Add logging-related arguments
    args, unparsed_args = parser.parse_known_args()

    # Setup logging; default logging file is assumed to be located next to the entry-point
    dlr_simutils_common.core.logging.setup_logging(
        args,
        default_config=root_dir / "logging.conf",
    )

    # Qt application instance
    app = QtWidgets.QApplication([sys.argv[0], *unparsed_args])  # Forward unparsed arguments
    app.setOrganizationName("Operato")
    app.setOrganizationDomain("operato.eu")
    app.setApplicationName(application_name)
    app.setApplicationVersion(application_version)

    # Qt bindings info
    logger.info("Using %s %s (Qt %s)", qtpy.API_NAME, qtpy.PYSIDE_VERSION or qtpy.PYQT_VERSION, qtpy.QT_VERSION)

    # Set application icon
    app.setWindowIcon(QtGui.QIcon(
        str(dlr_simutils_common.RESOURCES_DIR / "icon-operato-black.svg")
    ))

    # Make Ctrl+C work
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    # Apply style plugin, if necessary (and do so before we show the first dialog/window).
    settings = ApplicationSettings()
    if settings.stylePlugin:
        ApplicationWindow.setStylePlugin(settings.stylePlugin)
    if settings.thirdPartyTheme:
        ApplicationWindow.setThirdPartyTheme(settings.thirdPartyTheme)

    # Ensure DiTeR executable is available
    if True:
        if not dlr_simutils_common.core.diter.diter_exe:
            QtWidgets.QMessageBox.critical(
                None,
                "DiTeR executable missing",
                "Could not find DiTeR executable in either PATH or core.diter package directory!",
            )
            sys.exit(-1)

    # Application window
    try:
        main_window = application_window_type()
    except Exception as e:
        logger.critical("Fatal error encountered!", exc_info=True)
        QtWidgets.QMessageBox.critical(None, "Error", f"Fatal error encountered:\n{e}")
        sys.exit(-1)

    main_window.show()

    app.exec_()
