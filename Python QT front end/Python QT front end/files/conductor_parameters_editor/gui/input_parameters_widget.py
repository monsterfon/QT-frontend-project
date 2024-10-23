from qtpy import QtCore, QtWidgets

from dlr_simutils_common.gui import gui_utils
import dlr_simutils_common.gui.weather_parameters_widget


class WeatherParametersWidget(dlr_simutils_common.gui.weather_parameters_widget.WeatherParametersWidget):
    pass


class LineLoadWidget(gui_utils.ParametrizedFieldsMixIn, QtWidgets.QGroupBox):

    pass
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setTitle("Line load")

        layout = QtWidgets.QFormLayout(self)
        layout.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)

        # Line current/load
        spinBox = QtWidgets.QDoubleSpinBox()
        spinBox.setRange(0, 9999)
        spinBox.setValue(0)
        spinBox.setSuffix(" A")
        spinBox.setDecimals(0)
        spinBox.setSingleStep(1)
        spinBox.setToolTip("<span>Line current (load).</span>")

        self.spinBoxLineLoad = spinBox
        layout.addRow("Line load:", spinBox)

    def getLineLoad(self):
        return self.spinBoxLineLoad.value()

    def setLineLoad(self, value):
        self.spinBoxLineLoad.setValue(value)

    lineLoad = QtCore.Property(float, getLineLoad, setLineLoad)
    '''
