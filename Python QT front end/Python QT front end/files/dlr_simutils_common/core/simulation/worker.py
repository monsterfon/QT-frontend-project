import logging
import threading
import pathlib
import subprocess
import tempfile
import time

from qtpy import QtCore
import pandas as pd

from .. import diter


logger = logging.getLogger(__name__)


class SimulationWorker(QtCore.QObject):
    workerFinished = QtCore.Signal(name="workerFinished")
    simulationResultReady = QtCore.Signal(object, name="simulationResultReady")

    def __init__(self, worker_id, processor, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.worker_id = worker_id
        self.processor = processor

        self.dtr_process = None
        self.thread = threading.Thread(target=self._processingLoop, daemon=True)
        self.thread.name = f"Processing worker thread #{worker_id}"

    def _createResultForErrorMessage(self, error_message):
        raise NotImplementedError()

    def _initializeSimulationResult(self, sample):
        raise NotImplementedError()

    def _createDiterSimulationRequest(self, sample, pbdf_file):
        raise NotImplementedError()

    def _finalizeSimulationResult(self, result, csv_data):
        raise NotImplementedError()

    def start(self):
        self.thread.start()

    def join(self):
        self.thread.join()

    def cancel(self):
        # If we have a DiTeR process running, terminate it
        if self.dtr_process:
            self.dtr_process.kill()

    def _processingLoop(self):
        while True:
            # Get next sample from processor
            sample = self.processor.getNextSimulationSample()
            if sample is None:
                break

            # Process sample
            logger.debug("Worker #%i processing a sample...", self.worker_id)
            try:
                result = self._processSample(sample)
                logger.debug("Worker #%i processed sample in %.2f seconds...", self.worker_id, result.elapsed_time)
            except Exception as e:
                logger.warning("Worker #%i failed to process sample!", self.worker_id, exc_info=True)
                # Use implementation-specific helper so that result is of implementation-specific result type.
                result = self._createResultForErrorMessage(f"Unhandled exception: {e}")

            # Submit result
            self.simulationResultReady.emit(result)

        # End of loop
        logger.debug("Worker #%i exited its processing loop!", self.worker_id)
        self.workerFinished.emit()

    def _processSample(self, sample):
        # Process the sample
        start_time = time.time()

        # Use implementation-specific helper to initialize the result structure (e.g., store input data and parameters,
        # if necessary).
        result = self._initializeSimulationResult(sample)

        # *** Simulation ***
        with tempfile.TemporaryDirectory(prefix='diter_sim.') as tmp_path:
            tmp_dir = pathlib.Path(tmp_path)

            # Generate and write protobuffer for simulation
            pbd_file_prefix = "simulation"
            pbd_file = tmp_dir / f"{pbd_file_prefix}.pbd"

            self._createDiterSimulationRequest(sample, pbd_file)

            # Create simulation_out directory
            output_dir = tmp_dir / "simulation_output"
            output_dir.mkdir()

            # Process
            # NOTE: DiTeR executable does some rather naive input file name processing to obtain the base name, which
            # falls apart when full path is given (especially on Windows). Since we need to change into temporary
            # directory anyway, pass the relative input file name as well.
            self.dtr_process = subprocess.Popen(
                [diter.diter_exe, str(pbd_file.name)],
                cwd=str(tmp_dir),
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            text_stdout, text_stderr = self.dtr_process.communicate()

            # Read results
            if self.dtr_process.returncode == 0:
                output_file = output_dir / f"{pbd_file_prefix}_history.csv"

                # NOTE: dtr1d_main seems to use ", " as a separator. However, using multiple separators causes pandas to
                # use python-based parser instead of C-based one. So parse with "," as separator (the default), and add
                # spaces to column names...
                output_data = pd.read_csv(output_file)

                result.succeeded = True

                # Parse the result using implementation-specific helper.
                self._finalizeSimulationResult(result, output_data)
            else:
                result.succeeded = False
                result.error_message = "DiTeR process exited with non-zero status."

                # Display stderr and stdout
                logger.warning(
                    "DiTeR process exited with non-zero status!\n"
                    "Protobuffer:\n%s\n"
                    "Standard output:\n%s\n"
                    "Standard error:\n%s\n",
                    pbd_file.read_text(),
                    text_stdout,
                    text_stderr,
                    )

            result.elapsed_time = time.time() - start_time

        return result
