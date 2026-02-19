# Metafilter

## Overview

This provides a pipeline to process ERA5-Land meteorological data, retrieve relevant Sentinel-2 satellite imagery metadata through an openEO backend (Digital Earth Sweden by default), and visualize the results on an interactive map. The project aims to identify satellite imagery for specific weather conditions over a specified area of interest and render the footprints of these products geographically.

Essentially it is a demonstration of how metereological metadata can be used to filter satellite data series where optimal weather conditions might yield dataseries of, for instance, Sentinel 2 L2A data of good quality with respect to cloud cover, etc.

The work was co-developed with partners in the Space Data Lab 3.0 project.

---

## Features

1. **Download ERA5-Land Data**:
   - Uses the CDSAPI to fetch ERA5-Land weather data for a specified time period and area.

2. **Process ERA5 Data**:
   - Extracts dates that meet specific weather criteria (e.g., temperature thresholds and precipitation levels). This uses a predefined filter in JSON format (see filters/metafilter.json).

3. **Authenticate and Query Sentinel-2 Data**:
   - Retrieves Sentinel-2 data for the selected dates and area of interest using openEO (`load_collection` + `download`).
   - The default backend configured in this repo is Digital Earth Sweden (`https://openeo.digitalearth.se`).

4. **Visualize Sentinel-2 Footprints**:
   - Renders the footprints of the retrieved Sentinel-2 products on an interactive Folium map.

---

## Supported Data Fetching Modes

This repository currently supports two external data-fetching modes:

1. **ERA5-Land meteorology via CDS API**
   - Script: `scripts/download_era5.py`
   - Backend/service: Copernicus Climate Data Store (`cdsapi.Client().retrieve(...)`)
   - Purpose: Download weather variables used for filtering dates.

2. **Sentinel-2 imagery via openEO backend**
   - Script: `scripts/search_sentinel.py`
   - Backend/service: openEO backend URL configured in `utils/config.py` (`eo_service_url`)
   - Default backend in this repo: Digital Earth Sweden (`https://openeo.digitalearth.se`)
   - Purpose: Query/download Sentinel-2 (`s2_msi_l2a`) for filtered temporal and spatial extents.

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
     - `AREA`: The geographical bounding box of the area of interest (northern half of Sweden by default).
     - `eo_service_url`: openEO backend URL (default: `https://openeo.digitalearth.se`).
     - `username` / `password`: Credentials for the selected openEO backend.
   - For ERA5 download (`scripts/download_era5.py`), configure CDS API access for your Copernicus Climate Data Store account.

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

3. **Authenticate and Query Sentinel-2 Data**:
   - Connects to the configured openEO backend (Digital Earth Sweden by default) to fetch Sentinel-2 data for the filtered dates.

4. **Visualize Sentinel-2 Footprints**:
   - Generates an interactive map (`metafilter_results_map.html`) displaying the footprints of the retrieved Sentinel-2 products.

---

## Output

- **Console Output**:
  - Prints metadata for the retrieved Sentinel-2 products, including IDs, names, and timestamps.

- **Generated Map**:
  - Outputs an interactive map file: `metafilter_results_map.html`.
  - Open the file in a browser to view the Sentinel-2 footprints over the area of interest.

---

## Directory Structure

```plaintext
.
├── README.md                  # Project overview (this file)
├── license.txt                # APACHE 2.0 license and copyright notice
├── data/                      # Stores ERA5 and Sentinel data
│   ├── era5/                  # ERA5-Land weather data
│   └── sentinel/              # Placeholder for Sentinel imagery (if downloaded)
├── main.py                    # Main entry point for the project
├── requirements.txt           # Required Python dependencies
├── scripts/                   # Core functionality scripts
│   ├── download_era5.py       # Downloads ERA5-Land data
│   ├── process_era5.py        # Processes ERA5 data to filter dates
│   ├── search_sentinel.py     # Queries/downloads Sentinel-2 data via openEO
│   └── visualize.py           # Generates interactive maps
├── filters/                   # Stores JSON filters used in the processing
│   └── metafilter.json        # An example metadata filter JSON
└── utils/                     # Utility scripts and configurations
    └── config.py              # Configuration file for API credentials and settings
```

---

## Notes

- Sentinel-2 retrieval uses openEO credentials configured in `utils/config.py` and the configured `eo_service_url` (Digital Earth Sweden by default).
- ERA5-Land download requires a registered account with the [Copernicus Climate Data Store](https://cds.climate.copernicus.eu/) and CDS API setup.

For questions or issues, feel free to open an issue in the repository.

## Licensing and Copyright

All material in this repository follows the copyright and licensing as detailed in license.txt in the root directory of the repository.
