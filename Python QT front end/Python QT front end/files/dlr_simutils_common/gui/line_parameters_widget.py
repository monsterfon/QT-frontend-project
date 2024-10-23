from qtpy import QtCore, QtWidgets

from . import gui_utils


class _ConductorTypeComboBox(gui_utils.SearchableComboBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def sizeHint(self):
        # Prefer size that accommodates around 30 characters
        hint = super().sizeHint()
        metrics = self.fontMetrics()
        width = metrics.averageCharWidth() * 30
        if hint.width() < width:
            hint.setWidth(width)
        return hint


class LineParametersWidget(QtWidgets.QGroupBox):
    reloadConductorDefinitionsRequest = QtCore.Signal(name="reloadConductorDefinitionsRequest")
    showConductorInfoRequest = QtCore.Signal(name="showConductorInfoRequest")
    conductorTypeChanged = QtCore.Signal(str, name="conductorTypeChanged")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setTitle("Line parameters")

        layout = QtWidgets.QFormLayout(self)
        layout.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)

        # Conductor type
        hbox = QtWidgets.QHBoxLayout()

        comboBox = _ConductorTypeComboBox()
        comboBox.setToolTip("<span>Select conductor type.</span>")
        hbox.addWidget(comboBox, 1)
        comboBox.currentIndexChanged.connect(lambda idx: self.conductorTypeChanged.emit(self.comboBoxConductorType.currentData()))
        self.comboBoxConductorType = comboBox

        pushButton = QtWidgets.QPushButton()
        pushButton.setIcon(
            self.style().standardIcon(QtWidgets.QStyle.SP_BrowserReload)
        )
        pushButton.setToolTip("<span>Reload conductor definition files.</span>")
        pushButton.clicked.connect(self.reloadConductorDefinitionsRequest.emit)
        hbox.addWidget(pushButton)

        pushButton = QtWidgets.QPushButton("Details")
        pushButton.setToolTip("<span>Show information for selected conductor.</span>")
        pushButton.clicked.connect(self.showConductorInfoRequest.emit)
        hbox.addWidget(pushButton)

        layout.addRow("Conductor type:", hbox)

        # Orientation
        spinBox = QtWidgets.QDoubleSpinBox()
        spinBox.setRange(-360, 360)
        spinBox.setDecimals(2)
        spinBox.setSingleStep(1)
        spinBox.setValue(0)
        spinBox.setSuffix(" °")
        spinBox.setToolTip(
            "<span>Set line span orientation. Set to 0 to interpret wind "
            "direction values as incidence angles (angles-of-attack).</span>"
        )

        layout.addRow("Orientation:", spinBox)
        self.spinBoxOrientation = spinBox

        # Altitude
        spinBox = QtWidgets.QDoubleSpinBox()
        spinBox.setRange(-100, 6000)
        spinBox.setDecimals(2)
        spinBox.setSingleStep(1)
        spinBox.setValue(0)
        spinBox.setSuffix(" m")
        spinBox.setToolTip("<span>Set line span altitude.</span>")

        layout.addRow("Altitude:", spinBox)
        self.spinBoxAltitude = spinBox

        # Critical temperature
        spinBox = QtWidgets.QDoubleSpinBox()
        spinBox.setRange(0, 250)
        spinBox.setDecimals(0)
        spinBox.setSingleStep(1)
        spinBox.setValue(0)
        spinBox.setSuffix(" °C")
        spinBox.setToolTip("<span>Critical conductor core temperature.</span>")

        layout.addRow("Critical temp.:", spinBox)
        self.spinBoxCriticalTemperature = spinBox

        # Convection model
        comboBox = QtWidgets.QComboBox()
        comboBox.addItem("CIGRE", "cigre")
        comboBox.addItem("IEEE", "ieee")

        layout.addRow("Convection model:", comboBox)
        self.comboBoxConvectionModel = comboBox

    def setAvailableConductorTypes(self, entries):
        # Use helper that preserves the current selection
        self.comboBoxConductorType.replaceEntries(entries)

    def getConductorType(self):
        return self.comboBoxConductorType.currentData()

    conductorType = QtCore.Property(str, getConductorType, notify=conductorTypeChanged)

    def getLineAltitude(self):
        return self.spinBoxAltitude.value()

    lineAltitude = QtCore.Property(float, getLineAltitude)

    def getLineOrientation(self):
        return self.spinBoxOrientation.value()

    lineOrientation = QtCore.Property(float, getLineOrientation)

    def setCriticalTemperature(self, value):
        self.spinBoxCriticalTemperature.setValue(value)

    def getCriticalTemperature(self):
        return self.spinBoxCriticalTemperature.value()

    criticalTemperature = QtCore.Property(float, getCriticalTemperature, setCriticalTemperature)

    def setConvectionModel(self, value):
        value = value.lower()
        idx = self.comboBoxConvectionModel.findData(value)
        self.comboBoxConvectionModel.setCurrentIndex(idx)

    def getConvectionModel(self):
        return self.comboBoxConvectionModel.currentData()

    convectionModel = QtCore.Property(str, getConvectionModel, setConvectionModel)
