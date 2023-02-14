
# Historical Data Downloader | Backtesting | Optimization

This repository is dedicated for downloading historical cryptocurrency data as well as testing trading strategies and optimization of strategies.



## Historical Data Downloader
Install dependencies

```bash
  pip install -r requirements.txt
```

Start the application

```bash
  python3 main.py
```

Select data
```bash
  Choose the program mode (data / backtest / optimize):
  data
```

Choose a broker to download data from (Binance or FTX) 
example:
```bash
  Choose an exchange: binance
```
Select a crypto coin name to download. 
example:
```bash
  Choose a symbol: btcusdt
```
There is slight difference between Binance and FTX in the way they list crypto names. For example: for Binance we use BTCUSDT whereas for FTX we use BTC/USD. Please refer to binance_symbols.txt and ftx_symbols.txt for list of available crypto pair names. In case of Dukascopy, this broker uses an ID instead of the symbol name. For example, if you want to download BTCUSD value you have to use its ID value of 75304 instead. To find the corresponding ID of each symbol please refer to dukascopy_symbols.csv.

After downloading process has been completed the data can be found under the *data/* folder.

To view the data we can use HDF View application:
https://www.hdfgroup.org/downloads/hdfview/

To read the data we can use different methods either through Python's standard library or Pandas, to learn more please visit:
https://stackoverflow.com/questions/28170623/how-to-read-hdf5-files-in-python
