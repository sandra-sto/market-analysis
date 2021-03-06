import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.externals import joblib
from sklearn.preprocessing import MinMaxScaler

from market_analysis.deep_q_learning.preprocessing.data_transforms import DataTransforms
from market_analysis.features import DateFrameBuilder


class DataPreprocessor:

    _instance = None

    @staticmethod
    def get_instance():
        if DataPreprocessor._instance is None:
            DataPreprocessor._instance = DataPreprocessor()
        return DataPreprocessor._instance

    def __init__(self):
        self.minmaxscaler = None
        self.stocks_scaler = None
        self.budget_scaler = None

        self.data_transforms = DataTransforms()
        self.scaling = True

    def preprocess_data(self, data, stocks, budget):
        if data.size != 0:
            dataframe = self.build_dataframe(data)

            dataframe.dropna(inplace=True)
            # dataframe = data_transforms.remove_outliers(dataframe, 2.5)
            # dataframe = data_transforms.normalize_data(dataframe)

            # dataframe = self.data_transforms.smooth_data(dataframe, 10)
            dataframe = self.data_transforms.fill_missing_data(dataframe)

            dataframe.plot(legend = ['Price'])
            plt.title('Price')
            plt.legend()
            plt.grid(color = 'gray', linestyle = '-', linewidth = 0.25, alpha = 0.5)
            plt.show()

            if self.scaling:
                budget_min_max = np.array([0, 1])
                stocks_min_max = np.array([0, 1])

                if self.minmaxscaler == None:
                    self.minmaxscaler = MinMaxScaler()
                    self.stocks_scaler = MinMaxScaler()
                    self.budget_scaler = MinMaxScaler()

                    self.minmaxscaler.fit_transform(np.append(dataframe.values, 0).reshape(-1, 1))
                    self.stocks_scaler.fit(stocks_min_max.reshape(-1,1))
                    self.budget_scaler.fit(budget_min_max.reshape(-1,1))
                else:
                    self.minmaxscaler.transform(dataframe)

            return dataframe

        else: raise ValueError("There is no data")

    def transform_stocks(self, stocks):
        if self.scaling:
            return self.stocks_scaler.transform(stocks)[0][0]
        else:
            return stocks

    def transform_price_batch(self, data):
        if self.scaling:
            return pd.DataFrame(self.minmaxscaler.transform(data), index = data.index, columns = data.columns)
        else:
            return data

    def transform_price(self, price):
        if self.scaling:
            return self.minmaxscaler.transform(price)[0][0]
        else:
            return price

    def transform_budget(self, budget):
        if self.scaling:
            return self.budget_scaler.transform(budget)[0][0]
        else:
            return budget

    def inverse_transform_stocks(self, stocks):
        if self.scaling:
            return self.stocks_scaler.inverse_transform(stocks)[0][0]
        else:
            return stocks


    def inverse_transform_price(self, data):
        if self.scaling:
            return self.minmaxscaler.inverse_transform(data)[0][0]
        else:
            return data

    def inverse_transform_budget(self, budget):
        if self.scaling:
            return self.budget_scaler.inverse_transform(budget)[0][0]
        else:
            return budget

    def build_dataframe(self, data):
        dataframe = (
            DateFrameBuilder(data)
                # .add_returns()
                # .add_bolinger_bands_diff(7)
                .build()
        )
        return dataframe

    def save_scalars(self, folder):
        if folder[-1] != '/':
            folder = folder + '/'
        joblib.dump(self.minmaxscaler, folder + "price")
        joblib.dump(self.stocks_scaler, folder + "stocks")
        joblib.dump(self.budget_scaler, folder + "budget")

    def load_scalers(self, folder):
        if folder[-1] != '/':
            folder = folder + '/'

        self.minmaxscaler = joblib.load(folder + "price")
        self.stocks_scaler = joblib.load(folder + "stocks")
        self.budget_scaler =joblib.load(folder + "budget")
