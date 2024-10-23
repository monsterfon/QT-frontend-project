from qtpy import QtCore, QtWidgets
import re

import pathlib
import json
import os
from datetime import datetime

from qtpy.QtWidgets import  QFileDialog
from qtpy.QtCore import Signal


class _AutoFieldsWidgetMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._fieldEntries = []

        try:
            # Navigate up three levels from the current script's directory and then to the target file
            file_path = pathlib.Path(__file__).parent.parent.parent /  "conductor-types" / "config_conductor_data_min_max.json"
            with open(file_path, 'r') as file:
                self.conductor_data = json.load(file)
        except FileNotFoundError:
            QtWidgets.QMessageBox.information(self, "Error", "File 'config_conductor_data_min_max.json' not found.")
        except json.JSONDecodeError:
            QtWidgets.QMessageBox.information(self, "Error", "Failed to parse 'config_conductor_data_min_max.json'.")
        except Exception as e:
            QtWidgets.QMessageBox.information(self, "Error", f"Failed to load or parse the JSON file: {e}")


    def _registerField(self, valueName, stringFormat, valueFunc=None, defaultValue=0.00002):
        # Widget
        widget = QtWidgets.QDoubleSpinBox()
        if valueName is not None:
            if 'number_of_wires' in valueName:#number of wires is integer
                widget = QtWidgets.QSpinBox() 

        widget.setReadOnly(False)

        widget.setObjectName(valueName)


        # Set maximum value using the Maximum_min function
        max_min_values = self.Maximum_min(valueName)
        if max_min_values is not None:
            min_value, max_value = max_min_values
            try:
                if max_value is not None:
                    widget.setMaximum(max_value)
                if min_value is not None:
                    widget.setMinimum(min_value)
            except TypeError: #number of wires is integer
                widget.setRange(int(min_value), int(max_value))



        # Extract the number of decimals from stringFormat and set as precision
        match = re.search(r'\.(\d)f', stringFormat)
        if match:
            decimals = int(match.group(1))
            widget.setDecimals(decimals)

        # Extract unit from stringFormat and set as suffix
        unit = stringFormat.split('[')[-1].rstrip(']')
        if unit and not re.search(r'%|\.1f|\.2f|\.3f', unit):
            widget.setSuffix(f" {unit}")

        if defaultValue != 0:
            widget.setValue(defaultValue)

        # Register for updateData()
        self._fieldEntries.append((widget, stringFormat, valueName, valueFunc))


        return widget

    def updateData(self, data):
        for widget, stringFormat, valueName, valueFunc in self._fieldEntries:
            if valueName is None:
                value = valueFunc(data) if valueFunc else None
            else:
                value = data.get(valueName)

            # Check if valueName contains "specific_conductivity" and convert the value accordingly
            if "specific_conductivity" in valueName and value is not None:
                value = value / 1000000.0  # Convert from S/m to MS/m

            if value is not None:
                widget.setValue(value)
            else:
                widget.clear()

    def Maximum_min(self, field_name):

        if field_name is None:
            return None
        field_name = field_name.replace('icient', '.')
        if 'inner_part_' in field_name:
            field_name = field_name.replace('inner_part_', '')
            min_value, max_value = self.conductor_data["inner"][field_name].values()
        elif 'outer_part_' in field_name:
            field_name = field_name.replace('outer_part_', '')
            min_value, max_value = self.conductor_data["outer"][field_name].values()
        elif 'nusselt_base' in field_name:
            min_value, max_value = self.conductor_data["common"]["nusselt_base"].values()
        elif 'nusselt_exp' in field_name:
            min_value, max_value = self.conductor_data["common"]["nusselt_exp."].values()
        else:  # common_ part
            field_name = field_name.replace('common_part_', '')
            min_value, max_value = self.conductor_data["common"][field_name].values()


        # Remove any non-numeric characters and convert to float
        min_value = float(re.sub(r'[^\d.]+', '', min_value))
        max_value = float(re.sub(r'[^\d.]+', '', max_value))
        return min_value, max_value



