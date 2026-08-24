# PWP Tutorial: Hurricane-Driven Mixed Layer Response

A four-notebook walkthrough that builds glider-observed initial conditions for
Hurricane Ida (2021), runs them through the Price-Weller-Pinkel (PWP) 1-D
ocean mixed-layer model, and compares a barrier-layer case against a
synthetic no-barrier-layer case to see how pre-storm salinity stratification
changes the upper-ocean response to a hurricane.

Density/salinity calculations use the [TEOS-10 `gsw`](https://teos-10.github.io/GSW-Python/)
package throughout (the older, deprecated `seawater`/EOS-80 package has been
removed).

## Background

This is a simplified, standalone version of the analysis in
[rucool/BarrierLayer_HurricaneIda](https://github.com/rucool/BarrierLayer_HurricaneIda/tree/main),
trimmed down to the core pipeline for teaching purposes. The full analysis
went into:

> Miles, T. N., Coakley, S. J., Engdahl, J. M., Rudzin, J. E., Tsei, S., &
> Glenn, S. M. (2023). Ocean mixing during Hurricane Ida (2021): the impact
> of a freshwater barrier layer. *Frontiers in Marine Science*.
> https://doi.org/10.3389/fmars.2023.1224609

## Notebooks

Run in order:

1. **`notebook1.ipynb`** — Pulls glider profiles (via ERDDAP) and IBTrACS
   hurricane-track data, identifies the mixed layer depth (MLD) and
   isothermal layer depth (ILD) for each profile, and builds the "observed"
   (barrier layer) and synthetic "altered" (no barrier layer) initial
   condition NetCDF files used by the model run.
2. **`notebook2.ipynb`** — Builds and validates the atmospheric forcing:
   pulls HRRR wind/heat-flux fields at the buoy and glider locations,
   compares them against buoy observations, and writes out the forcing
   NetCDF used by PWP.
3. **`notebook3.ipynb`** — Runs the PWP model itself for a given initial
   condition (original or altered) and forcing case, and saves the
   time-evolving temperature/salinity/density/velocity output.
4. **`notebook4.ipynb`** — Post-processes the PWP output: computes MLD/ILD
   evolution for both cases and plots the temperature response, comparing
   the barrier-layer and no-barrier-layer runs.

## Setup

```bash
pip install numpy pandas xarray netCDF4 matplotlib scipy scikit-learn cmocean bottleneck gsw erddapy seawater
```

`seawater` is still required here even though none of these notebooks import
it directly — the PWP model code itself (`PWP.py`/`PWP_helper.py`, see
below) depends on it internally.

Each notebook has a **Paths** cell near the top — edit `DATA_DIR` (and
`PWP_CODE_DIR` in notebook3) to point at your local copies of the files
below before running.

### PWP model code

Notebook 3 imports the PWP model itself (`PWP.py`, `PWP_helper.py`), which is
not part of this repo. Download or clone it from
[earlew/pwp_python_00](https://github.com/earlew/pwp_python_00):

```bash
git clone https://github.com/earlew/pwp_python_00.git
```

and point `PWP_CODE_DIR` at it (default expects it as a sibling folder,
`../pwp_python_00`, i.e. one level up from this notebook folder).

### Data you need to supply

Place these under `DATA_DIR` (default `./data`, i.e. alongside the
notebooks):

| File | Used by | Notes |
|---|---|---|
| `ibtracs.ALL.list.v04r01.csv` | 1 | IBTrACS best-track data (all basins, v04r01) — download from [NCEI](https://www.ncei.noaa.gov/data/international-best-track-archive-for-climate-stewardship-ibtracs/v04r01/access/csv/ibtracs.ALL.list.v04r01.csv) and place directly in `DATA_DIR` (i.e. `data/ibtracs.ALL.list.v04r01.csv`) |
| `forcing/buoy_location.csv` | 2 | Buoy site metadata (name, lat/lon) for HRRR extraction |
| `forcing/glider_location_close.csv`, `forcing/glider_location_082800.csv` | 2 | Glider location metadata per case |
| `forcing/hrrr_data_20210825_20210905/*.nc` | 2 | Daily HRRR NetCDF files covering the storm period |
| `final_run/data/`, `final_run/figures/` | 1, 2, 3, 4 | Created automatically — this is where each notebook's outputs (initial conditions, forcing, PWP runs, figures) get written and then read back by the next notebook |

**A note on the HRRR files:** full daily HRRR grids are ~700+ MB each,
far too large for GitHub. This repo ships only a small cropped example
(landfall ± 1 day, spatially cropped to the two sites used here) —
see `scripts/make_example_hrrr_subset.py` for how it was made, and for
your own runs with the full storm period you'll want the complete set
from your own HRRR archive.

Notebook 4 also re-opens the notebook-1 initial-condition file
(`ng645-<profileID>_original.nc`) alongside the PWP output, since the PWP
run itself doesn't carry latitude/longitude — that fixed position is what
the `gsw` conversion below needs.

## Notes on the `gsw` swap

Where the original code used `seawater.dens(S, T, P)` (practical salinity,
in-situ temperature, EOS-80), the notebooks now compute Absolute Salinity and
Conservative Temperature first and call `gsw.rho`:

```python
SA = gsw.SA_from_SP(SP, p, lon, lat)
CT = gsw.CT_from_t(SA, t, p)
rho = gsw.rho(SA, CT, p)
```

`seawater.dens0(S, T)` (potential density at the surface) became `gsw.rho(SA, CT, 0)`,
and `seawater.f(lat)` (Coriolis parameter) became `gsw.f(lat)`.

Pressure is approximated as depth in dbar throughout, matching the
approximation the original `seawater` code already made at these shallow,
near-surface depths.
