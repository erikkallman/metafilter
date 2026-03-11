from pathlib import Path

from scripts.compare_ndvi import (
    authenticate,
    compare_ndvi_strategies,
    create_ndvi_comparison_plot,
)
from scripts.process_era5 import (
    load_metafilter_parameters,
    process_era5_data,
    save_daily_metrics,
)
from utils.config import NDVI_OUTPUT_DIR, eo_service_url, password, username


def main():
    metafilter_params = load_metafilter_parameters("filters/metafilter.json")
    era5_results = process_era5_data(
        "data/era5/era5_land_july_2023.nc",
        metafilter_params,
    )

    output_dir = Path(NDVI_OUTPUT_DIR)
    daily_metrics_path = output_dir / "era5_daily_metrics.csv"
    save_daily_metrics(era5_results["daily_metrics"], daily_metrics_path)

    connection = authenticate(username, password, eo_service_url)
    comparison_summary, comparison_results = compare_ndvi_strategies(
        connection=connection,
        all_dates=era5_results["all_dates"],
        selected_dates=era5_results["selected_dates"],
        output_dir=output_dir,
    )

    plot_path = create_ndvi_comparison_plot(
        comparison_results,
        output_path=output_dir / "ndvi_comparison_plot.png",
        ndvi_threshold=comparison_summary["ndvi_threshold"],
    )

    print(
        "Generated NDVI comparison plot:",
        plot_path,
    )


if __name__ == "__main__":
    main()
