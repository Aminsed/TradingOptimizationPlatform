from utils import ms_to_dt
from typing import List, Tuple

import matplotlib.pyplot as plt



def plot_hist_data(symbol: str, data: List[Tuple]):
    timestamps, open_prices, high_prices, low_prices, close_prices, volumes = zip(*data)
    datetime_stamps = timestamps

    fig, ax1 = plt.subplots()
    ax1.plot(datetime_stamps, close_prices, label="Close Price", color='g')
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Price')
    ax1.legend(loc='upper left')

    ax2 = ax1.twinx()
    ax2.plot(datetime_stamps, volumes, label="Volume", color='b')
    ax2.set_ylabel('Volume')
    ax2.legend(loc='upper right')

    plt.title(f"{symbol} Historical Data")
    plt.show()
