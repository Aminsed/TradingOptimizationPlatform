#include "Database.h"

#include <chrono>
#include <cstdlib>

using namespace std;

Database::Database(const string& file_name)
{
    string FILE_NAME = "../../data/" + file_name + ".h5";
    hid_t fapl = H5Pcreate(H5P_FILE_ACCESS);

    herr_t status = H5Pset_libver_bounds(fapl, H5F_LIBVER_LATEST, H5F_LIBVER_LATEST);
    status = H5Pset_fclose_degree(fapl, H5F_CLOSE_STRONG);

    printf("Opening file: %s\n", FILE_NAME.c_str());
    h5_file = H5Fopen(FILE_NAME.c_str(), H5F_ACC_RDONLY, fapl);

    if (h5_file < 0) { 
        // In case the db wasn't found we assume the the db file
        // is located in parent Python directory.
        FILE_NAME = "data/" + file_name + ".h5";
        h5_file = H5Fopen(FILE_NAME.c_str(), H5F_ACC_RDONLY, fapl);
        if (h5_file < 0) {
            printf("Error opening file: %s\n", FILE_NAME.c_str());
        }
        else {
            printf("Database file loacted at %s directory used\n", FILE_NAME.c_str());
        }
    }
}

void Database::close_file()
{
    H5Fclose(h5_file);
    printf("Closed file\n");
}

double** Database::get_data(const string& symbol, const string& exchange, int& array_size)
{
    double** results = {};

    hid_t dataset = H5Dopen2(h5_file, symbol.c_str(), H5P_DEFAULT);

    if (dataset == -1) {
        return results;
    }

    auto start_ts = std::chrono::high_resolution_clock::now();

    hid_t dspace = H5Dget_space(dataset);
    hsize_t dims[2];

    H5Sget_simple_extent_dims(dspace, dims, NULL);

    array_size = (int)dims[0];

    results = new double*[dims[0]];

    for (size_t i = 0; i < dims[0]; ++i)
    {
        results[i] = new double[dims[1]];
    }

    // H5Dread function reads the dataset file in a 1D array so we decalre 
    // a 1D array named candles_arr to store the data.
    double* candles_arr = new double[dims[0] * dims[1]];

    H5Dread(dataset, H5T_NATIVE_DOUBLE, H5S_ALL, H5S_ALL, H5P_DEFAULT, candles_arr);

    // Sicne we have 5 columns we loop over our 1D array by strides of 6
    // and append them to the results 2D array.
    int j = 0;
    for (int i = 0; i < dims[0] * dims[1]; i += 6)
    {
        results[j][0] = candles_arr[i]; // timestamp
        results[j][1] = candles_arr[i + 1]; // open
        results[j][2] = candles_arr[i + 2]; // high
        results[j][3] = candles_arr[i + 3]; // low
        results[j][4] = candles_arr[i + 4]; // close
        results[j][5] = candles_arr[i + 5]; // volume

        j++; // index of the "results" 2D array
    }
    // getting rid of the 1D array
    delete[] candles_arr;

    qsort(results, dims[0], sizeof(results[0]), compare);

    H5Sclose(dspace);
    H5Dclose(dataset);

    auto end_ts = chrono::high_resolution_clock::now();
    auto read_duration = chrono::duration_cast<chrono::milliseconds> (end_ts - start_ts);

    printf("Fetched %i %s %s data in %i ms\n", (int)dims[0], exchange.c_str(), symbol.c_str(), (int)read_duration.count());

    return results;

}

// Creating a comparisoon function for the qsort function from cstdlib library
// to sort the 1D array that is being read from database based on timestamp value.
int compare(const void* pa, const void* pb)
{
    const double* a = *(const double**)pa;
    const double* b = *(const double**)pb;
    //[0] is location of timestamp column
    if (a[0] == b[0]) {
        return 0;
    }
    else if (a[0] < b[0]) {
        return -1;
    }
    else {
        return 1;
    }
}