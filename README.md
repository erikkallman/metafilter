# Sentinel Data Visualization Project

## Overview

This project provides a pipeline to process ERA5-Land meteorological data, retrieve relevant Sentinel-2 satellite imagery metadata from the Copernicus Data Space Ecosystem, and visualize the results on an interactive map. The project aims to identify satellite imagery for specific weather conditions over a specified area of interest and render the footprints of these products geographically.

---

## Features

1. **Download ERA5-Land Data**:
   - Uses the CDSAPI to fetch ERA5-Land weather data for a specified time period and area.

2. **Process ERA5 Data**:
   - Extracts dates that meet specific weather criteria (e.g., temperature thresholds and precipitation levels).

3. **Authenticate and Query Sentinel-2 Metadata**:
   - Retrieves Sentinel-2 metadata for the selected dates and area of interest using the Copernicus Data Space Ecosystem's OData API.

4. **Visualize Sentinel-2 Footprints**:
   - Renders the footprints of the retrieved Sentinel-2 products on an interactive Folium map.

---

## Installation and Setup

1. **Install Conda or Python Virtual Environment Manager**:
   - [Miniconda](https://docs.conda.io/en/latest/miniconda.html) or [Virtualenv](https://virtualenv.pypa.io/en/latest/).

2. **Set up the environment**:
   ```bash
   # Clone the repository
   git clone https://github.com/your-username/metafilter.git
   cd metafilter

   # Create and activate a virtual environment
   conda create -n metafilter-env python=3.12 -y
   conda activate metafilter-env

   # Install required Python packages
   pip install -r requirements.txt
   ```

3. **Configure Your Environment**:
   - Update the following values in `utils/config.py`:
     - `DATASPACE_USERNAME`: Your Copernicus Data Space Ecosystem username.
     - `DATASPACE_PASSWORD`: Your Copernicus Data Space Ecosystem password.
     - `AREA`: The geographical bounding box of the area of interest (northern half of Sweden by default).

---

## Usage

Run the project using the main script:

```bash
python main.py
```

### Workflow Steps

1. **Download ERA5-Land Data**:
   - Uncomment the `download_era5_land()` function in `main.py` to download data for the specified time period.

2. **Process ERA5 Data**:
   - Automatically filters ERA5-Land data to identify dates matching specified weather conditions.

3. **Authenticate and Query Sentinel-2 Metadata**:
   - Connects to the Copernicus Data Space Ecosystem to fetch Sentinel-2 metadata for the filtered dates.

4. **Visualize Sentinel-2 Footprints**:
   - Generates an interactive map (`sentinel_results_map.html`) displaying the footprints of the retrieved Sentinel-2 products.

---

## Output

- **Console Output**:
  - Prints metadata for the retrieved Sentinel-2 products, including IDs, names, and timestamps.

- **Generated Map**:
  - Outputs an interactive map file: `sentinel_results_map.html`.
  - Open the file in a browser to view the Sentinel-2 footprints over the area of interest.

---

## Directory Structure

```plaintext
.
├── README.md                  # Project overview (this file)
├── data/                      # Stores ERA5 and Sentinel data
│   ├── era5/                  # ERA5-Land weather data
│   └── sentinel/              # Placeholder for Sentinel imagery (if downloaded)
├── main.py                    # Main entry point for the project
├── notebooks/                 # Optional Jupyter notebooks for experimentation
├── requirements.txt           # Required Python dependencies
├── scripts/                   # Core functionality scripts
│   ├── download_era5.py       # Downloads ERA5-Land data
│   ├── process_era5.py        # Processes ERA5 data to filter dates
│   ├── search_sentinel.py     # Queries Sentinel-2 metadata
│   └── visualize.py           # Generates interactive maps
└── utils/                     # Utility scripts and configurations
    ├── config.py              # Configuration file for API credentials and settings
    └── geo_utils.py           # Placeholder for additional geospatial utilities
```

---

## Notes

- Ensure you have valid Copernicus Data Space Ecosystem credentials to query Sentinel-2 metadata.
- ERA5-Land data download requires a registered account with the [Copernicus Climate Data Store](https://cds.climate.copernicus.eu/).

For questions or issues, feel free to open an issue in the repository.

## License

This project is licensed under the [MIT License](LICENSE).
