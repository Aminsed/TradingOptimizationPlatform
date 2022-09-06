// On Balance Volume strategy
Obv::Obv(char* exchange_c, char* symbol_c, char* timeframe_c, long long from_time, long long to_time)
{
    exchange = exchange_c;
    symbol = symbol_c;
    timeframe = timeframe_c;


    Database db(exchange);
    int array_size = 0;
    double** res = db.get_data(symbol, exchange, array_size);
    db.close_file();

    // Convert the result to tuple of vectors.
    std::tie(ts, open, high, low, close, volume) = rearrange_candles(res, timeframe, from_time, to_time, array_size);
}

void Obv::execute_backtest()
{
    pnl = 0.0;
    max_dd = 0.0;

    double max_pnl = 0.0;
    int current_position = 0;
    double entry_price;

    vector<double> obv_closes = {};

    for (int i = 0; i < ts.size(); i++)
    {
        obv_closes.push_back(close[i]);

        if (obv_closes.size() > 10) {
            obv_closes.erase(obv_closes.begin());
        }

        if (obv_closes.size() < 10) {
            continue;
        }

        double sum = accumulate(obv_closes.begin(), obv_closes.end(), 0.0);
        double mean = sum / 10;

        // Long Signal

        if (close[i] > mean && current_position <= 0) {

            if (current_position == -1) {
                double pnl_temp = (entry_price / close[i] - 1) * 100;
                pnl += pnl_temp;
                max_pnl = max(max_pnl, pnl);
                max_dd = max(max_dd, max_pnl - pnl);
            }

            current_position = 1;
            entry_price = close[i];
        }

        // Short Signal

        if (close[i] < mean && current_position >= 0) {

            if (current_position == 1) {
                double pnl_temp = (close[i] / entry_price - 1) * 100;
                pnl += pnl_temp;
                max_pnl = max(max_pnl, pnl);
                max_dd = max(max_dd, max_pnl - pnl);
            }

            current_position = -1;
            entry_price = close[i];
        }

    }
}