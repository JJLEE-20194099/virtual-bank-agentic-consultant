from abc import ABC, abstractmethod


class MarketDataProvider(ABC):

    @abstractmethod
    async def get_ohlcv(self, symbol: str):
        pass

    @abstractmethod
    async def get_multiple(self, symbols: list[str]):
        pass