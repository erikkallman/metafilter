# MIT License
# Copyright (c) 2024 Erik Källman
# See the LICENSE file for more details.
import json
import os
import folium
from pyproj import Transformer
from shapely.geometry import shape
from utils.config import AREA

def visualize_sentinel_results(temporal_extent):
    """
    Visualize the footprints of Sentinel-2 products on a map.
    """
    stac_data = extract_stac_data()

    stac_coordinates = transform_stac_geometry(stac_data)

    create_folium_map(stac_coordinates, AREA, temporal_extent)

def extract_stac_data():
    stac_file_path = os.path.join("..\\output_directory", "stac.json")
    if not os.path.exists(stac_file_path):
        raise FileNotFoundError("stac.json not found in the extracted files.")
    with open(stac_file_path, 'r') as f:
        stac_data = json.load(f)
        return stac_data

def transform_stac_geometry(stac_data, src_crs="epsg:32633", dst_crs="epsg:4326"):
    transformer = Transformer.from_crs(src_crs, dst_crs, always_xy=True)
    utm_geometry = stac_data["geometry"]["coordinates"][0]
    latlon_coordinates = [transformer.transform(x, y) for x, y in utm_geometry]
    return latlon_coordinates

def create_folium_map(stac_coordinates, spatial_extent, temporal_extent, output_file="metafilter_results_map.html"):

    # Format spatial and temporal extents for tooltip
    spatial_info = f"[West: {spatial_extent['west']}, East: {spatial_extent['east']}, " \
                   f"South: {spatial_extent['south']}, North: {spatial_extent['north']}]"

    temporal_info = f"{temporal_extent[0]} to {temporal_extent[1]}"

    # Create a Folium map centered at the centroid of the STAC footprint
    stac_polygon = shape({"type": "Polygon", "coordinates": [stac_coordinates]})
    centroid = stac_polygon.centroid
    m = folium.Map(location=[centroid.y, centroid.x], zoom_start=8)

    # Add the STAC footprint as a GeoJSON layer with updated tooltip
    folium.GeoJson(
        stac_polygon.__geo_interface__,  # GeoJSON representation of the footprint
        tooltip=(
            f"<b>STAC Footprint</b><br>"
            f"<b>Spatial Extent:</b> {spatial_info}<br>"
            f"<b>Temporal Extent:</b> {temporal_info}"
        )
    ).add_to(m)

    # Save the map
    m.save(output_file)
    print(f"Map saved as `{output_file}`.")

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
