from abc import ABC, abstractmethod
from typing import Any, Dict

from pandas import Timestamp

from qstrat.Data import yfconn


class Stock(ABC):
    """Abstract class for a stock."""
    _ticker: str = None
    _curr_price: float = 0.0
    _open: float = 0.0
    _high: float = 0.0
    _low: float = 0.0
    _close: float = 0.0
    _volume: float = 0.0
    _dividends: float = 0.0
    _stock_splits: float = 0.0

    def __init__(self, ticker: str, timestamp: Timestamp = None):
        self._ticker = ticker
        self.fetch_quote(timestamp)

    @abstractmethod
    def get(self) -> Dict[str, Any]:
        """Return a dictionary of stock information."""
        return {
            "ticker": self._ticker,
            "curr_price": self._curr_price,
            "open": self._open,
            "high": self._high,
            "low": self._low,
            "close": self._close,
            "volume": self._volume,
            "dividends": self._dividends,
            "stock_splits": self._stock_splits
        }

    @abstractmethod
    def view_data(self):
        """Return relevant data for view module."""
        pass

    def fetch_quote(self, timestamp: Timestamp = None):
        """Fetch the current quote information."""
        data = yfconn.get_stock_quote(self._ticker, timestamp)
        self._open = data['Open'].iloc[0]
        self._high = data['High'].iloc[0]
        self._low = data['Low'].iloc[0]
        self._close = data['Close'].iloc[0]
        self._curr_price = self._close
        self._volume = data['Volume'].iloc[0]
        self._dividends = data['Dividends'].iloc[0]
        self._stock_splits = data['Stock Splits'].iloc[0]


class Quote(Stock):
    """Class for a stock quote."""
    _timestamp: Timestamp = None

    def __init__(self, ticker: str, timestamp: Timestamp = None):
        super().__init__(ticker, timestamp)
        if timestamp is None:
            self._timestamp = Timestamp.now()
        else:
            self._timestamp = timestamp

    def get(self) -> Dict[str, Any]:
        """Return a dictionary of stock information from all class attributes."""
        res = super().get()
        res.update({
            "timestamp": self._timestamp,
        })
        return res

    def view_data(self) -> Dict[str, Any]:
        """Return relevant data for view module."""
        date = self._timestamp.strftime("%Y-%m-%d")
        time = self._timestamp.strftime("%H:%M:%S")
        return {
            "ticker": self._ticker,
            "curr_price": f"${self._curr_price:.2f}",
            "date": date,
            "time": time
        }


class Transaction(Stock):
    """Class for a stock transaction."""
    _executed_price: float = 0.0
    _executed_timestamp: Timestamp = None
    _quantity: int = 0
    _type: str = None
    _value: float = 0.0

    def __init__(self, ticker: str, quantity: int, timestamp: Timestamp = None):
        super().__init__(ticker, timestamp)
        if timestamp is None:
            self._executed_timestamp = Timestamp.now()
        else:
            self._executed_timestamp = timestamp
        if quantity > 0:
            self._type = "buy"
        elif quantity < 0:
            self._type = "sell"
        self._quantity = quantity
        self._executed_price = self._curr_price
        self._value = self._executed_price * self._quantity

    def get(self) -> Dict[str, Any]:
        res = super().get()
        res.update({
            "executed_price": self._executed_price,
            "executed_timestamp": self._executed_timestamp,
            "quantity": self._quantity,
            "type": self._type,
            "value": self._value
        })
        return res

    def view_data(self) -> Dict[str, Any]:
        return {
            "ticker": self._ticker,
            "type": self._type,
            "executed_price": f"${self._executed_price:.2f}",
            "quantity": self._quantity,
            "value": self._value,
            "date_time": f"{self._executed_timestamp}"
        }

    @property
    def executed_price(self):
        return self._executed_price

    @property
    def value(self):
        return self._value

    @property
    def quantity(self):
        return self._quantity

    @property
    def executed_timestamp(self):
        return self._executed_timestamp


class Position(Stock):
    _average_purchase_price: float = 0.0
    _purchase_value: float = 0.0
    _current_value: float = 0.0
    _quantity: int = 0
    _num_transactions: int = 0
    _pnl: float = 0.0
    _date_range: (Timestamp, Timestamp) = None

    def __init__(self, ticker: str, timestamp: Timestamp = None, initial_transaction: Transaction = None):
        if initial_transaction is not None:
            self._average_purchase_price = initial_transaction.executed_price
            self._purchase_value = initial_transaction.value
            self._current_value = self._purchase_value
            self._quantity = initial_transaction.quantity
            self._num_transactions = 1
            timestamp = initial_transaction.executed_timestamp
            self._date_range = (timestamp, timestamp)
        super().__init__(ticker, timestamp)

    def get(self) -> Dict[str, Any]:
        res = super().get()
        res.update({
            "average_purchase_price": self._average_purchase_price,
            "purchase_value": self._purchase_value,
            "current_value": self._current_value,
            "quantity": self._quantity,
            "num_transactions": self._num_transactions,
            "date_range": self._date_range
        })
        return res

    def view_data(self) -> Dict[str, Any]:
        return {
            "ticker": self._ticker,
            "purchase_value": f"${self._purchase_value:.2f}",
            "current_value": f"${self._current_value:.2f}",
            "quantity": self._quantity,
            "start_date": self._date_range[0] if self._date_range is not None else None,
            "end_date": self._date_range[1] if self._date_range is not None else None
        }

    def stack_transaction(self, transaction: Transaction):
        if transaction._ticker != self._ticker:
            raise ValueError("Transaction ticker does not match position ticker.")
        self._num_transactions += 1
        self._quantity += transaction.quantity
        if transaction.quantity > 0:
            self._purchase_value += transaction.value
        else:
            self._purchase_value += transaction.quantity * self._average_purchase_price
        self._current_value = self._quantity * transaction._curr_price
        self._pnl = self._current_value - self._purchase_value
        if self._quantity > 0:
            self._average_purchase_price = self._purchase_value / self._quantity
        else:
            self._average_purchase_price = 0.0
        if self._date_range is None:
            self._date_range = (transaction.executed_timestamp, transaction.executed_timestamp)
        else:
            self._date_range = (min(self._date_range[0], transaction.executed_timestamp),
                                max(self._date_range[1], transaction.executed_timestamp))

    @property
    def purchase_value(self):
        return self._purchase_value

    @property
    def current_value(self):
        return self._current_value

    @property
    def quantity(self):
        return self._quantity
