# MIT License
# Copyright (c) 2024 Erik Källman
# See the LICENSE file for more details.

from scripts.download_era5 import download_era5_land
from scripts.process_era5 import process_era5_data, load_metafilter_parameters
from scripts.search_sentinel import authenticate, search_sentinel_data
from scripts.visualize import visualize_sentinel_results
from utils.config import DATASPACE_USERNAME, DATASPACE_PASSWORD, AREA

def main():
    # Step 1: Download ERA5-Land data
    # Uncomment the line below if you want to download the ERA5-Land data
    download_era5_land()

    # Load metafilter parameters from JSON
    metafilter_file = "filters/metafilter.json"
    metafilter_params = load_metafilter_parameters(metafilter_file)

    # Step 2: Process ERA5 data to filter dates
    era5_file = "data/era5/era5_land_july_2023.nc"
    selected_dates = process_era5_data(era5_file, metafilter_params)
    print("Selected dates:", selected_dates)

    # Step 3: Authenticate with the Copernicus Data Space Ecosystem
    token = authenticate(DATASPACE_USERNAME, DATASPACE_PASSWORD)

    # Step 4: Search Sentinel-2 data for filtered dates
    products = search_sentinel_data(selected_dates, token)
    if not products:
        print("No products found for the given criteria.")
        return

    print("Found the following Sentinel-2 L2A products:")
    # Step 5: Print the results
    for product in products:
        print(f"ID: {product['Id']}, Name: {product['Name']}, "
              f"Start Date: {product['ContentDate']['Start']}, End Date: {product['ContentDate']['End']}")

    # Step 6: Visualize the results
    visualize_sentinel_results(products)

if __name__ == "__main__":
    main()
