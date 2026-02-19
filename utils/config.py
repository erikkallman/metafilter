from dotenv import load_dotenv
import os

load_dotenv()

# Covers a part of the northern half of Sweden
AREA = {
    "west": 18.0,
    "east": 18.5,
    "south": 66.0,
    "north": 66.5
}

# Output directories
OUTPUT_DIR = "data"

eo_service_url = "https://openeo.digitalearth.se"
username = "testuser"
password = "secretpassword"

# Ensure credentials are loaded
if not username or not password:
    raise EnvironmentError("username and password must be set in the .env file.")
