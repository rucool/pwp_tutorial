"""
One-time prep script -- NOT part of the tutorial pipeline itself.

The raw HRRR files in data/forcing/hrrr_data_20210825_20210905/ are full
CONUS-grid daily files (~700+ MB each) and can't go on GitHub. load_hrrr()
in notebook2 only ever samples the single grid point nearest to a given
site, so the fix is to crop each file down to a small box around the two
sites used in this tutorial and drop the variables load_hrrr() never reads.

Run this once, in the same environment/kernel you use for the notebooks,
after pointing SRC_DIR at your full local HRRR files. It writes small
cropped copies to OUT_DIR -- it does not touch your original files.
"""
import os
import xarray as xr

SRC_DIR = './data/forcing/hrrr_data_20210825_20210905'
OUT_DIR = './data/forcing/hrrr_data_20210825_20210905_example'

# Days to keep for the GitHub example (landfall +/- 1 day)
EXAMPLE_DATES = ['20210828', '20210829', '20210830']

# Bounding box comfortably containing both sites used in this tutorial:
#   buoy 42040:        29.207,  -88.237
#   glider ng645:       28.123, -89.366
LAT_MIN, LAT_MAX = 27.0, 31.0
LON_MIN, LON_MAX = -91.0, -87.0

# Only the variables load_hrrr() actually reads
KEEP_VARS = ['gridlat_0', 'gridlon_0', 'wind_speed', 'eastward_wind',
             'northward_wind', 'lv_HTGL1', 'time']

os.makedirs(OUT_DIR, exist_ok=True)

for date in EXAMPLE_DATES:
    fn = f'hrrr_data_{date}.nc'
    src_path = os.path.join(SRC_DIR, fn)
    if not os.path.exists(src_path):
        print(f'Skipping {fn}: not found in {SRC_DIR}')
        continue

    ds = xr.open_dataset(src_path)
    ds_small = ds[[v for v in KEEP_VARS if v in ds.variables]]

    mask = ((ds_small['gridlat_0'] >= LAT_MIN) & (ds_small['gridlat_0'] <= LAT_MAX) &
            (ds_small['gridlon_0'] >= LON_MIN) & (ds_small['gridlon_0'] <= LON_MAX))
    ds_small = ds_small.where(mask, drop=True)

    out_path = os.path.join(OUT_DIR, fn)
    ds_small.to_netcdf(out_path)
    ds.close()

    orig_mb = os.path.getsize(src_path) / 1e6
    new_mb = os.path.getsize(out_path) / 1e6
    print(f'{fn}: {orig_mb:.0f} MB -> {new_mb:.2f} MB')

print(f'\nDone. Cropped files are in {OUT_DIR} -- notebook2.ipynb reads directly')
print('from this folder name, so no renaming needed.')
