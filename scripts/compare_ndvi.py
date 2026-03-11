import json
from datetime import date, timedelta
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import rasterio

from utils.config import AREA, NDVI_OUTPUT_DIR


def print_info(message):
    print(f"INFO {message}")


def _get_openeo_connect():
    try:
        from openeo import connect
    except ImportError as exc:
        raise RuntimeError(
            "The openeo package is required for NDVI comparison runs. "
            "Install dependencies from requirements.txt in the intended environment."
        ) from exc

    return connect


def authenticate(username, password, eo_service_url):
    print_info(f"Connecting to openEO backend: {eo_service_url}")
    connect = _get_openeo_connect()
    connection = connect(eo_service_url)
    print_info("Authenticating with basic auth")
    connection.authenticate_basic(username=username, password=password)
    print_info("openEO authentication complete")
    return connection


def to_day_window(day_string):
    current_day = date.fromisoformat(day_string)
    next_day = current_day + timedelta(days=1)
    return [current_day.isoformat(), next_day.isoformat()]


def build_ndvi_cube(connection, temporal_extent, spatial_extent=AREA):
    data_cube = connection.load_collection(
        collection_id="s2_msi_l2a",
        spatial_extent=spatial_extent,
        temporal_extent=temporal_extent,
        bands=["b04", "b08"],
    )

    try:
        return data_cube.ndvi(red="b04", nir="b08")
    except TypeError:
        return data_cube.ndvi(nir="b08", red="b04")


def download_ndvi_raster(connection, day_string, output_path, spatial_extent=AREA):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if output_path.exists():
        return output_path

    ndvi_cube = build_ndvi_cube(
        connection,
        temporal_extent=to_day_window(day_string),
        spatial_extent=spatial_extent,
    )

    try:
        ndvi_cube.download(str(output_path), format="GTiff")
    except TypeError:
        ndvi_cube.download(outputfile=str(output_path), format="GTiff")

    return output_path


def summarize_ndvi_raster(raster_path):
    with rasterio.open(raster_path) as dataset:
        data = dataset.read(masked=True).astype("float32")
        if data.count() == 0:
            raise ValueError(f"No valid NDVI pixels found in {raster_path}.")

        flattened = data.compressed()
        band_means = [
            round(float(np.ma.mean(data[index])), 4)
            for index in range(dataset.count)
        ]

        return {
            "band_count": int(dataset.count),
            "valid_pixel_count": int(flattened.size),
            "mean_ndvi": round(float(flattened.mean()), 4),
            "median_ndvi": round(float(np.median(flattened)), 4),
            "p90_ndvi": round(float(np.percentile(flattened, 90)), 4),
            "max_ndvi": round(float(flattened.max()), 4),
            "band_means": json.dumps(band_means),
        }


def format_progress(current, total, width=20):
    if total <= 0:
        return "[--------------------]"

    filled = int(width * current / total)
    if current > 0 and filled == 0:
        filled = 1
    return f"[{'#' * filled}{'-' * (width - filled)}]"


def run_strategy(connection, strategy_name, day_strings, output_dir=NDVI_OUTPUT_DIR):
    results = []
    strategy_dir = Path(output_dir) / strategy_name
    total_days = len(day_strings)

    print_info(
        f"Starting strategy '{strategy_name}' for {total_days} day(s) into {strategy_dir}"
    )

    for index, day_string in enumerate(day_strings, start=1):
        raster_path = strategy_dir / f"{day_string}.tif"
        cached = raster_path.exists()
        progress = format_progress(index, total_days)
        record = {
            "strategy": strategy_name,
            "date": day_string,
            "raster_path": str(raster_path),
            "status": "pending",
        }

        try:
            source_label = "cached" if cached else "download"
            print_info(
                f"{strategy_name} {progress} {index}/{total_days} {day_string} {source_label}"
            )
            download_ndvi_raster(connection, day_string, raster_path)
            record.update(summarize_ndvi_raster(raster_path))
            record["status"] = "ok"
            print_info(
                f"{strategy_name} {day_string} mean_ndvi={record['mean_ndvi']}"
            )
        except Exception as exc:
            record["status"] = "error"
            record["error"] = str(exc)
            print_info(f"{strategy_name} {day_string} error: {exc}")

        results.append(record)

    print_info(f"Completed strategy '{strategy_name}'")
    return pd.DataFrame(results)


def summarize_strategy(results_df, ndvi_threshold):
    successful = results_df[results_df["status"] == "ok"].copy()
    summary = {
        "candidate_days": int(len(results_df)),
        "successful_days": int(len(successful)),
        "error_days": int((results_df["status"] == "error").sum()),
        "mean_of_mean_ndvi": None,
        "median_of_mean_ndvi": None,
        "share_above_threshold": None,
        "best_day": None,
        "best_day_mean_ndvi": None,
    }

    if successful.empty:
        return summary

    summary["mean_of_mean_ndvi"] = round(float(successful["mean_ndvi"].mean()), 4)
    summary["median_of_mean_ndvi"] = round(float(successful["mean_ndvi"].median()), 4)
    summary["share_above_threshold"] = round(
        float((successful["mean_ndvi"] >= ndvi_threshold).mean()),
        4,
    )

    best_row = successful.sort_values("mean_ndvi", ascending=False).iloc[0]
    summary["best_day"] = best_row["date"]
    summary["best_day_mean_ndvi"] = round(float(best_row["mean_ndvi"]), 4)
    return summary


