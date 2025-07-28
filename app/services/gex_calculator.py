# app/services/gex_calculator.py
from __future__ import annotations

import math
from collections import defaultdict
from datetime import date
from typing import Dict, List

from app.models.option_chain import OptionChain
from app.models.option_contract import OptionContract


class GexCalculator:
    """
    Calculate per-strike call/put GEX and the chain-level total.

    • Uses *1 %-move* scaling   → γ × OI × 100 × S² × 0.01
    • Calls are +, puts are –   (dealer-direction convention)
    • Slices to the N strikes closest to spot (default = 20).
    """

    # ────────────────────────────────────────────────────────────────────
    # public entry-point
    # ────────────────────────────────────────────────────────────────────
    def calc(
        self,
        chain: OptionChain,
        *,
        strikes: int = 20,
        risk_free: float = 0.05,
    ) -> Dict:
        """
        Parameters
        ----------
        chain     : OptionChain
        strikes   : int   → keep this many closest strikes (default 20)
        risk_free : float → annual risk-free rate for B-S fallback

        Returns
        -------
        dict  { symbol, as_of, total_gex, bars }
              bars → { strike : { "C": gex_call, "P": gex_put } }
        """
        # ---------- slice contracts ----------
        spot = chain.ticker.price
        contracts = self._closest_strikes(chain.contracts, spot, strikes)

        # ---------- aggregate ----------
        bars: Dict[float, Dict[str, float]] = defaultdict(
            lambda: {"C": 0.0, "P": 0.0}
        )
        total = 0.0

        for c in contracts:
            γ = (
                c.gamma
                if c.gamma is not None
                else self._bs_gamma(
                    spot,
                    c.strike,
                    self._years_to_exp(chain.as_of.date(), c.exp_date),
                    risk_free,
                    sigma=0.40,        # crude IV fallback
                )
            )

            # 1 %-move scaling
            gex = γ * c.open_interest * 100 * spot * spot * 0.01

            side = "C" if c.option_type.upper() == "C" else "P"
            signed = gex if side == "C" else -gex

            bars[c.strike][side] += signed
            total += signed

        return {
            "symbol": chain.ticker.symbol,
            "as_of": chain.as_of.isoformat(),
            "total_gex": total,   # USD change in dealer delta for 1 % move
            "bars": bars,
        }

    # ────────────────────────────────────────────────────────────────────
    # helpers (private)
    # ────────────────────────────────────────────────────────────────────
    @staticmethod
    def _closest_strikes(
        contracts: List[OptionContract], spot: float, n: int
    ) -> List[OptionContract]:
        """Return n contracts (≈ n strikes) nearest to spot."""
        return sorted(contracts, key=lambda c: abs(c.strike - spot))[:n]

    @staticmethod
    def _years_to_exp(as_of: date, exp: date) -> float:
        return max((exp - as_of).days, 0) / 365.0

    @staticmethod
    def _bs_gamma(
        S: float, K: float, T: float, r: float, sigma: float
    ) -> float:
        """Black-Scholes gamma for a European option."""
        if T <= 0 or sigma <= 0 or S <= 0:
            return 0.0
        d1 = (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (
            sigma * math.sqrt(T)
        )
        pdf = math.exp(-0.5 * d1 * d1) / math.sqrt(2 * math.pi)
        return pdf / (S * sigma * math.sqrt(T))
