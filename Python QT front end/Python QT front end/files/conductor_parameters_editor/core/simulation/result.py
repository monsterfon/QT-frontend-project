import dataclasses

from dlr_simutils_common.core.simulation.result import SimulationResult as SimulationResultBase


@dataclasses.dataclass
class SimulationResult(SimulationResultBase):
    # Timestamps
    time: list = None

    # Results
    ampacity: list = None
    time_to_overheat: list = None
    conductor_core_temperature: list = None

    # Input data
    ambient_temperature: list = None
    wind_speed: list = None
    wind_direction: list = None
    air_pressure: list = None
    rain_rate: list = None
    relative_humidity: list = None
    solar_irradiance: list = None
