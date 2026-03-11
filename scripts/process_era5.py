import json
from pathlib import Path

import pandas as pd
import xarray as xr

from utils.config import AREA


def load_metafilter_parameters(json_file):
    with open(json_file, "r") as file:
        return json.load(file)


def subset_dataset_to_area(dataset, area):
    latitude = dataset["latitude"]
    longitude = dataset["longitude"]

    if latitude[0] > latitude[-1]:
        latitude_slice = slice(area["north"], area["south"])
    else:
        latitude_slice = slice(area["south"], area["north"])

    if longitude[0] > longitude[-1]:
        longitude_slice = slice(area["east"], area["west"])
    else:
        longitude_slice = slice(area["west"], area["east"])

    return dataset.sel(latitude=latitude_slice, longitude=longitude_slice)


def calculate_daily_metrics(file_path, area=AREA):
    dataset = xr.open_dataset(file_path)
    if "valid_time" in dataset.coords or "valid_time" in dataset.dims:
        dataset = dataset.rename({"valid_time": "time"})

    dataset = subset_dataset_to_area(dataset, area)
    if dataset.sizes.get("latitude", 0) == 0 or dataset.sizes.get("longitude", 0) == 0:
        raise ValueError("Configured AREA does not overlap the ERA5 dataset.")

    temperature_c = dataset["t2m"] - 273.15
    precipitation_mm = dataset["tp"] * 1000.0

    spatial_dims = tuple(
        dimension
        for dimension in ("latitude", "longitude")
        if dimension in temperature_c.dims
    )

    daily_mean_temp = temperature_c.resample(time="1D").mean()
    daily_total_precip = precipitation_mm.resample(time="1D").sum()

    if spatial_dims:
        daily_mean_temp = daily_mean_temp.mean(dim=spatial_dims, skipna=True)
        daily_total_precip = daily_total_precip.mean(dim=spatial_dims, skipna=True)

    metrics = pd.DataFrame(
        {
            "date": pd.to_datetime(daily_mean_temp["time"].values).strftime("%Y-%m-%d"),
            "mean_temp_c": daily_mean_temp.values,
            "total_precip_mm": daily_total_precip.values,
        }
    )
    return metrics


def apply_metafilter(daily_metrics, metafilter_params):
    temp_threshold = metafilter_params["temperature"]["threshold"]
    precip_threshold = metafilter_params["precipitation"]["threshold"]

    filtered_metrics = daily_metrics.copy()
    filtered_metrics["selected"] = (
        (filtered_metrics["mean_temp_c"] > temp_threshold)
        & (filtered_metrics["total_precip_mm"] < precip_threshold)
    )
    return filtered_metrics


def process_era5_data(file_path, metafilter_params, area=AREA):
    daily_metrics = calculate_daily_metrics(file_path, area=area)
    filtered_metrics = apply_metafilter(daily_metrics, metafilter_params)

    all_dates = filtered_metrics["date"].tolist()
    selected_dates = filtered_metrics.loc[filtered_metrics["selected"], "date"].tolist()
    if not selected_dates:
        raise ValueError("No dates matched the configured metafilter thresholds.")

    return {
        "all_dates": all_dates,
        "selected_dates": selected_dates,
        "full_temporal_extent": [all_dates[0], all_dates[-1]],
        "selected_temporal_extent": [selected_dates[0], selected_dates[-1]],
        "daily_metrics": filtered_metrics,
    }


def save_daily_metrics(daily_metrics, output_path):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    daily_metrics.to_csv(output_path, index=False)


if __name__ == "__main__":
    metafilter_file = "filters/metafilter.json"
    metafilter_params = load_metafilter_parameters(metafilter_file)
    results = process_era5_data("data/era5/era5_land_july_2023.nc", metafilter_params)
    print(results["selected_dates"])
