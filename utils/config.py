# MIT License
# Copyright (c) 2024 Erik Källman
# See the LICENSE file for more details.

from dotenv import load_dotenv
import os

load_dotenv()

# Area of interest: Västerbotten subset
AREA = [69.0, 10.0, 65.0, 24.0]  # Covers the northern half of Sweden

# Output directories
OUTPUT_DIR = "data"

eo_service_url = "https://openeo.digitalearth.se"
username = "testuser"
password = "secretpassword"

# Ensure credentials are loaded
if not username or not password:
    raise EnvironmentError("username and password must be set in the .env file.")
