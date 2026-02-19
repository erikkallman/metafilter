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
    Process ERA5 data using parameters from the metafilter and return
    temporal_extent for use in OpenEO's load_collection.
    """
    ds = xr.open_dataset(file_path)
    ds = ds.rename({'valid_time': 'time'})

    # Convert temperature from Kelvin to Celsius
    ds['t2m'] = ds['t2m'] - 273.15

    # Compute daily mean temperature and total precipitation
    daily_mean_temp = ds['t2m'].resample(time='1D').mean()
    daily_total_precip = ds['tp'].resample(time='1D').sum()

    # Apply metafilter thresholds and extract selected dates
    temp_threshold = metafilter_params["temperature"]["threshold"]
    precip_threshold = metafilter_params["precipitation"]["threshold"]

    selected_dates = (daily_mean_temp > temp_threshold) & (daily_total_precip < precip_threshold)
    selected_dates = daily_mean_temp.time.values[np.where(selected_dates.values)[0]]

    # Get start and end dates in "YYYY-MM-DD" format
    return [str(selected_dates[0])[:10], str(selected_dates[-1])[:10]]

if __name__ == "__main__":
    # Load metafilter parameters from JSON
    metafilter_file = "filters/metafilter.json"
    metafilter_params = load_metafilter_parameters(metafilter_file)

    # Process ERA5 data
    file_path = f"{OUTPUT_DIR}/era5/era5_land_july_2023.nc"
    selected_dates = process_era5_data(file_path, metafilter_params)

    print("Selected dates:", selected_dates)
