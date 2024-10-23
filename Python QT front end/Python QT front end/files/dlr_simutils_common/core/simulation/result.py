import dataclasses
import math


@dataclasses.dataclass
class SimulationResult:
    # Status
    succeeded: bool = False
    error_message: str = None
    elapsed_time: float = math.nan
