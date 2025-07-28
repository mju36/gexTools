from dataclasses import dataclass
from datetime import datetime

@dataclass(slots=true)
class Ticker:
    symbol: str
    price: float
    volume: int
    as_of: datetime  # last quoted
