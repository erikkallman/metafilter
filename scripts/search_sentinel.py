# MIT License
# Copyright (c) 2024 Erik Källman
# See the LICENSE file for more details.

import requests
from urllib.parse import quote
from datetime import datetime
from openeo import connect
from utils.config import DATASPACE_USERNAME, DATASPACE_PASSWORD, AREA

# Authentication endpoint and API base URL
AUTH_URL = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
API_BASE_URL = "https://catalogue.dataspace.copernicus.eu/odata/v1"

def format_dates(date):
    """
    Format dates to the correct ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ).
    """
    return datetime.fromisoformat(str(date)).strftime('%Y-%m-%dT%H:%M:%SZ')

def authenticate(username, password, eo_service_url):
    # Connect to OpenEO backend
    connection = connect(eo_service_url)

    # Authenticate using basic authentication
    connection.authenticate_basic(username=username, password=password)
    return connection

def search_sentinel_data(selected_dates, connection):

    """
    Search for Sentinel-2 L2A products using openEO.
    """

    data_cube = connection.load_collection(
        collection_id="s2_msi_l2a",
        spatial_extent=AREA,
        temporal_extent=selected_dates,
        bands=["b08", "b02",  "b04"]
    )

    products = data_cube.download(format="gtiff")
    return products

if __name__ == "__main__":
    # Example dates and area from config
    selected_dates = ["2023-07-01", "2023-07-13"]

    # Authenticate and search for products
    token = authenticate(DATASPACE_USERNAME, DATASPACE_PASSWORD)
    products = search_sentinel_data(selected_dates, token)
    print("Found the following Sentinel-2 L2A products:")
    # Print the results
    for product in products:
        print(f"ID: {product['Id']}, Name: {product['Name']}, Start Date: {product['ContentDate']['Start']}, End Date: {product['ContentDate']['End']}")