class ConductorCommonInfoWidget(_AutoFieldsWidgetMixin, QtWidgets.QGroupBox):
    def __init__(self, *args, default_values=None, **kwargs):
        super().__init__(*args, **kwargs)
        default_values = default_values

        self.setAlignment(QtCore.Qt.AlignCenter)

        layout = QtWidgets.QFormLayout(self)
        layout.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)

        # Add fields
        layout.addRow(
            "Cross-section:",
            self._registerField("conductor_cross_section", "%.2f [mm²]", defaultValue = default_values["conductor_cross_section"])
        )
        layout.addRow(
            "DC resistance (*):",
            self._registerField("dc_resistance", "%.4f [Ω / km]", defaultValue = default_values["dc_resistance"])
        )
        layout.addRow(
            "Mass per unit length (*):",
            self._registerField("mass_per_unit_length", "%.1f [kg / km]", defaultValue = default_values["mass_per_unit_length"])
        )
        layout.addRow(
            "Emissivity:",
            self._registerField("emissivity", "%.2f", defaultValue = default_values["emissivity"])
        )
        layout.addRow(
            "Absorptivity:",
            self._registerField("absorptivity", "%.2f", defaultValue = default_values["absorptivity"])
        )
        layout.addRow(
            "Eff. radial th. conductivity:",
            self._registerField("effective_radial_thermal_conductivity", "%.2f [W / m K]", defaultValue = default_values["effective_radial_thermal_conductivity"])
        )
        layout.addRow(
            "Skin-effect factor:",
            self._registerField("skin_effect_factor", "%.4f", defaultValue = default_values["skin_effect_factor"])
        )
        layout.addRow(
            "Wetted factor:",
            self._registerField("wetted_factor", "%.2f", defaultValue = default_values["wetted_factor"])
        )
        layout.addRow(
            "Impinging factor:",
            self._registerField("impinging_factor", "%.2f", defaultValue = default_values["impinging_factor"])
        )
        layout.addRow(
            "Recovery factor:",
            self._registerField("recovery_factor", "%.2f", defaultValue = default_values["recovery_factor"])
        )
        layout.addRow(
            "Rough surface correction:",
            self._registerField("rough_surface_correction", "%.2f", defaultValue = default_values["rough_surface_correction"])
        )

        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(self._registerField("nusselt_base_1", "%.3f", defaultValue = default_values["nusselt_base_1"]))
        hbox.addWidget(self._registerField("nusselt_base_2", "%.3f", defaultValue = default_values["nusselt_base_2"]))
        hbox.addWidget(self._registerField("nusselt_base_3", "%.3f", defaultValue = default_values["nusselt_base_3"]))
        layout.addRow("Nusselt base:", hbox)

        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(self._registerField("nusselt_exp_1", "%.3f", defaultValue = default_values["nusselt_exp_1"]))
        hbox.addWidget(self._registerField("nusselt_exp_2", "%.3f", defaultValue = default_values["nusselt_exp_2"]))
        hbox.addWidget(self._registerField("nusselt_exp_3", "%.3f", defaultValue = default_values["nusselt_exp_3"]))
        layout.addRow("Nusselt exp.:", hbox)


class ConductorPartInfoWidget(_AutoFieldsWidgetMixin, QtWidgets.QGroupBox):
    def __init__(self, fieldPrefix, *args, default_values=None, **kwargs ):
        super().__init__(*args, **kwargs)
        default_values = default_values

        self.setAlignment(QtCore.Qt.AlignCenter)

        layout = QtWidgets.QFormLayout(self)
        layout.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)

        # Add fields
        layout.addRow(
            "Number of wires:",
            self._registerField(f"{fieldPrefix}_number_of_wires", "%d", defaultValue = default_values["number_of_wires"])
        )
        layout.addRow(
            "Diameter of wire:",
            self._registerField(f"{fieldPrefix}_diameter_of_wire", "%.2f [mm]", defaultValue = default_values["diameter_of_wire"])
        )
        layout.addRow(
            "Diameter:",
            self._registerField(f"{fieldPrefix}_diameter", "%.2f [mm]", defaultValue = default_values["diameter"])
        )
        layout.addRow(
            "Cross-section:",
            self._registerField(f"{fieldPrefix}_cross_section", "%.2f [mm²]", defaultValue = default_values["cross_section"])
        )
        layout.addRow(
            "Specific weight:",
            self._registerField(f"{fieldPrefix}_specific_weight", "%.1f [kg / m³]", defaultValue = default_values["specific_weight"])
        )
        layout.addRow(
            "Specific heat:",
            self._registerField(f"{fieldPrefix}_specific_heat", "%.1f [J / kg K]", defaultValue = default_values["specific_heat"])
        )
        layout.addRow(
            "Specific heat coeff.:",
            self._registerField(f"{fieldPrefix}_specific_heat_coefficient", "%.6f [1 / K]", defaultValue = default_values["specific_heat_coefficient"])
        )
        layout.addRow(
            "Resistivity coeff.:",
            self._registerField(f"{fieldPrefix}_resistivity_coefficient", "%.6f [1 / K]", defaultValue = default_values["resistivity_coefficient"])
        )


        layout.addRow(
            "Specific conductivity:",
            self._registerField(
                f"{fieldPrefix}_specific_conductivity",  "%.2f [MS / m]",
                lambda entry: entry[f"{fieldPrefix}_specific_conductivity"] / 1000000.0,  # S / m -> MS / m
                defaultValue=default_values["specific_conductivity"] / 1000000.0
            )
        )

        #dummy widget to set min width to 300
        hbox = QtWidgets.QHBoxLayout()
        placeholder = QtWidgets.QWidget()
        placeholder.setMinimumWidth(300)
        hbox.addWidget(placeholder)
        dummyWidget = QtWidgets.QWidget()
        dummyWidget.setLayout(hbox)
        layout.addRow(dummyWidget)


