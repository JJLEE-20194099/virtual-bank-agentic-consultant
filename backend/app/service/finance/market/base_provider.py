from abc import ABC, abstractmethod


class MarketDataProvider(ABC):

    @abstractmethod
    def get_ohlcv(self, symbol: str, start_date: str, end_date: str, interval: str):
        pass

    @abstractmethod
    def get_multiple(self, symbols: list[str]):
        pass