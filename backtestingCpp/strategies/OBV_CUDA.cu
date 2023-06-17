#include <thrust/device_vector.h>
#include <thrust/transform_reduce.h>
#include <thrust/count.h>
#include <thrust/scan.h>
#include <thrust/functional.h>

// Define a functor to calculate the mean
struct MeanFunctor
{
    const int window_size;

    MeanFunctor(int size) : window_size(size) {}

    __host__ __device__
    double operator()(const double& x) const
    {
        return x / window_size;
    }
};

void Obv::execute_backtest()
{
    pnl = 0.0;
    max_dd = 0.0;

    double max_pnl = 0.0;
    int current_position = 0;
    double entry_price;

    thrust::device_vector<double> obv_closes(close.begin(), close.end());

    // Create a temporary vector to store the mean values
    thrust::device_vector<double> mean_values(obv_closes.size());

    // Calculate the mean values using transform_reduce
    thrust::transform_reduce(obv_closes.begin(), obv_closes.end(), mean_values.begin(), MeanFunctor(10),0.0, thrust::plus<double>());

    // Create a temporary vector to store the cumulative sum
    thrust::device_vector<double> cumulative_sum(obv_closes.size());

    // Calculate the cumulative sum using inclusive_scan
    thrust::inclusive_scan(obv_closes.begin(), obv_closes.end(), cumulative_sum.begin());

    for (int i = 0; i < obv_closes.size(); i++)
    {
        if (obv_closes.size() > 10) {
            obv_closes.erase(obv_closes.begin());
        }

        if (obv_closes.size() < 10) {
            continue;
        }

        double mean = mean_values[i];

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