from qtpy import QtCore, QtWidgets


class SearchableComboBox(QtWidgets.QComboBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Make combo box searchable
        self.setEditable(True)
        self.setInsertPolicy(QtWidgets.QComboBox.NoInsert)

        proxy = QtCore.QSortFilterProxyModel()
        proxy.setSourceModel(self.model())
        proxy.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        proxy.setFilterKeyColumn(self.modelColumn())
        self._proxy = proxy

        completer = QtWidgets.QCompleter()
        completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        completer.setModel(proxy)
        completer.setCompletionColumn(self.modelColumn())
        completer.setCompletionMode(QtWidgets.QCompleter.UnfilteredPopupCompletion)
        self.setCompleter(completer)
        self._competer = completer

        self.editTextChanged.connect(proxy.setFilterFixedString)

    def replaceEntries(self, entries):
        # Store old choice
        previouslySelected = self.currentData()

        # Temporarily disable proxy to avoid warnings about inconsistent state
        self._proxy.setSourceModel(None)

        self.clear()
        for name in entries:
            self.addItem(name, name)

        # Re-enable proxy
        self._proxy.setSourceModel(self.model())

        # Restore old choice
        previousIdx = self.findData(previouslySelected)
        if previousIdx != -1:
            self.setCurrentIndex(previousIdx)


class ParametrizedFieldsMixIn:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._parametersMap = {}

    def _registerParameterField(self, parameterName, spinBox):
        self._parametersMap[parameterName] = spinBox

    def _collectParameters(self):
        return {
            parameterName: spinBox.value()
            for parameterName, spinBox in self._parametersMap.items()
        }

    def _populateFields(self, data):
        for parameterName, spinBox in self._parametersMap.items():
            try:
                value = data[parameterName]
            except KeyError:
                continue
            spinBox.setValue(value)
