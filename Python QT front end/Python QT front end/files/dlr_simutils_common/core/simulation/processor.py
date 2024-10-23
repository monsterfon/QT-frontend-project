import logging
import threading
import itertools
import math
import statistics

from qtpy import QtCore


logger = logging.getLogger(__name__)


class SimulationProcessor(QtCore.QObject):
    processingStarted = QtCore.Signal(int, name="processingStarted")
    processingFinished = QtCore.Signal(name="processingFinished")
    processingProgress = QtCore.Signal(int, int, float, name="processingProgress")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.abortOnError = False

        # Status flags
        self.isActive = False
        self.wasCanceled = False
        self.wasAborted = False

        self.workers = []
        self.syncLock = threading.Lock()

        self.results = []

        # Timer for collating the progress update when workers finish shortly after each other
        self.progressUpdateTimer = QtCore.QTimer()
        self.progressUpdateTimer.setInterval(500)
        self.progressUpdateTimer.setSingleShot(True)
        self.progressUpdateTimer.timeout.connect(self.signalProgressUpdate)

    def _initializeProcessing(self, *args, **kwargs):
        raise NotImplementedError()

    def _createWorker(self, index):
        raise NotImplementedError()

    def _createSimulationSample(self):
        raise NotImplementedError()

    def processData(self, *args, **kwargs):
        if self.isActive:
            raise RuntimeError("Processing already active!")

        # Initialize implementation-specific details of processing engine.
        self.numSamples = None
        self.numWorkers = None

        self._initializeProcessing(*args, **kwargs)

        assert self.numSamples is not None, "initializeProcessing() did not initialize self.numSamples!"
        assert self.numWorkers is not None, "initializeProcessing() did not initialize self.numWorkers!"

        # Clear flags
        self.isActive = True
        self.wasCanceled = False
        self.wasAborted = False

        self.results = []

        # Create workers
        self.workers = set()
        for i in range(self.numWorkers):
            worker = self._createWorker(i)  # Create implementation-specific worker!
            worker.simulationResultReady.connect(self.onWorkerResultReady)
            worker.workerFinished.connect(self.onWorkerFinished)
            self.workers.add(worker)

        # Start workers...
        self.processingStarted.emit(self.numSamples)

        for worker in self.workers:
            worker.start()

    def cancelProcessing(self):
        # Set the flag that prevents us from serving any more samples to workers.
        self.wasCanceled = True

        # Terminate the current processes in workers, if necessary.
        for worker in self.workers:
            worker.cancel()

    def onWorkerFinished(self):
        worker = self.sender()

        worker.join()  # Ensure worker's thread has fully exited

        # Remove worker from list; when no workers are left, we are done,
        # one way or another.
        self.workers.remove(worker)
        if not self.workers:
            self.isActive = False

            self.processingFinished.emit()

    def getNextSimulationSample(self):
        # Called by workers from their threads; synchronize via lock
        with self.syncLock:
            if not self.isActive or self.wasCanceled or self.wasAborted:
                return None

            # Sample creation is implementation-specific...
            return self._createSimulationSample()

    def onWorkerResultReady(self, result):
        # Store results
        self.results.append(result)

        # Abort on error
        if not result.succeeded and self.abortOnError:
            self.wasAborted = True
            # Terminate the current processes in workers, if necessary.
            for worker in self.workers:
                worker.cancel()

            return

        # Signal update - use timer to collate results that arrive
        # shortly together
        if not self.progressUpdateTimer.isActive():
            self.progressUpdateTimer.start()

    def signalProgressUpdate(self):
        # Only if we are still processing; due to the collation delay, it might happen that we reached the end or were
        # canceled since the original signal.
        if not self.isActive or self.wasCanceled or self.wasAborted:
            return

        # Estimate time based on last N successful results
        elapsedTimes = (
            entry.elapsed_time for entry in reversed(self.results)
            if math.isfinite(entry.elapsed_time)
        )
        elapsedTimes = itertools.islice(elapsedTimes, 25)
        try:
            elapsedTime = statistics.median(elapsedTimes)
        except statistics.StatisticsError:
            elapsedTime = math.nan  # Cannot estimate

        remainingSamples = self.numSamples - len(self.results)
        estimatedTime = elapsedTime * remainingSamples / len(self.workers)

        # Update progresss
        self.processingProgress.emit(
            len(self.results),
            len([entry for entry in self.results if not entry.succeeded]),
            estimatedTime,
        )
