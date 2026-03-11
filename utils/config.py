import os

from dotenv import load_dotenv

load_dotenv()

# Covers a part of the northern half of Sweden
AREA = {
    "west": 18.0,
    "east": 18.5,
    "south": 66.0,
    "north": 66.5,
}

# Output directories
OUTPUT_DIR = "data"
NDVI_OUTPUT_DIR = os.path.join(OUTPUT_DIR, "ndvi_comparison")

eo_service_url = os.getenv("OPENEO_SERVICE_URL", "https://openeo.digitalearth.se")
username = os.getenv("OPENEO_USERNAME") or os.getenv("DATASPACE_USERNAME")
password = os.getenv("OPENEO_PASSWORD") or os.getenv("DATASPACE_PASSWORD")

if not username or not password:
    raise EnvironmentError(
        "OpenEO credentials must be set via OPENEO_USERNAME/OPENEO_PASSWORD "
        "or DATASPACE_USERNAME/DATASPACE_PASSWORD."
    )
