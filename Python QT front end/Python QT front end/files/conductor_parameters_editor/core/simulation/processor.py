import collections

from .worker import SimulationWorker

from dlr_simutils_common.core.simulation.processor import SimulationProcessor as SimulationProcessorBase


class SimulationProcessor(SimulationProcessorBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _initializeProcessing(
        self,
        conductorType,
        lineData,
        initialWeatherData,
        initialLineLoad,
        changedWeatherData,
        changedLineLoad,
        numWorkers
    ):
        # Initialize numSamples and numWorkers - required by parent!
        self.numSamples = 1
        self.numWorkers = min(self.numSamples, numWorkers)

        # Store parametrization for sample generation
        self.conductorType = conductorType
        self.lineData = lineData
        self.initialWeatherData = initialWeatherData
        self.initialLineLoad = initialLineLoad
        self.changedWeatherData = changedWeatherData
        self.changedLineLoad = changedLineLoad

        # Reset sample counter
        self.numGeneratedSamples = 0

    def _createWorker(self, index):
        return SimulationWorker(index, self)

    def _createSimulationSample(self):
        # Called with synchronization lock
        if self.numGeneratedSamples >= self.numSamples:
            return None

        # There is, in fact, only one sample...
        self.numGeneratedSamples += 1

        # ... so it makes more sense to crate input data series here than in the worker.
        dataSeries = collections.defaultdict(lambda: [])

        STEP = 30  # half-minute time step (which also matches the simulation's discrete time step)
        DURATION = 3600  # 1 hour
        PRE_DURATION = 300  # 5 min
        WEATHER_KEYS = (
            'ambient_temperature',
            'wind_speed',
            'wind_direction',
            'air_pressure',
            'rain_rate',
            'relative_humidity',
            'solar_irradiance',
        )

        # -M * STEP, .., 0
        for timestamp in range(-PRE_DURATION, STEP, STEP):
            dataSeries["time"].append(timestamp)
            for key in WEATHER_KEYS:
                dataSeries[key].append(self.initialWeatherData[key])
            dataSeries["line_load"].append(self.initialLineLoad)

        # STEP, .., N * STEP
        for timestamp in range(STEP, DURATION + STEP, STEP):
            dataSeries["time"].append(timestamp)
            for key in WEATHER_KEYS:
                dataSeries[key].append(self.changedWeatherData[key])
            dataSeries["line_load"].append(self.changedLineLoad)

        dataSeries.default_factory = None

        return self.lineData, dataSeries
