class RealTimeTradingDataGetter:
    def __init__(self, db_worker, data_preprocessor):
        self.db_worker = db_worker
        self.data_preprocessor = data_preprocessor
        self.last_timestamp = None

    def is_new_data_present(self, ticker):
        self.instance = self.get_data(ticker)

        return self.instance.name != self.last_timestamp


    def get_new_data(self, ticker):
        self.last_timestamp = self.instance.name

        return self.instance

    def get_data(self, ticker):
        data = self.db_worker.get_trades(ticker, 50)
        return data.iloc[-1]