class ConductorInfoWidget(_AutoFieldsWidgetMixin,QtWidgets.QWidget):
    dataUpdated_temperature_thermal_limit = Signal(int, int)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        default_values_inner = {
            "specific_weight": 7780.0,
            "specific_heat": 900.0,
            "specific_heat_coefficient": 0.00038,
            "resistivity_coefficient": 0.0045,
            "specific_conductivity": 1450000.0,
            "cross_section": 0.0,
            "diameter": 0.0,
            "number_of_wires": 0,
            "diameter_of_wire": 0.0
            }
        default_values_outer = {
            "specific_weight": 2703.0,
            "specific_heat": 900.0,
            "specific_heat_coefficient": 0.0038,
            "resistivity_coefficient": 0.004,
            "specific_conductivity": 35400000.0,
            "cross_section": 0.0,
            "diameter": 0.0,
            "number_of_wires": 0,
            "diameter_of_wire": 0.0
            }
        default_values_common = {
            "conductor_cross_section": 0.0,
            "mass_per_unit_length": 0.0,
            "dc_resistance": 0.0,
            "effective_radial_thermal_conductivity": 2.0,
            "wetted_factor": 0.71,
            "impinging_factor": 1.0,
            "recovery_factor": 0.79,
            "skin_effect_factor": 1.0199,
            "absorptivity": 0.75,
            "emissivity": 0.75,
            "rough_surface_correction": 1.0,
            "nusselt_base_1": 0.641,
            "nusselt_base_2": 0.641,
            "nusselt_base_3": 0.048,
            "nusselt_exp_1": 0.471,
            "nusselt_exp_2": 0.471,
            "nusselt_exp_3": 0.8,
            "critical_temperature": 80.0,
            "static_thermal_limit": 960.0
            }

        self.setWindowFlags(QtCore.Qt.Window)
        self.setWindowTitle("Conductor information")

        layout = QtWidgets.QVBoxLayout(self)

        scrollArea = QtWidgets.QScrollArea()
        scrollArea.setWidgetResizable(True)
        layout.addWidget(scrollArea)

        scrollAreaWidget = QtWidgets.QWidget()
        scrollArea.setWidget(scrollAreaWidget)

        columnLayout = QtWidgets.QVBoxLayout(scrollAreaWidget)

        # Conductor INFO label
        self.labelConductorType = QtWidgets.QLabel("Press enter to save the JSON file:")
        self.labelConductorType.setFixedHeight(20)  # Set the height to 20 pixels
        layout.addWidget(self.labelConductorType)


        # Conductor type
        self.lineEditConductorType = QtWidgets.QLineEdit()
        self.lineEditConductorType.setPlaceholderText("Enter conductor type")
        self.lineEditConductorType.setFixedHeight(20)  # Set the height to 20 pixels
        self.lineEditConductorType.returnPressed.connect(self.dump_to_json)
        layout.addWidget(self.lineEditConductorType)
        #add another one called standards name
        # Standards Name QLineEdit
        self.lineEditStandardsName = QtWidgets.QLineEdit()
        self.lineEditStandardsName.setPlaceholderText("Enter standard's name")
        self.lineEditStandardsName.setFixedHeight(20)  # Ensure consistent height with the Conductor Type field
        self.lineEditStandardsName.returnPressed.connect(self.dump_to_json)
        # Add the new QLineEdit to the layout
        layout.addWidget(self.lineEditStandardsName)


        # Group boxes: inner and outer part
        hbox = QtWidgets.QHBoxLayout()
        layout.addLayout(hbox)

        self.widgetInner = ConductorPartInfoWidget("inner_part", "Inner part", default_values=default_values_inner)
        hbox.addWidget(self.widgetInner)

        self.widgetOuter = ConductorPartInfoWidget("outer_part", "Outer part", default_values=default_values_outer)
        hbox.addWidget(self.widgetOuter)

        # Group box: common conductor properties
        self.widgetCommon = ConductorCommonInfoWidget("Common conductor parameters", default_values=default_values_common)
        layout.addWidget(self.widgetCommon)

        layout.addStretch(1)

        self.conductor_type = "default_type"
        self.standards_name ="standard"

    def load_from_json(self):

        while True:
            try:
                filename, _ = QFileDialog.getOpenFileName(self, "Open JSON file", "",
                                                          "JSON files (*.json);;All files (*.*)")
                if not filename:
                    print("No file selected. Operation cancelled.")
                    return  # Exit the method if no file is selected

                with open(filename, 'r') as file:
                    data = json.load(file)


                name = data.get("name", "Unknown")
                self.updateConductorData(name, data)

                break  # Exit the loop and method after successful operation

            except Exception as e:
                print(f"Failed to load or parse the JSON file: {e}")
                retry = QtWidgets.QMessageBox.question(self, "Error", "Failed to load the file. Do you want to retry?",
                                                       QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
                if retry == QtWidgets.QMessageBox.No:
                    print("Operation cancelled by the user.")
                    break  # Exit the loop and method if the user decides not to retry



    def collect_spinbox_values(self, widget):
        spin_box_values = {}
        for child in widget.children():
            if isinstance(child, QtWidgets.QSpinBox) or isinstance(child, QtWidgets.QDoubleSpinBox):
                spin_box_values[child.objectName()] = child.value()
                if "specific_conductivity" in child.objectName() :
                    spin_box_values[child.objectName()] = (child.value() * 1000000.0) # MS / m -> S / m
            else:
                spin_box_values.update(self.collect_spinbox_values(child))
        return spin_box_values


    def dump_to_json(self):
        # Collect the values of all QSpinBox and QDoubleSpinBox widgets in the ConductorInfoWidget

        spin_box_inner = self.collect_spinbox_values(self.widgetInner)
        spin_box_common = self.collect_spinbox_values(self.widgetCommon)
        spin_box_outer = self.collect_spinbox_values(self.widgetOuter)
        self.conductor_type = self.lineEditConductorType.text()
        self.standards_name = self.lineEditStandardsName.text()

        #dummy values
        temperature = 80
        ampacity = 500

        # Create a dictionary for the conductor type and standard's name
        type_and_standard = {
            "name": self.conductor_type,
            "standard": self.standards_name,
        }
        # Combine all the collected values into one dictionary, ensuring type and standard are at the top
        self.data = {**type_and_standard, **spin_box_inner, **spin_box_outer, **spin_box_common,
            "critical_temperature": temperature,
            "static_thermal_limit": ampacity}

        # Delete all key-value pairs where the keys are empty
        #self.data = {k: v for k, v in self.data.items() if k}

        # Use QFileDialog to get the save file path from the user
        json_file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Save JSON File", "", "JSON files (*.json);;All files (*.*)"
        )

        # Check if a path was selected (i.e., the dialog was not canceled)
        if not json_file_path:
            print("Save operation cancelled.")
            return

        # Ensure the file has a .json extension
        if not json_file_path.endswith('.json'):
            json_file_path += '.json'

        # Write the data to the selected JSON file
        with open(json_file_path, 'w') as json_file:
            json.dump(self.data, json_file, indent=4)
        print(f"JSON file created at {json_file_path}")

    def updateConductorData(self, name, data):
        # Update the QLineEdit widgets with the conductor type and standards name
        self.lineEditConductorType.setText(name)
        self.lineEditStandardsName.setText(data.get("standard", ""))

        # with corresponding data for each part.
        self.widgetInner.updateData(data)
        self.widgetOuter.updateData(data)
        self.widgetCommon.updateData(data)


        # Emit signal to update the conductor data
        critical_temperature = int(data.get("critical_temperature", 0))  # Default to 0 if not found
        static_thermal_limit = int(data.get("static_thermal_limit", 0))  # Default to 0 if not found
        self.dataUpdated_temperature_thermal_limit.emit(critical_temperature, static_thermal_limit)


