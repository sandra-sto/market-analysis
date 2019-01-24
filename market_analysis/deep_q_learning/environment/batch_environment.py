from collections import namedtuple

import numpy as np

from market_analysis.deep_q_learning.environment.environment import Environment
from market_analysis.deep_q_learning.reinforcement.action import Action
State = namedtuple('State', ['s_return', 'bollinger_band_diff', 'sharpe_ratio', 'daily_return','stocks', 'budget'])


class BatchEnvironment(Environment):

    def __init__(self, reward, original_prices, preprocessor, agent_state):
        # super.__init__(reward, preprocessor, agent_state)
        self.data = preprocessor.transform_price_batch(original_prices)
        self.data = self.data.round(3)
        self.original_price = original_prices

        self.num_of_features = None

        super(BatchEnvironment, self).__init__(reward, preprocessor, agent_state)


    def get_num_of_states_per_training_episode(self):
        return self.data.shape[0]

    def reset(self):
        # self.unrp = self.agent_state.num_of_stocks*self.data.iloc[0]
        self.agent_state.reset()
        # self.num_of_stocks_bought = self.initial_num_of_stocks

        self.data_index = 1

        self.curr_state = self.create_state(self.data.iloc[0],
                                            self.preprocessor.transform_stocks(1),
                                            self.preprocessor.transform_budget(1),
                                            #
                                            # self.preprocessor.transform_stocks(self.agent_state.num_of_stocks),
                                            # self.preprocessor.transform_budget(self.agent_state.budget),
                                            self.preprocessor.transform_price(0))

    # def create_state(self, data, num_of_stocks, budget, inventory):
    #     values = np.array(data)
    #     # values = np.concatenate([data, data1, data2])
    #     values = np.append(data, [
    #         num_of_stocks,budget,inventory])
    #
    #     self.num_of_features = len(values)
    #     return values

    def step(self, action):
        new_state, done = self.get_new_state(self.curr_state, action)

        if new_state is None:
            reward = 0
        else:
            reward = self.reward(self.curr_state, action, new_state)

        if action == Action.Sell:
            self.agent_state.remove_inventory()
        self.data_index+=1
        self.curr_state = new_state

        return new_state, reward, done

    def get_new_state(self, state, action):
        price = self.original_price.ix[self.data_index-1, 'Price']
        if self.data_index == self.data.shape[0]:
            return None, True

        # stocks = self.preprocessor.transform_stocks(1)
        elif action == Action.Sell:
            self.action_sell(price)

            # self.agent_state.remove_inventory()
            # self.profit+=self.data.iloc[self.data_index]*1
            # self.profit+=self.preprocessor.transform_budget(state[0])*stocks
            # self.num_of_stocks_bought-= stocks
        elif action == Action.Buy:

            self.action_buy(price)

            # self.profit-=self.data.iloc[self.data_index]*1
            # self.unrp+=1*self.data.iloc[self.data_index]
            # self.num_of_stocks_bought+=stocks
        # self.unrp=self.agent_state.num_of_stocks*self.data.iloc[self.data_index]

        return self.create_state(self.data.ix[self.data_index],
                                self.preprocessor.transform_stocks(1 if self.agent_state.num_of_stocks>0 else 0),
                                self.preprocessor.transform_budget(1 if self.agent_state.budget>0*self.data.ix[self.data_index].values[0] else 0),
                                 # 0 if self.agent_state.get_inventory() == 0 else self.preprocessor.transform_price(self.agent_state.get_inventory())), False
                                self.preprocessor.transform_price(self.agent_state.get_inventory())), False