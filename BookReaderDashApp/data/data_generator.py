import numpy as np
import csv
import pandas as pd

path = 'data/data_book_big.csv'

# Creates new set of data
# TODO: Stop using fixed values in fonction

def create_more_date(number):
    volumes = np.round(np.random.binomial(200, 0.5, 2 * number), 1)
    start_nanos_epoch = 1565157926599450000
    periods = start_nanos_epoch + np.cumsum(np.random.binomial(1000, 0.5, number) * 1000)
    datetimes = pd.to_datetime(periods)
    msuk, source, tradePx, tradeSz, channelId, seqNum, msgIdx = 79889147, 'EUREX', 0, 0, 0, 597283, 0
    prices_bid = create_prices(number)
    prices_ask = prices_bid + np.round(np.random.gamma(0.2, 0.1, size=number), 2)
    data = []
    for i in range(number):
        line = [periods[i], datetimes[i], msuk, source,
                prices_bid[i], volumes[2 * i], prices_ask[i], volumes[2 * i + 1],
                prices_bid[i], volumes[2 * i], prices_ask[i], volumes[2 * i + 1],
                tradePx, tradeSz, channelId, seqNum, msgIdx]
        data.append(line)
    return data


def create_prices(number):
    percent_changes = np.random.normal(0.0001, 0.01, number)
    prices = 82.2 * np.exp(np.cumsum(percent_changes))
    return np.round(prices, 3)


def save_data(data, path):
    with open(path, mode='w') as f:
        writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for line in data:
            writer.writerow(line)


# f'source Modify CAU19(79889147) Sell 1819@82.8 (new qty/price) lvl=6 new number of orders = 31 src=2019-08-07 01:14:22.433700419 CDT our=2019-08-07 01:14:22.433706420 CDT flags= seq=227633875336 bid:37@82.2 ask:1137@82.3 cbid:37@82.2 cask:1137@82.3'
# data = create_more_date(1000)
# save_data(data)
