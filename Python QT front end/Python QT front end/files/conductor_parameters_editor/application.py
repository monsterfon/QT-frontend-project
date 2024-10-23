import os
import copy
import logging

from qtpy import QtWidgets

import pandas as pd

import dlr_simutils_common.application

from .gui import input_parameters_widget
from .gui import progress_dialog
#pravi include za ConductorInfoWidget
from dlr_simutils_common.gui import conductor_info_widget

from .core.simulation import processor

from qtpy.QtCore import Signal




logger = logging.getLogger(__name__)


class ApplicationWindow(dlr_simutils_common.application.ApplicationWindow):
    saveAsJsonRequested = Signal()
    LoadAsJsonRequested = Signal()


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


        # Simulation processor
        self._processor = processor.SimulationProcessor()
        self._processor.processingStarted.connect(self.onProcessingStarted)
        self._processor.processingFinished.connect(self.onProcessingFinished)
        self._processor.processingProgress.connect(self.onProcessingProgress)

        self.processingProgressDialog = None  # Instantiated and cleared on-demand

        # Export filename
        self.exportFilename = None

        # *** UI ***
        self.setWindowTitle("Conductor parameters editor")

        # ** Main widget **
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)  # Main layout

        '''new buttons'''
        buttons_widget = QtWidgets.QWidget()  # New widget for the buttons

        buttons_widget.setMaximumHeight(50)  # Set maximum height for the widget

        Hbox_layout = QtWidgets.QHBoxLayout(buttons_widget)  # Set Vbox_layout as the layout of buttons_widget
        run_button = QtWidgets.QPushButton("Run ampacity simulation")
        run_button.setMaximumSize(300, 50)
        ampacity_label = QtWidgets.QLabel("Ampacity: ")
        ampacity_label.setMaximumSize(70, 50)
        self.ampacity_edit = QtWidgets.QLineEdit()

        Hbox_layout.addWidget(run_button)
        Hbox_layout.addWidget(ampacity_label)
        Hbox_layout.addWidget(self.ampacity_edit)
        layout.addWidget(buttons_widget)  # Add buttons_widget to the main layout
        ''''''

        self.setCentralWidget(widget)

        # Splitter
        splitter = QtWidgets.QSplitter()
        layout.addWidget(splitter)

        # ** Left widget in the splitter: conductor parameters, inputs, simulation settings **
        # Organized in tabs to reduce height
        tabWidget = QtWidgets.QTabWidget()
        splitter.addWidget(tabWidget)  # Add tabWidget to the splitter

        # * Tab: simulation settings *
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)
        layout.addStretch(1)

        # * Tab: Conductor parameters *
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(widget)







        #VERY IMPORTANT
        # Instantiate ConductorInfoWidget and add it to the layout
        conductor_info_widget_instance = conductor_info_widget.ConductorInfoWidget()
        layout.addWidget(conductor_info_widget_instance)
        layout.addStretch(1)
        tabWidget.addTab(widget, "Conductor parameters")
        # This method is triggered when the "Save as JSON" action is initiated. Emits the saveAsJsonRequested signal, which is connected to the dump_to_json method
        self.saveAsJsonRequested.connect(conductor_info_widget_instance.dump_to_json)
        self.LoadAsJsonRequested.connect(conductor_info_widget_instance.load_from_json)







        # * Tab: Weather conditions *
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)
        self.initialWeatherConditionsWidget = input_parameters_widget.WeatherParametersWidget()
        layout.addWidget(self.initialWeatherConditionsWidget)



        layout.addStretch(1)
        # add the tab
        tabWidget.addTab(widget, "Weather conditions")

        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)

        self.changedWeatherConditionsWidget = input_parameters_widget.WeatherParametersWidget()
        layout.addWidget(self.changedWeatherConditionsWidget)


        layout.addStretch(1)
        # add the tab


        '''simulation data'''
        # * Tab: Simulation settings *
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout(widget)  # Changed QVBoxLayout to QFormLayout for addRow method

        # Altitude
        spinBox = QtWidgets.QDoubleSpinBox()
        spinBox.setRange(-100, 5000)
        spinBox.setDecimals(2)
        spinBox.setSingleStep(25)
        spinBox.setValue(300)
        spinBox.setSuffix(" m")
        spinBox.setToolTip("<span>Set line span altitude.</span>")
        layout.addRow("Altitude:", spinBox)
        self.spinBoxAltitude = spinBox

        # Critical temperature
        spinBox = QtWidgets.QDoubleSpinBox()
        spinBox.setRange(0, 200)
        spinBox.setDecimals(0)
        spinBox.setSingleStep(10)
        spinBox.setValue(80)
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

        tabWidget.addTab(widget, "Simulation settings")





        # ** Fill splitter **
        splitter.addWidget(tabWidget)






        # Connect the signal to the slot
        #self.conductorInfoWidget.dataUpdated_temperature_thermal_limit.connect(self.updateTemperatureAndAmpacity)
        conductor_info_widget_instance.dataUpdated_temperature_thermal_limit.connect(self.updateTemperatureAndAmpacity)

    # Slot to update ampacity and critical temperature
    def updateTemperatureAndAmpacity(self, temperature, thermal_limit):

        try:
            print(temperature, thermal_limit)
            # Update ampacity_edit with the thermal limit value
            self.ampacity_edit.setText(str(thermal_limit))
            # Update spinBoxCriticalTemperature with the temperature value
            self.spinBoxCriticalTemperature.setValue(temperature)
        except Exception as e:
            #do a pop up with error message
            print(e)
            pass



    def onRunSimulation(self):
        # Retrieve conductor parameters
        lineParameters = copy.copy(
            self._conductorDefinitions.get(self._conductorType)
        )
        if not lineParameters:
            return



        # Collect input parameters
        initialWeatherConditions = self.initialWeatherConditionsWidget.weatherParameters
        initialLineLoad = self.initialLineLoadWidget.lineLoad

        changedWeatherConditions = self.changedWeatherConditionsWidget.weatherParameters
        changedLineLoad = self.changedLineLoadWidget.lineLoad

        # Collect simulation settings
        parallelProcesses = os.cpu_count()  # FIXME: make a setting?

        # Run processing
        try:
            self._processor.processData(
                self._conductorType,
                lineParameters,
                initialWeatherConditions,
                initialLineLoad,
                changedWeatherConditions,
                changedLineLoad,
                parallelProcesses,
            )
        except Exception as e:
            logger.error("Failed to start processing!", exc_info=True)
            QtWidgets.QMessageBox.warning(self, "Error", f"Failed to start processing:\n{e}")
            return

    def onProcessingStarted(self, numAllSamples):
        logger.debug("Processing started!")

        dialog = progress_dialog.ProgressDialog(
            numAllSamples=numAllSamples,
            parent=self,
        )
        dialog.canceled.connect(self._processor.cancelProcessing)
        dialog.show()

        self.processingProgressDialog = dialog

    def onProcessingFinished(self):
        logger.debug("Processing finished!")

        # Hide and destroy the progress dialog
        self.processingProgressDialog.hide()
        self.processingProgressDialog.deleteLater()
        self.processingProgressDialog = None

        # Process the results
        if self._processor.wasCanceled:
            QtWidgets.QMessageBox.information(self, "Operation canceled", "Processing was canceled by user.")
            return
        elif self._processor.wasAborted:
            QtWidgets.QMessageBox.warning(
                self,
                "Operation aborted",
                "Processing was aborted due to an error in (sub)process.",
            )
            return

        # Check if we have any results
        validEntries = [entry for entry in self._processor.results if entry.succeeded]
        if not validEntries:
            QtWidgets.QMessageBox.warning(self, "No results", "Processing did not yield any results!")
            # Fall-through to update the plot


    def onProcessingProgress(self, numProcessedSamples, numFailures, estimatedTime):
        logger.debug("Processing progress: %d, ETA: %.2f seconds", numProcessedSamples, estimatedTime)

        if self.processingProgressDialog:
            self.processingProgressDialog.updateProgress(
                numProcessedSamples,
                numFailures,
                estimatedTime,
            )

    def onExportResults(self):
        # Check that we have results
        results = self._processor.results
        if not results or not results[0].succeeded:
            QtWidgets.QMessageBox.information(self, "No results", "No results to export!")
            return
        results = results[0]

        # Obtain filename
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Export results",
            self.exportFilename,
            "CSV files (*.csv);;All files (*.*)")

        if not filename:
            return

        # Ensure we have suffix
        _, ext = os.path.splitext(filename)
        if not ext:
            filename += '.csv'

        self.exportFilename = filename  # Store for reuse

        # Create pandas dataframe. The results are represented in a dataclasses.dataclass structure that contains lists,
        # so we cannot directly pass it to pandas' dataframe.
        EXPORT_COLUMNS = (
            "time",
            "ambient_temperature",
            "wind_speed",
            "wind_direction",
            "relative_humidity",
            "solar_irradiance",
            "air_pressure",
            "rain_rate",
            "line_load",
            "ampacity",
            "time_to_overheat",
            "conductor_core_temperature",
        )

        df = pd.DataFrame({key: getattr(results, key) for key in EXPORT_COLUMNS})
        try:
            df.to_csv(filename, index=False)
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Error", f"Failed to export data to '{filename}':\n{e}")
            return

    def onConductorDefinitionsUpdated(self):
        pass

    def onConductorTypeChanged(self, conductorType):
        if not conductorType:
            return

        # Store the property, retrieve the data
        self._conductorType = conductorType
        data = self._conductorDefinitions.get(self._conductorType)



        # Update the information widget
        self.conductorInfoWidget.updateConductorData(
            self._conductorType,
            data,
        )



    def on_save_as_json_triggered(self):
        self.saveAsJsonRequested.emit()

    def on_Load_from_json_triggered(self)  :
        self.LoadAsJsonRequested.emit()

