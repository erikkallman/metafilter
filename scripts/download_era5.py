# MIT License
# Copyright (c) 2024 Erik Källman
# See the LICENSE file for more details.

import cdsapi
from utils.config import AREA, OUTPUT_DIR

def download_era5_land():
    c = cdsapi.Client()
    c.retrieve(
        'reanalysis-era5-land',
        {
            'variable': ['2m_temperature', 'total_precipitation'],
            'year': '2023',
            'month': '07',
            'day': [f'{day:02d}' for day in range(1, 32)],
            'time': [f'{hour:02d}:00' for hour in range(24)],
            'area': AREA,
            'format': 'netcdf',
        },
        f"{OUTPUT_DIR}/era5/era5_land_july_2023.nc"
    )

if __name__ == "__main__":
    download_era5_land()
