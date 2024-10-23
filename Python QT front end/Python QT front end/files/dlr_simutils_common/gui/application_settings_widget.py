from qtpy import QtCore, QtWidgets


class ApplicationSettingsDialog(QtWidgets.QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle("Application settings")
        self.resize(800, 600)

        layout = QtWidgets.QVBoxLayout(self)

        self.tabWidget = QtWidgets.QTabWidget()
        layout.addWidget(self.tabWidget)

        # Tab: interface settings
        self.interfaceSettingsWidget = InterfaceSettingsWidget()
        self.tabWidget.addTab(self.interfaceSettingsWidget, "Interface settings")

        # Button box
        buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Close)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        layout.addWidget(buttonBox)

    # Work around the fact that Qt dialogs that are closed via accept() or reject() do not seem to disappear from
    # Windows 10 taskbar preview
    def showEvent(self, event):
        super().showEvent(event)

        try:
            from qtpy import QtWinExtras
            QtWinExtras.QtWin.setWindowExcludedFromPeek(self.windowHandle(), False)
        except Exception:
            pass

    def hideEvent(self, event):
        super().hideEvent(event)

        try:
            from qtpy import QtWinExtras
            QtWinExtras.QtWin.setWindowExcludedFromPeek(self.windowHandle(), True)
        except Exception:
            pass


class InterfaceSettingsWidget(QtWidgets.QWidget):
    stylePluginChanged = QtCore.Signal(str, name="stylePluginChanged")
    thirdPartyThemeChanged = QtCore.Signal(str, name="thirdPartyThemeChanged")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        layout = QtWidgets.QFormLayout(self)
        layout.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)

        # Note about style changes
        label = QtWidgets.QLabel(
            "<b>Note:</b> Style changes might require application restart to take full effect."
        )
        layout.addRow(label)

        # Style plugin
        comboBox = QtWidgets.QComboBox()
        layout.addRow("Qt style plugin: ", comboBox)
        self.comboBoxStyle = comboBox

        comboBox.addItem("System default", "")

        availableStyles = QtWidgets.QStyleFactory.keys()
        for style in availableStyles:
            comboBox.addItem(style, style)

        comboBox.currentIndexChanged.connect(self._onStylePluginChanged)

        # Third party theme
        comboBox = QtWidgets.QComboBox()
        layout.addRow("Third party theme: ", comboBox)
        self.comboBoxThirdPartyTheme = comboBox

        comboBox.addItem("None", "")

        try:
            import qdarkstyle  # noqa: F401
            comboBox.addItem("qdarkstyle", "qdarkstyle")
        except ImportError:
            pass

        try:
            import qtmodern  # noqa: F401
            comboBox.addItem("qtmodern (light)", "qtmodern-light")
            comboBox.addItem("qtmodern (dark)", "qtmodern-dark")
        except ImportError:
            pass

        comboBox.currentIndexChanged.connect(self._onThirdPartyThemeChanged)

    def _onStylePluginChanged(self, idx):
        self.stylePluginChanged.emit(self.comboBoxStyle.currentData())

    def _onThirdPartyThemeChanged(self, idx):
        self.thirdPartyThemeChanged.emit(self.comboBoxThirdPartyTheme.currentData())

    # Style plugin
    def getStylePlugin(self):
        return self.comboBoxStyle.currentData()

    def setStylePlugin(self, value):
        idx = self.comboBoxStyle.findData(value)
        self.comboBoxStyle.blockSignals(True)
        self.comboBoxStyle.setCurrentIndex(idx)
        self.comboBoxStyle.blockSignals(False)

    stylePlugin = QtCore.Property(str, getStylePlugin, setStylePlugin, notify=stylePluginChanged)

    # Style plugin
    def getThirdPartyTheme(self):
        return self.comboBoxThirdPartyTheme.currentData()

    def setThirdPartyTheme(self, value):
        idx = self.comboBoxThirdPartyTheme.findData(value)
        self.comboBoxThirdPartyTheme.blockSignals(True)
        self.comboBoxThirdPartyTheme.setCurrentIndex(idx)
        self.comboBoxThirdPartyTheme.blockSignals(False)

    thirdPartyTheme = QtCore.Property(str, getThirdPartyTheme, setThirdPartyTheme, notify=thirdPartyThemeChanged)
