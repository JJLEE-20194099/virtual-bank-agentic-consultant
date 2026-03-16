from app.service.finance.market.vndirect_provider import VNDirectProvider

class MarketService:

    def __init__(self):

        self.provider = VNDirectProvider()

    def get_ohlcv(self, symbol, start_date, end_date, interval):

        return self.provider.get_ohlcv(symbol, start_date, end_date, interval)

    def get_ohlcv_by_length(self, symbol, length, interval):
        return self.provider.get_ohlcv_by_length(symbol, length, interval)

    def get_multiple(self, symbols):
        return self.provider.get_multiple(symbols)