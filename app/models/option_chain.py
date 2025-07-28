from dataclasses import dataclass
from datetime import datetime

from .option_chain import OptionContract
from .ticker import Ticker

@dataclass(slots=true)
class OptionChain:
    ticker: Ticker.symbol
    contracts: list[OptionContract]
    as_of: datetime

    def closest_strikes(self,n: int = 20) -> "OptionContract":
        spot = self.ticker.price
        closest = sorted(self.contracts, key=lambda c: abs(c.strike - spot))[:n]
        return OptionChain(self.ticker,self.as_of,closest)