from qtpy import QtCore, QtWidgets

import dlr_simutils_common.gui.line_parameters_widget


class ConductorParametersWidget(dlr_simutils_common.gui.line_parameters_widget.ConductorParametersWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        layout = self.layout()

        # Insert read-only static limit display right below the conductor type combo box
        spinBox = QtWidgets.QDoubleSpinBox()
        spinBox.setRange(0, 9999)
        spinBox.setDecimals(0)
        spinBox.setSingleStep(1)
        spinBox.setValue(0)
        spinBox.setSuffix(" A")
        spinBox.setToolTip("<span>Static thermal limit for the conductor type.</span>")

        spinBox.setEnabled(False)

        # Insert the spin box into the layout if necessary
        #layout.insertRow(1, "Static limit:", spinBox)
        self.spinBoxStaticThermalLimit = spinBox

    def setStaticThermalLimit(self, value):
        self.spinBoxStaticThermalLimit.setValue(value)

    def getStaticThermalLimit(self):
        return self.spinBoxStaticThermalLimit.value()

    staticThermalLimit = QtCore.Property(float, getStaticThermalLimit, setStaticThermalLimit)
