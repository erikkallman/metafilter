# MIT License
# Copyright (c) 2024 Erik Källman
# See the LICENSE file for more details.

import folium
from shapely.wkt import loads as load_wkt
import geopandas as gpd

def preprocess_footprint(footprint_wkt):
    """
    Clean and standardize the WKT format for footprints.
    """
    if footprint_wkt.startswith("geography'SRID=4326;"):
        footprint_wkt = footprint_wkt.replace("geography'SRID=4326;", "").strip()
    elif footprint_wkt.startswith("SRID=4326;"):
        footprint_wkt = footprint_wkt.replace("SRID=4326;", "").strip()
    return footprint_wkt

def visualize_sentinel_results(products):
    """
    Visualize the footprints of Sentinel-2 products on a map.
    """
    # Create a base map centered on the approximate area of interest
    m = folium.Map(location=[67.0, 17.0], zoom_start=5)

    for product in products:
        product_id = product['Id']
        name = product['Name']
        start_date = product['ContentDate']['Start']
        end_date = product['ContentDate']['End']
        footprint_wkt = product['Footprint']  # Assuming the footprint is in WKT format

        # Preprocess the Footprint WKT
        footprint_wkt = preprocess_footprint(footprint_wkt)

        try:

            # Convert WKT to a Shapely object
            footprint = load_wkt(footprint_wkt)

            # Convert Shapely geometry to GeoJSON for Folium
            geojson = gpd.GeoSeries([footprint]).__geo_interface__

            # Add the footprint to the map
            folium.GeoJson(
                geojson,
                name=f"{name} ({product_id})",
                tooltip=(
                    f"ID: {product_id}<br>"
                    f"Name: {name}<br>"
                    f"Start: {start_date}<br>"
                    f"End: {end_date}"
                )
            ).add_to(m)
        except Exception as e:
            print(f"Error processing footprint for product {product_id}: {e}")

    # Add layer control
    folium.LayerControl().add_to(m)

    # Save the map to an HTML file
    m.save("sentinel_results_map.html")
    print("Map saved to sentinel_results_map.html")

if __name__ == "__main__":
    # Example: Mock data for products
    example_products = [
        {
            "Id": "example-id-1",
            "Name": "S2A_MSIL2A_20230701T102031_N0509_R065_T33WXS_20230701T134500",
            "ContentDate": {
                "Start": "2023-07-01T10:20:31Z",
                "End": "2023-07-01T13:45:00Z"
            },
            "Footprint": "POLYGON((10.0 65.0, 24.0 65.0, 24.0 69.0, 10.0 69.0, 10.0 65.0))"
        },
        {
            "Id": "example-id-2",
            "Name": "S2B_MSIL2A_20230710T102031_N0509_R065_T33WXS_20230710T134500",
            "ContentDate": {
                "Start": "2023-07-10T10:20:31Z",
                "End": "2023-07-10T13:45:00Z"
            },
            "Footprint": "POLYGON((12.0 66.0, 15.0 66.0, 15.0 67.0, 12.0 67.0, 12.0 66.0))"
        }
    ]

    visualize_sentinel_results(example_products)
