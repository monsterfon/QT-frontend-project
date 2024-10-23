from .result import SimulationResult

from dlr_simutils_common.core.simulation.worker import SimulationWorker as SimulationWorkerBase
from dlr_simutils_common.core import diter


class SimulationWorker(SimulationWorkerBase):
    DATA_SERIES_KEYS = (
        'time',
        'ambient_temperature',
        'wind_speed',
        'wind_direction',
        'air_pressure',
        'rain_rate',
        'relative_humidity',
        'solar_irradiance',
        'line_load',
    )

    def _createResultForErrorMessage(self, error_message):
        return SimulationResult(
            succeeded=False,
            error_message=error_message,
        )

    def _initializeSimulationResult(self, sample):
        result = SimulationResult()

        # Copy input data series to the result structure
        _, dataSeries = sample

        for key in self.DATA_SERIES_KEYS:
            setattr(result, key, dataSeries[key])

        return result

    def _createDiterSimulationRequest(self, sample, pbd_file):
        lineData, dataSeries = sample

        # Convert data series into measurement entries list
        measurementEntries = []
        for idx in range(len(dataSeries["time"])):
            measurementEntries.append({
                key: dataSeries[key][idx]
                for key in self.DATA_SERIES_KEYS
            })

        # Generate and write simulation request protobuffer to file.
        request = diter.generate_simulation_request(
            lineData,
            measurementEntries,
            presimulation_time=7200,
        )
        diter.write_request_to_protobuffer(pbd_file, request)

    def _finalizeSimulationResult(self, result, csv_data):
        # Retrieve result series. Explicitly convert to python floats
        result.ampacity = [float(value) for value in csv_data[' I_th [A]']]
        result.conductor_core_temperature = [float(value) for value in csv_data[' T_core [deg C]']]
        result.time_to_overheat = [float(value) for value in csv_data[' time_to_overheat [s]']]