def compare_ndvi_strategies(
    connection,
    all_dates,
    selected_dates,
    output_dir=NDVI_OUTPUT_DIR,
    ndvi_threshold=0.6,
):
    print_info(
        f"Preparing NDVI comparison: baseline={len(all_dates)} day(s), "
        f"metafilter={len(selected_dates)} day(s)"
    )
    baseline_results = run_strategy(
        connection,
        strategy_name="baseline_all_days",
        day_strings=all_dates,
        output_dir=output_dir,
    )
    metafilter_results = run_strategy(
        connection,
        strategy_name="metafilter_selected_days",
        day_strings=selected_dates,
        output_dir=output_dir,
    )

    all_results = pd.concat([baseline_results, metafilter_results], ignore_index=True)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    results_csv_path = output_dir / "ndvi_comparison_results.csv"
    all_results.to_csv(results_csv_path, index=False)

    baseline_summary = summarize_strategy(baseline_results, ndvi_threshold=ndvi_threshold)
    metafilter_summary = summarize_strategy(metafilter_results, ndvi_threshold=ndvi_threshold)

    comparison_summary = {
        "ndvi_threshold": ndvi_threshold,
        "baseline_all_days": baseline_summary,
        "metafilter_selected_days": metafilter_summary,
        "candidate_day_reduction": round(
            1 - (len(selected_dates) / len(all_dates)),
            4,
        ),
        "mean_ndvi_delta": (
            round(
                metafilter_summary["mean_of_mean_ndvi"]
                - baseline_summary["mean_of_mean_ndvi"],
                4,
            )
            if baseline_summary["mean_of_mean_ndvi"] is not None
            and metafilter_summary["mean_of_mean_ndvi"] is not None
            else None
        ),
        "share_above_threshold_delta": (
            round(
                metafilter_summary["share_above_threshold"]
                - baseline_summary["share_above_threshold"],
                4,
            )
            if baseline_summary["share_above_threshold"] is not None
            and metafilter_summary["share_above_threshold"] is not None
            else None
        ),
        "results_csv": str(results_csv_path),
    }

    summary_json_path = output_dir / "ndvi_comparison_summary.json"
    with open(summary_json_path, "w") as file:
        json.dump(comparison_summary, file, indent=2)

    print_info(f"Wrote NDVI comparison table: {results_csv_path}")
    print_info(f"Wrote NDVI comparison summary: {summary_json_path}")
    comparison_summary["summary_json"] = str(summary_json_path)
    return comparison_summary, all_results


def create_ndvi_comparison_plot(results_df, output_path, ndvi_threshold=0.6):
    successful = results_df[results_df["status"] == "ok"].copy()
    if successful.empty:
        raise ValueError("No successful NDVI results were available to plot.")

    successful["date"] = pd.to_datetime(successful["date"])
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    baseline = successful[successful["strategy"] == "baseline_all_days"].sort_values("date")
    metafilter = successful[successful["strategy"] == "metafilter_selected_days"].sort_values("date")

    figure, axis = plt.subplots(figsize=(12, 6))

    if not baseline.empty:
        axis.plot(
            baseline["date"],
            baseline["mean_ndvi"],
            color="#9AA0A6",
            linewidth=1.5,
            marker="o",
            markersize=4,
            label="All days",
        )
        axis.axhline(
            baseline["mean_ndvi"].mean(),
            color="#9AA0A6",
            linestyle="--",
            linewidth=1,
            alpha=0.7,
        )

    if not metafilter.empty:
        axis.plot(
            metafilter["date"],
            metafilter["mean_ndvi"],
            color="#2E7D32",
            linewidth=2,
            marker="o",
            markersize=6,
            label="Metafilter-selected days",
        )
        axis.axhline(
            metafilter["mean_ndvi"].mean(),
            color="#2E7D32",
            linestyle="--",
            linewidth=1,
            alpha=0.7,
        )

    axis.axhline(
        ndvi_threshold,
        color="#B3261E",
        linestyle=":",
        linewidth=1.5,
        label=f"High NDVI threshold ({ndvi_threshold})",
    )
    axis.set_title("NDVI Comparison: All Days vs Metafilter-Selected Days")
    axis.set_xlabel("Acquisition day")
    axis.set_ylabel("Mean NDVI")
    axis.grid(alpha=0.25)
    axis.legend()
    figure.autofmt_xdate()
    figure.tight_layout()
    figure.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(figure)

    print_info(f"Wrote NDVI comparison plot: {output_path}")
    return output_path
