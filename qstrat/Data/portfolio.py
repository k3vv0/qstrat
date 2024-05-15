from typing import List, Dict

from pandas import Timestamp

from qstrat.Data.stock import Position, Transaction


class Portfolio:
    """Class for a portfolio."""
    _start_date: Timestamp = None
    _end_date: Timestamp = None
    _positions: Dict[str, Position] = {}
    _cash_balance: float = 0.0
    _total_value: float = 0.0
    _total_paid: float = 0.0

    def __init__(self, cash: float = 5000.0, tickers: List[str] = None, config: str = None):
        if config is not None:
            # Load from the configuration file.
            # load_config(config)
            pass
        else:
            if tickers is not None:
                for ticker in tickers:
                    self._positions[ticker] = Position(ticker)
            self._cash_balance = cash
            self._total_value = cash
            self._start_date = self._end_date = Timestamp.now()

    def __str__(self):
        """Return a string representation of the portfolio."""
        res = f"Portfolio:\n"
        for ticker, pos in self._positions.items():
            res += f"{ticker}: {pos.quantity}\n"
        res += f"Cash: ${self._cash_balance:.2f}\n"
        res += f"Total value: ${self._total_value:.2f}\n"
        return res

    def buy(self, ticker, quantity, timestamp=None):
        """Buy a quantity of a stock at a given price."""
        t = Transaction(ticker, quantity, timestamp)
        if ticker not in self._positions:
            self._positions[ticker] = Position(ticker, initial_transaction=t)
        else:
            self._positions[ticker].stack_transaction(t)
        self.update_balances(t.value)
        pass

    def sell(self, ticker, quantity, timestamp=None):
        """Sell a quantity of a stock at a given price."""
        t = Transaction(ticker, -quantity, timestamp)
        if ticker not in self._positions:
            self._positions[ticker] = Position(ticker, initial_transaction=t)
        else:
            self._positions[ticker].stack_transaction(t)
        self.update_balances(t.value)
        pass

    def update_balances(self, value: float):
        """Calculate the total value of the portfolio given current prices."""
        purchase_value = 0.0
        current_value = 0.0
        for pos in self._positions.values():
            purchase_value += pos.purchase_value
            current_value += pos.current_value
        self._cash_balance -= value
        self._total_paid = purchase_value
        self._total_value = current_value + self._cash_balance


if __name__ == "__main__":
    # Build sample portfolio with NVDA, AAPL, and XOM.
    p = Portfolio(tickers=["NVDA", "AAPL", "XOM"])
    print(p)
    p.buy("NVDA", 10, Timestamp("2021-01-11"))
    p.buy("AAPL", 5, Timestamp("2021-01-11"))
    p.buy("XOM", 10, Timestamp("2021-01-11"))
    print(p)
    p.sell("AAPL", 3, Timestamp("2022-01-04"))
    print(p)
    p.sell("XOM", 5, Timestamp("2023-01-05"))
    print(p)
    p.sell("NVDA", 5, Timestamp("2024-01-04"))
    print(p)
