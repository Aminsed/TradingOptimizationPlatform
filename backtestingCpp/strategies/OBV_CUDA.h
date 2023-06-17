#ifndef OBV_H
#define OBV_H

#include <vector>

class Obv
{
public:
    Obv(char* exchange_c, char* symbol_c, char* timeframe_c, long long from_time, long long to_time);
    void execute_backtest();

private:
    double pnl;
    double max_dd;
    std::vector<double> ts;
    std::vector<double> open;
    std::vector<double> high;
    std::vector<double> low;
    std::vector<double> close;
    std::vector<double> volume;

    // Add any other necessary member variables and functions

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
};

#endif