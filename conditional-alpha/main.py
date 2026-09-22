from AlgorithmImports import *


class AlphaReaderLab(QCAlgorithm):
    """Packaging-only backtest. Open research.ipynb for the teaching experiment."""

    def initialize(self):
        self.set_start_date(2024, 1, 2)
        self.set_end_date(2024, 1, 3)
        self.set_cash(100000)
        self.add_equity("SPY", Resolution.DAILY)
        self.debug("Open research.ipynb and Run All. This packaging backtest places no trades.")

    def on_data(self, data):
        pass
