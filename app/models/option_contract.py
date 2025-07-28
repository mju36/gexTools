from dataclasses import dataclass
from datetime import datetime

@dataclass(slots=true)
class optionContract:
    strike: float
    exp_date: datetime
    option_type: str
    volume: int
    gamma: float
    delta: float
    
