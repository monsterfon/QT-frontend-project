from qtpy import QtCore, QtWidgets

from . import gui_utils


class WeatherParametersWidget(gui_utils.ParametrizedFieldsMixIn, QtWidgets.QGroupBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setTitle("Weather conditions")

        layout = QtWidgets.QFormLayout(self)
        layout.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)

        # Ambient temperature
        spinBox = QtWidgets.QDoubleSpinBox()
        spinBox.setRange(-50, 60)
        spinBox.setValue(35)
        spinBox.setSuffix(" °C")
        spinBox.setDecimals(2)
        spinBox.setSingleStep(1)
        spinBox.setToolTip("<span>Ambient temperature.</span>")

        layout.addRow("Ambient temperature:", spinBox)
        self._registerParameterField("ambient_temperature", spinBox)

        # Wind speed
        spinBox = QtWidgets.QDoubleSpinBox()
        spinBox.setRange(0, 25)
        spinBox.setValue(0.6)
        spinBox.setSuffix(" m/s")
        spinBox.setDecimals(2)
        spinBox.setSingleStep(0.1)
        spinBox.setToolTip("<span>Wind speed.</span>")

        layout.addRow("Wind speed:", spinBox)
        self._registerParameterField("wind_speed", spinBox)

        # Wind direction
        spinBox = QtWidgets.QDoubleSpinBox()
        spinBox.setRange(-360, 360)
        spinBox.setValue(90)
        spinBox.setSuffix(" °")
        spinBox.setDecimals(2)
        spinBox.setSingleStep(1)
        spinBox.setToolTip("<span>Wind direction.</span>")

        layout.addRow("Wind direction:", spinBox)
        self._registerParameterField("wind_direction", spinBox)

        # Relative humidity
        spinBox = QtWidgets.QDoubleSpinBox()
        spinBox.setRange(0, 100)
        spinBox.setValue(90)
        spinBox.setSuffix(" %")
        spinBox.setDecimals(2)
        spinBox.setSingleStep(1)
        spinBox.setToolTip("<span>Relative humidity.</span>")

        layout.addRow("Relative humidity:", spinBox)
        self._registerParameterField("relative_humidity", spinBox)

        # Solar irradiance
        spinBox = QtWidgets.QDoubleSpinBox()
        spinBox.setRange(0, 1500)
        spinBox.setValue(900)
        spinBox.setSuffix(" W/m²")
        spinBox.setDecimals(2)
        spinBox.setSingleStep(1)
        spinBox.setToolTip("<span>Solar irradiance.</span>")

        layout.addRow("Solar irradiance:", spinBox)
        self._registerParameterField("solar_irradiance", spinBox)

        # Air pressure
        spinBox = QtWidgets.QDoubleSpinBox()
        spinBox.setRange(801, 1199)
        spinBox.setValue(981.80)
        spinBox.setSuffix(" mbar")
        spinBox.setDecimals(2)
        spinBox.setSingleStep(1)
        spinBox.setToolTip("<span>Air pressure.</span>")

        layout.addRow("Air pressure:", spinBox)
        self._registerParameterField("air_pressure", spinBox)

        # Rain rate
        spinBox = QtWidgets.QDoubleSpinBox()
        spinBox.setRange(0, 100)
        spinBox.setValue(0)
        spinBox.setSuffix(" mm/h")
        spinBox.setDecimals(2)
        spinBox.setSingleStep(1)
        spinBox.setToolTip("<span>Rain rate.</span>")

        layout.addRow("Rain rate:", spinBox)
        self._registerParameterField("rain_rate", spinBox)

    def getWeatherParameters(self):
        return self._collectParameters()

    def setWeatherParameters(self, data):
        self._populateFields(data)

    weatherParameters = QtCore.Property(dict, getWeatherParameters, setWeatherParameters)
