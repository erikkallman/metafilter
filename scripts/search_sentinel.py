# MIT License
# Copyright (c) 2024 Erik Källman
# See the LICENSE file for more details.

import requests
from urllib.parse import quote
from datetime import datetime
from utils.config import DATASPACE_USERNAME, DATASPACE_PASSWORD, AREA

# Authentication endpoint and API base URL
AUTH_URL = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
API_BASE_URL = "https://catalogue.dataspace.copernicus.eu/odata/v1"

def format_dates(date):
    """
    Format dates to the correct ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ).
    """
    return datetime.fromisoformat(str(date)).strftime('%Y-%m-%dT%H:%M:%SZ')

def authenticate(username, password):
    """
    Authenticate with the Copernicus Data Space Ecosystem and return an access token.
    """
    response = requests.post(
        AUTH_URL,
        data={
            'client_id': 'cdse-public',
            'username': username,
            'password': password,
            'grant_type': 'password'
        }
    )
    response.raise_for_status()
    return response.json()["access_token"]

def build_query(selected_dates, area):
    """
    Build the OData query URL for Sentinel-2 L2A products.
    """
    # Format dates
    start_date = format_dates(selected_dates[0])
    end_date = format_dates(selected_dates[-1])

    # Construct the polygon WKT
    polygon_wkt = (
        f"POLYGON(({area[1]} {area[2]}, "
        f"{area[3]} {area[2]}, "
        f"{area[3]} {area[0]}, "
        f"{area[1]} {area[0]}, "
        f"{area[1]} {area[2]}))"
    )

    # Do not encode SRID=4326
    encoded_polygon = f"SRID=4326;{polygon_wkt}"

    # Build the query using OData.CSC.Intersects
    query = (
        f"{API_BASE_URL}/Products?$filter="
        f"startswith(Name,'S2') and "
        f"ContentDate/Start ge {start_date} and "
        f"ContentDate/End le {end_date} and "
        f"Online eq true and "
        f"OData.CSC.Intersects(area=geography'{encoded_polygon}')"
    )

    return query

def search_sentinel_data(selected_dates, token):
    """
    Search for Sentinel-2 L2A products using the Copernicus Data Space Ecosystem API.
    """
    headers = {
        "Authorization": f"Bearer {token}"
    }

    # Build the query
    query = build_query(selected_dates, AREA)

    # Make the request
    try:
        response = requests.get(query, headers=headers)
        response.raise_for_status()
        products = response.json().get("value", [])
        return products
    except requests.exceptions.HTTPError as e:
        print("HTTPError occurred:")
        print(f"Status Code: {response.status_code}")
        print(f"Response URL: {response.url}")
        print(f"Response Content: {response.text}")  # Print detailed response content
        raise e

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
