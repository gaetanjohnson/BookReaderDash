import numpy as np
import csv
import pandas as pd
from pathlib import Path

# Creates new set of data
class DataGenerator:
    FIRST_LINE = 'nanosEpoch,time,msuk,source,cbidPx,cbidSz,caskPx,caskSz,bidPx,bidSz,askPx,askSz,tradePx,tradeSz,channelId,seqNum,msgIdx'
    DATA_DIR = Path(__file__).resolve().parent.joinpath("../data")

    @classmethod
    def _save_data(cls, mode, path, data):
        with open(path, mode='w') as f:
            writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            if mode == 'top':
                f.write(cls.FIRST_LINE)
            for line in data:
                writer.writerow(line) if mode == 'top' else f.write(line + '\n')

    @classmethod
    def _generate_data(cls, quantity, mode, **kwargs):
        start_nanos_epoch = kwargs.get('start_nanos_epoch', 1565157926599450000)
        average_time_delta = kwargs.get('average_time_delta', 1000)
        msuk = kwargs.get('msuk', 79889147)
        source = kwargs.get('source', 'EUREX')
        channelId = kwargs.get('channelId', 0)
        msgIdx = kwargs.get('msgIdx', 0)
        average_volume = kwargs.get('average_volume', 200)
        variance = kwargs.get('variance', 0.5)
        base_rate = kwargs.get('base_rate', 0.001)
        vol = kwargs.get('vol', 0.003)
        base_price = kwargs.get('base_price', 82.2)
        seqNum = kwargs.get('seqNum', 597283)

        times = cls._generate_times(quantity, start_nanos_epoch, average_time_delta)
        datetimes = pd.to_datetime(times)
        volumes = cls._generate_volumes(quantity, average_volume, variance)
        prices_bid = cls._generate_prices(quantity, base_rate, vol, base_price)
        spreads = cls._generate_spreads(quantity)
        prices_ask = prices_bid + spreads
        trade_prices = cls._generate_trades(quantity)
        volumes_bid, volumes_ask, volumes_trade = volumes[:quantity], volumes[quantity:2*quantity], volumes[:2*quantity]
        direction = cls._generate_directions(quantity)
        data = []
        for i in range(quantity):
            if mode == 'top':
                line = [times[i], datetimes[i], msuk, source,
                        prices_bid[i], volumes_bid[i], prices_ask[i], volumes_ask[i],
                        prices_bid[i], volumes_bid[i], prices_ask[i], volumes_ask[i],
                        trade_prices[i], volumes_trade[i], channelId, seqNum, msgIdx]
            else:
                line = f'source Modify CAU19({msuk}) {direction[i]} {volumes_trade[i]}@{trade_prices[i]} (new qty/price) ' \
                       f'lvl=6 new number of orders = 31 src={datetimes[i]} CDT our={datetimes[i]} CDT flags= ' \
                       f'seq={seqNum} bid:{volumes_bid[i]}@{prices_bid[i]} ask:{volumes_ask[i]}@{prices_ask[i]} ' \
                       f'cbid:{volumes_bid[i]}@{prices_bid[i]} cask:{volumes_ask[i]}@{prices_ask[i]}'

            data.append(line)
        return data

    @classmethod
    def _generate_data_from_file(cls, df, mode, **kwargs):
        msuk = kwargs.get('msuk', '000')
        source = kwargs.get('source', 'EUREX')
        channelId = kwargs.get('channelId', 0)
        msgIdx = kwargs.get('msgIdx', 0)
        seqNum = kwargs.get('seqNum', 597283)
        direction = df['type'].map({'a': 'Sell', 'b': 'Buy'})
        volumes_trade = df['amount'].values
        trade_prices = df['price'].values

        df_ask, df_bid = df[df['type'] == 'a'], df[df['type'] == 'b']
        df_best_ask = df_ask.loc[df_ask.groupby('date')['price'].idxmin()].drop(columns=['type'])
        df_best_bid = df_bid.loc[df_bid.groupby('date')['price'].idxmax()].drop(columns=['type'])
        df_best_ask.columns = ['date', 'best_ask', 'best_ask_vol']
        df_best_bid.columns = ['date', 'best_bid', 'best_bid_vol']
        prices_ask = df_best_ask['best_ask'].values
        prices_bid = df_best_bid['best_bid'].values
        volumes_ask = df_best_ask['best_ask_vol'].values
        volumes_bid = df_best_bid['best_bid_vol'].values
        data = []

        if mode == 'top':
            times = df_best_ask['date'].values
            datetimes = pd.to_datetime(times, unit='ms').values
            for i, time in enumerate(times):
                line = [time, datetimes[i], msuk, source,
                        prices_bid[i], volumes_bid[i], prices_ask[i], volumes_ask[i],
                        prices_bid[i], volumes_bid[i], prices_ask[i], volumes_ask[i],
                        0, 0, channelId, seqNum, msgIdx]
                data.append(line)

        else:
            df = df.join(df_best_ask.set_index('date'), on='date')
            df = df.join(df_best_bid.set_index('date'), on='date')
            prices_ask = df['best_ask'].values
            prices_bid = df['best_bid'].values
            volumes_ask = df['best_ask_vol'].values
            volumes_bid = df['best_bid_vol'].values
            times = df['date'].values
            datetimes = pd.to_datetime(times, unit='ms').values
            for i, time in enumerate(times):
                distance = (prices_bid[i] - trade_prices[i]) / prices_bid[i] if direction[i] == 'Buy' \
                    else (trade_prices[i] - prices_ask[i]) / prices_ask[i]
                if distance < 0.01:
                    line = f'source Modify CAU19({msuk}) {direction[i]} {volumes_trade[i]}@{trade_prices[i]} (new qty/price) ' \
                           f'lvl=6 new number of orders = 31 src={datetimes[i]} CDT our={datetimes[i]} CDT flags= ' \
                           f'seq={seqNum} bid:{volumes_bid[i]}@{prices_bid[i]} ask:{volumes_ask[i]}@{prices_ask[i]} ' \
                           f'cbid:{volumes_bid[i]}@{prices_bid[i]} cask:{volumes_ask[i]}@{prices_ask[i]}'

                    data.append(line)
        return data


    @classmethod
    def _generate_times(cls, quantity, start_nanos_epoch, average_time_delta):
        return start_nanos_epoch + np.cumsum(np.random.binomial(average_time_delta, 0.5, quantity) * 1000)

    @classmethod
    def _generate_volumes(cls, quantity, average_volume, variance):
        return np.round(np.random.binomial(average_volume, variance, 3 * quantity), 1)

    @classmethod
    def _generate_prices(cls, quantity, base_rate, vol, base_price):
        percent_changes = np.random.normal(base_rate, vol, quantity)
        prices = base_price * np.exp(np.cumsum(percent_changes))
        return np.round(prices, 3)

    # Not very realistic
    @classmethod
    def _generate_spreads(cls, quantity):
        return np.round(np.random.gamma(0.2, 0.1, size=quantity), 2)

    # TODO: Think of clever ways to generate trades
    @classmethod
    def _generate_trades(cls, quantity):
        return [0] * quantity

    @classmethod
    def _generate_directions(cls, quantity):
        return np.random.choice(['Buy', 'Sell'], quantity)

    @classmethod
    def create_more_data(cls, quantity, mode='top', **kwargs):
        if mode not in ['top', 'line']:
            raise ValueError('Data Generation mode should be either top or line')
        data = cls._generate_data(quantity, mode, **kwargs)
        extension = '.csv' if mode == 'top' else '.txt'
        file_name = 'new_data' + extension
        path = cls.DATA_DIR / file_name
        cls._save_data(mode, path, data)

    @classmethod
    def create_more_data_from_file(cls, filepath, mode='top', **kwargs):
        if mode not in ['top', 'line']:
            raise ValueError('Data Generation mode should be either top or line')
        df = pd.read_csv(filepath)
        data = cls._generate_data_from_file(df, mode, **kwargs)
        extension = '.csv' if mode == 'top' else '.data'
        file_name = 'data_' + mode + 'new' + extension
        path = cls.DATA_DIR / file_name
        cls._save_data(mode, path, data)

# quantity = 200
# mode = 'top'
# params = {}
# DataGenerator.create_more_data(quantity, mode, **params)
file_path = './BitMEX_XBTUSD_RAW.csv'
mode = 'line'
DataGenerator.create_more_data_from_file(file_path, mode)