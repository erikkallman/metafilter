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

# Sentinel API credentials
# Sentinel API credentials
DATASPACE_USERNAME = os.getenv("DATASPACE_USERNAME")
DATASPACE_PASSWORD = os.getenv("DATASPACE_PASSWORD")

# Ensure credentials are loaded
if not DATASPACE_USERNAME or not DATASPACE_PASSWORD:
    raise EnvironmentError("DATASPACE_USERNAME and DATASPACE_PASSWORD must be set in the .env file.")
