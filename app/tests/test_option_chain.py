# tests/test_option_chain.py
from datetime import datetime, date
from models.ticker import Ticker
from models.option_contract import OptionContract
from models.option_chain import OptionChain

def test_chain_slice():
    tkr = Ticker("AAPL", 190.0, 10_000_000, datetime.utcnow())
    contracts = [
        OptionContract(187.5, date(2025,7,25), "C", 0.012, 0.45, 1000, 200),
        OptionContract(190.0, date(2025,7,25), "P", 0.013,-0.55, 900,  180),
    ]
    chain = OptionChain(tkr, tkr.as_of, contracts)
    assert len(chain.contracts) == 2
