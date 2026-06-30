# 2026 Venezuela M7.5 doublet — preliminary teleseismic finite-fault model

Preliminary finite-fault rupture model of the **24 June 2026 northern-Venezuela strike-slip
doublet** (Mw 7.2 foreshock + Mw 7.5 mainshock, 39 s apart; San Sebastián fault), from
**teleseismic body + surface waves**, with a side-by-side comparison to the published **USGS NEIC**
model.

> **Status: preliminary.** This is an independent rupture-imaging result, shared for transparency and
> reproducibility. It is part of a larger study of the sequence's anomalous aftershock-magnitude
> deficit; the InSAR-enhanced inversion and the aftershock/afterslip analysis are ongoing.

## Headline result

| Quantity | This study | USGS NEIC |
|---|---|---|
| Mw | 7.57 | 7.54 |
| Mechanism | E–W right-lateral strike-slip (strike 86°, dip 74°, rake −176°) | strike 80°/86°, dip 75°, rake −175° |
| Directivity | unilateral **eastward** toward Caracas (up-dip) | unilateral eastward |
| Peak slip | ~2.8 m | ~2.5 m |
| Rupture duration | ~100 s | >90 s |
| Avg. rupture velocity | ~2.7 km/s (subshear) | 2.32 km/s |
| Data | teleseismic body (59) + surface (61) | teleseismic body (58) + surface (63) |

The two independent inversions yield **nearly identical moment-rate functions** (dominant pulse at
~40 s, matching multi-pulse shape) and the **same main-slip location** (~70–120 km east of the
hypocentre, offshore toward Caracas). Neither model inverted InSAR — adding it is the planned next
step.

## Method

The inversion uses **WISP** (`neic-finitefault`; Ji, Koch & Goldberg — the USGS NEIC method), a
wavelet-domain simulated-annealing kinematic finite-fault inversion, with `fk` Green's functions on a
**LITHO1.0** 1-D velocity model sampled at the epicentre. The whole doublet is modelled as one
extended rupture referenced to the foreshock origin (single combined-moment CMT).

## What is and isn't in this repository

- **Included:** the two analysis notebooks (with embedded figures), the plotting/comparison scripts,
  the **WISP solution outputs** needed to regenerate every figure, and the USGS reference products.
- **Not included:** the WISP source code itself, and the raw/processed seismic waveforms. To re-run
  the *inversion* (not just the figures) you must install WISP separately and download the data —
  see [Reproducing the inversion](#reproducing-the-inversion).

```
notebooks/
  07_wisp_venezuela_combined_corrected.ipynb   # the FFM: solution, isochrones, rise time, waveform fits
  08_compare_usgs.ipynb                          # comparison with the USGS NEIC model
scripts/
  fig_fault_isochrone.py        # true-1:1-scale slip + rupture-front isochrones; rise-time map
  fig_station_geometry.py       # azimuth–distance station coverage by phase
  fig_station_map_global.py     # global station map (PyGMT)
  usgs_compare.py               # moment-rate / slip comparison vs USGS
  imgutil.py                    # trims whitespace from WISP's native waveform panels
  build_nb07.py, build_nb08.py  # regenerate the notebooks from the scripts + results
results/
  ffm.4/NP1.big/   # WISP solution outputs for the final model (Solution.txt, STF.txt, plots/, ...)
  ffm.3/NP1.big/   # previous run (used for a robustness check in nb07)
data/usgs/         # USGS NEIC products: complete_inversion.fsp, moment_rate.mr, CMTSOLUTION, FFM.geojson
reproduce_inversion/   # scripts that drive WISP to produce ffm.3/ffm.4 (require WISP)
```

## Viewing

Open the notebooks directly (GitHub renders them, figures included), or locally:

```bash
jupyter lab notebooks/07_wisp_venezuela_combined_corrected.ipynb
```

## Regenerating the figures (no WISP needed)

The figures are produced from the included WISP solution outputs, so they regenerate without WISP:

```bash
conda env create -f environment.yml   # or: pip install numpy pandas matplotlib pillow pygmt obspy
conda activate venezuela2026-ffm
cd scripts && python build_nb07.py && python build_nb08.py        # rebuild notebook JSON
cd ../notebooks && jupyter nbconvert --to notebook --execute --inplace *.ipynb
```

Notebooks resolve paths relative to the repository root (run them from `notebooks/`).

## Reproducing the inversion

The inversion itself requires **WISP** (not included):

1. Install `neic-finitefault` (WISP): https://github.com/usgs/neic-finitefault
2. Acquire teleseismic data (IRIS/GEOFON networks II, G, IU, GE; 30°–90°) and responses.
3. The scripts in `reproduce_inversion/` show how the final runs were produced from a base WISP run:
   `rerun_ffm_longdur.py` (set the maximum source duration so the rupture front isn't truncated) and
   `rerun_ffm_exclude_rayleigh.py` (down-weight three misfitting Rayleigh stations). See the notebook
   methods sections for the full parameterization.

## Data and software credits

- **WISP / `neic-finitefault`** — Ji, C., D. J. Wald, & D. V. Helmberger; USGS NEIC implementation
  (Koch, Goldberg et al.). Please cite WISP if you use this workflow.
- **USGS NEIC** finite-fault product for event `us6000t7zp` (files in `data/usgs/`).
- **Teleseismic waveforms** — IRIS/EarthScope and GEOFON FDSN data centres.
- Velocity model: **LITHO1.0** (Pasyanos et al., 2014).

## License

Code: MIT (see `LICENSE`). Figures and derived results: CC-BY-4.0. USGS products in `data/usgs/` are
U.S. Government public-domain works.
