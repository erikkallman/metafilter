# MIT License
# Copyright (c) 2024 Erik Källman
# See the LICENSE file for more details.

import json
import xarray as xr
import numpy as np
from utils.config import OUTPUT_DIR

def load_metafilter_parameters(json_file):
    """
    Load metafilter parameters from a JSON file.
    """
    with open(json_file, 'r') as file:
        return json.load(file)

def process_era5_data(file_path, metafilter_params):
    """
    Process ERA5 data using parameters from the metafilter.
    """
    ds = xr.open_dataset(file_path)
    ds = ds.rename({'valid_time': 'time'})

    # Convert temperature from Kelvin to Celsius
    ds['t2m'] = ds['t2m'] - 273.15

    # Compute daily mean temperature and total precipitation
    daily_mean_temp = ds['t2m'].resample(time='1D').mean()
    daily_total_precip = ds['tp'].resample(time='1D').sum()

    # Apply metafilter thresholds
    temp_threshold = metafilter_params["temperature"]["threshold"]
    precip_threshold = metafilter_params["precipitation"]["threshold"]

    selected_days = (daily_mean_temp > temp_threshold) & (daily_total_precip < precip_threshold)
    return selected_days.time.values[np.where(selected_days.values)[0]]

if __name__ == "__main__":
    # Load metafilter parameters from JSON
    metafilter_file = "filters/metafilter.json"
    metafilter_params = load_metafilter_parameters(metafilter_file)

    # Process ERA5 data
    file_path = f"{OUTPUT_DIR}/era5/era5_land_july_2023.nc"
    selected_dates = process_era5_data(file_path, metafilter_params)

    print("Selected dates:", selected_dates)
