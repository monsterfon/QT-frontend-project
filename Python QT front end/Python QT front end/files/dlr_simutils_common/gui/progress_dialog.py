import math

from qtpy import QtCore, QtWidgets


def format_time_estimate(seconds):
    SECONDS_PER_DAY = 24 * 60 * 60
    days = int(seconds // SECONDS_PER_DAY)
    seconds -= days * SECONDS_PER_DAY

    SECONDS_PER_HOUR = 60 * 60
    hours = int(seconds // SECONDS_PER_HOUR)
    seconds -= hours * SECONDS_PER_HOUR

    SECONDS_PER_MINUTE = 60
    minutes = int(seconds // SECONDS_PER_MINUTE)
    seconds -= minutes * SECONDS_PER_MINUTE

    if days:
        return f"{days} day(s), {hours} hour(s)"
    elif hours:
        return f"{hours} hour(s), {minutes} minute(s)"
    elif minutes:
        return f"{minutes} minute(s), {seconds:.1f} seconds"
    else:
        return f"{seconds:.1f} seconds"


class _ConfirmationDialog(QtWidgets.QMessageBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle("Cancel processing?")
        self.setWindowModality(QtCore.Qt.WindowModal)

        self.setIcon(QtWidgets.QMessageBox.Question)
        self.setText("Are you sure you want to cancel processing?")
        self.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        self.setDefaultButton(QtWidgets.QMessageBox.No)


class _ReadOnlyLineEdit(QtWidgets.QLineEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setReadOnly(True)

    def sizeHint(self):
        # Prefer size that accommodates around 30 characters
        hint = super().sizeHint()
        metrics = self.fontMetrics()
        width = metrics.averageCharWidth() * 30
        if hint.width() < width:
            hint.setWidth(width)
        return hint


class ProgressDialog(QtWidgets.QDialog):
    canceled = QtCore.Signal(name="canceled")

    def __init__(self, numAllSamples, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.numAllSamples = numAllSamples
        self.isCanceled = False

        # *** UI ***
        self.setWindowTitle("Processing...")
        self.setWindowModality(QtCore.Qt.ApplicationModal)

        layout = QtWidgets.QFormLayout(self)
        layout.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)

        self.labelProcessing = QtWidgets.QLabel("Processing... please wait")
        layout.addRow(self.labelProcessing)

        self.lineEditProcessedSamples = _ReadOnlyLineEdit()
        self.lineEditProcessedSamples.setToolTip(
            "<span>Number of processed samples.</span>"
        )
        layout.addRow("Processed samples:", self.lineEditProcessedSamples)

        self.lineEditEstimatedTime = _ReadOnlyLineEdit()
        self.lineEditEstimatedTime.setToolTip(
            "<span>Estimated time to process remaining samples.</span>"
        )
        layout.addRow("Estimated time:", self.lineEditEstimatedTime)

        self.progressBar = QtWidgets.QProgressBar()
        self.progressBar.setRange(0, numAllSamples)
        layout.addRow(self.progressBar)

        # Button box
        buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        layout.addRow(buttonBox)

        self.buttonBox = buttonBox

        # Confirmation dialog - we must not use `QtWidgets.QMessageBox.question()` to confirm cancellation, because
        # the processing might reach the end before user selects the answer. In that case, tearing down the progress
        # dialog ends up in a crash because the confirmation dialog will block the execution while spinning a local
        # event loop. So instead, instantiate proper modal instance, and show it when confirmation is required (as
        # part of main event loop).
        self.confirmationDialog = _ConfirmationDialog(parent=self)
        self.confirmationDialog.accepted.connect(self.onConfirmCancellation)

        # Initial update
        self.updateProgress(0, 0, float('nan'))

    def updateProgress(self, numProcessedSamples, numFailures, estimatedTime):
        # No updates if we are in process of canceling operation
        if self.isCanceled:
            return

        # Update progress in dialog title
        progress = 100 * numProcessedSamples / self.numAllSamples
        self.setWindowTitle(f"Processing ({progress:.1f}%)...")

        # Update progress in line edit (processes samples and failures count)
        self.lineEditProcessedSamples.setText(
            f"{numProcessedSamples} / {self.numAllSamples} ({numFailures} failures)"
        )

        # Update progress bar
        self.progressBar.setValue(numProcessedSamples)

        # Update estimated time
        if math.isfinite(estimatedTime):
            self.lineEditEstimatedTime.setText(
                format_time_estimate(estimatedTime)
            )
        else:
            self.lineEditEstimatedTime.setText("N/A")

    def reject(self):
        # Do nothing if user already confirmed cancellation
        if self.isCanceled:
            return

        # Show the confirmation dialog
        self.confirmationDialog.show()

    def onConfirmCancellation(self):
        # Update the UI...
        self.setWindowTitle("Aborting...")
        self.labelProcessing.setText("Aborting processing... please wait")
        self.progressBar.setRange(0, 0)

        self.buttonBox.button(QtWidgets.QDialogButtonBox.Cancel).setEnabled(False)  # Disable the button

        # ... and signal cancellation
        self.isCanceled = True
        self.canceled.emit()
