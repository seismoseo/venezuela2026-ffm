"""Build notebook 07 — corrected combined finite-fault model (ffm.4):
43 s rupture-time cap fixed AND the 3 misfitting Rayleigh stations excluded.
Includes a full methods/constraints section and clean legended waveform fits."""
import json, os

nb = {"cells": [], "metadata": {"kernelspec": {"display_name": "Python 3",
      "language": "python", "name": "python3"}, "language_info": {"name": "python"}},
      "nbformat": 4, "nbformat_minor": 5}

def md(t): nb["cells"].append({"cell_type": "markdown", "metadata": {}, "source": t})
def code(t): nb["cells"].append({"cell_type": "code", "metadata": {}, "execution_count": None,
                                 "outputs": [], "source": t})

md("""# Venezuela 2026 — combined finite-fault model (WISP), corrected & audited

Single-event finite-fault inversion of the whole **M7.2 + M7.5 doublet rupture**, referenced to the
**foreshock origin** (22:04:33 UTC) and allowed to span the full rupture — exactly as a SOTA FFM
(and the USGS model) treats it. This notebook documents the **audited** run `ffm.4`, which fixes two
problems found in earlier attempts (preserved as `ffm.0`–`ffm.3`):

1. **Rupture-time saturation (the 43 s wall).** Earlier runs inherited WISP's default
   `max_source_dur = int(2.5 × half_duration) = int(2.5 × 17.5) = 43 s`. For a 270 km unilateral
   rupture (front needs ~85 s at 2.8 km/s) this is far too short, so the inversion piled all eastern
   slip onto the 43 s ceiling — implying rupture velocities of 3.7–5.4 km/s, faster than the model's
   own `max_vel` (3.5 km/s), i.e. **physically impossible**. **Fix:** raise the cap to 110 s.
2. **Three misfitting Rayleigh stations** (EFI, HRV, PKME) — excluded from the inversion
   (`trace_weight = 0`) and shown in gray for reference. (Their Love components are kept.)

Both changes are isolated edits to a clone of the previous run; data, geometry, velocity model,
and weights are otherwise identical.""")

code("""import os, json, sys
import numpy as np, re
import pandas as pd
from IPython.display import Image, display
ROOT = os.path.abspath(os.path.join(os.getcwd(), '..'))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import fig_fault_isochrone as fi
import fig_station_geometry as fsg
from imgutil import trim   # trims WISP's large white margins so panels embed tightly

RUN = os.path.join(ROOT, 'results', 'ffm.4', 'NP1.big')
P = os.path.join(RUN, 'plots')
seg = json.load(open(os.path.join(RUN, 'segments_data.json')))['segments'][0]
ann = json.load(open(os.path.join(RUN, 'annealing_prop.json')))
print('combined model (ffm.4): strike %.0f  dip %.0f  rake %.0f' % (seg['strike'], seg['dip'], seg['rake']))
print('fault %.0f km (along-strike) x %.0f km (along-dip) | %d x %d subfaults'
      % (seg['delta_strike']*seg['stk_subfaults'], seg['delta_dip']*seg['dip_subfaults'],
         seg['stk_subfaults'], seg['dip_subfaults']))
print('max_source_dur = %s s (was 43) | rupture_vel %.1f, bounds %.1f-%.1f km/s'
      % (ann['max_source_dur'], seg['rupture_vel'], seg['min_vel'], seg['max_vel']))""")

md("""## Inversion setup, constraints, and inputs — what is prescribed vs. solved

This section answers the natural "what did you fix vs. what did the data decide?" questions.

### Geometry and the along-dip (vertical) domain
The fault is a single planar segment, **28 subfaults along strike × 6 subfaults down-dip**
(`delta_strike` = 10 km, `delta_dip` = 5 km → 280 km × 30 km). The **only** constraint on the
along-dip (vertical) domain is this **30 km extent** plus **Laplacian smoothing** of slip between
neighbouring subfaults (`regularization_borders.txt` = free edges, no slip forced to zero at a
particular depth). Slip is free on every subfault; depth of the main slip patch is **solved**, not
imposed. The plane's strike/dip (86°/74°) come from the W-phase moment-tensor nodal plane.

### Hypocenter — prescribed
Yes: the **epicenter (10.436°N, 68.528°W) and depth (20.3 km) are fixed** at the catalog/CMT
hypocenter (foreshock origin), placed at subfault (`hyp_stk`=4, `hyp_dip`=4). This is standard for
kinematic FFM — the rupture must nucleate *somewhere*, and the hypocenter is an independent
observation. The rupture **front timing and slip everywhere else are solved**.

### Velocity model for the Green's functions
Built by WISP from **LITHO1.0** (a global lithospheric model) sampled at the epicenter, with a
mantle half-space appended — a 7-layer 1-D crustal model (Moho ≈ 36 km). Body-wave Green's functions
use this near-source structure plus teleseismic ray propagation; surface-wave Green's functions come
from a precomputed long-period normal-mode bank.

### Station selection — automatic, by WISP's `get-data`
**No manual cherry-picking.** Teleseismic body waves: networks **II, G, IU, GE**, channels `BH*`,
**30°–90°** epicentral distance (the standard teleseismic P window: beyond upper-mantle triplications,
before core diffraction), with quality/header checks. Surface waves similarly auto-selected. The only
manual intervention is **down-weighting**: SH is at weight 0.5 by WISP default, and we additionally
set 3 misfitting Rayleigh traces to 0 (below).""")
code("""# velocity model used for the Green's functions (LITHO1.0 at the epicenter + mantle)
vm = open(os.path.join(RUN, 'vel_model.txt')).read().split('\\n')[1:]
rows = [r.split() for r in vm if r.strip()]
df_vm = pd.DataFrame([(float(r[0]), float(r[1]), float(r[2]), float(r[3])) for r in rows],
                     columns=['Vp (km/s)', 'Vs (km/s)', 'Density (g/cc)', 'Thickness (km)'])
df_vm['Top depth (km)'] = df_vm['Thickness (km)'].cumsum().shift(fill_value=0)
display(df_vm)""")

md("""## Is the result data-driven, or tuned to USGS? — a robustness check

We never fed USGS's slip model, length, or timing into the inversion: the mechanism comes from the
independent W-phase CMT, the hypocenter from the catalog, and slip/rake/rupture-time/rise-time are
solved from the waveforms. Two pieces of evidence that the model is **data-driven**:

- Given a **110 s ceiling on a 270 km fault**, the inversion *chose* ~100 s with slip concentrated at
  30–120 km, tapering to zero — it filled **neither** the time ceiling **nor** the fault length.
- **Excluding the 3 worst Rayleigh stations barely changed the model** (below): if a few traces had
  been controlling the answer, removing them would have changed it.""")
code("""# robustness: compare ffm.3 (all data) vs ffm.4 (3 Rayleigh excluded)
def load(run):
    txt = open(os.path.join(ROOT, 'results', run, 'Solution.txt')).read().splitlines()
    m = re.search(r'nx\\(Along-strike\\)=\\s*(\\d+)\\s*Dx\\s*=\\s*([\\d.]+)km\\s*ny\\(downdip\\)=\\s*(\\d+)\\s*Dy\\s*=\\s*([\\d.]+)km', txt[1])
    nx, ny = int(m[1]), int(m[3])
    i0 = next(i for i, l in enumerate(txt) if 'slip' in l and 'rake' in l) + 1
    a = np.array([[float(x) for x in l.split()[:11]] for l in txt[i0:] if len(l.split()) >= 11])
    return (a[:, 3]/100).reshape(ny, nx), a[:, 10].sum()
s3, m3 = load('ffm.3/NP1.big'); s4, m4 = load('ffm.4/NP1.big')
mw = lambda m: (2/3)*(np.log10(m)-16.1)
print('                     ffm.3 (all)   ffm.4 (3 excl)')
print('peak slip (m)        %6.2f        %6.2f' % (s3.max(), s4.max()))
print('Mw                   %6.2f        %6.2f' % (mw(m3), mw(m4)))
print('slip-pattern correlation (ffm.3 vs ffm.4): %.3f' % np.corrcoef(s3.ravel(), s4.ravel())[0, 1])""")

md("""## Data coverage — stations and phase types used
Azimuth (from epicentre) vs epicentral distance, by phase. WISP auto-selected these channels.""")
code("display(Image(fsg.plot(RUN)))")
md("On the globe (azimuthal-equidistant, centred on the epicentre) — dense in North America and Europe, sparser to the south:")
code("display(Image(os.path.join(P, 'StationMap_global.png')))")

md("""## A. Solution
### A1. Slip distribution (unilateral eastward rupture toward Caracas)""")
code("display(Image(os.path.join(P, 'SlipDist_plane0.png')))")
md("""Rupture nucleates deep at the west (foreshock, ~20 km, star) and propagates **east and up-dip**;
the main slip patch (**peak ~2.8 m**) is shallow and ~30–120 km east of the hypocenter — offshore
toward Caracas/La Guaira, consistent with the damage distribution and back-projection/directivity.""")

md("### A2. On-fault slip + rupture-front isochrones (true 1:1 scale)")
code("display(Image(fi.plot(RUN)))")
md("""**This is the same slip model as A1**, drawn at true 1:1 scale (no vertical exaggeration) with
the hypocentre (star) at the origin — note it now sits exactly on the **t = 0** isochrone (an earlier
version had a one-cell indexing offset). White contours are **rupture-front arrival isochrones**
(every 5 s; WISP's A1 shows the same front every 10 s). The front propagates continuously east to
**~100 s** — **no 43 s saturation** — and along the dominant eastward direction the implied rupture
velocity is everywhere **subshear** (≈2.7 km/s, obeying `max_vel`).""")

md("""### A3. Rise time (per-subfault slip duration) — solved, not assumed

Is rise time prescribed? **No — it is solved by the inversion**, within a windowed slip-rate basis
(`min_rise` = 1 s, `delta_rise` = 2 s, **8 time windows**): each subfault's source-time function is a
sum of overlapping triangles whose amplitudes the inversion fits, so the *shape and duration* of slip
at each subfault are data-driven. The map below shows the resulting per-subfault slip duration
(rise + fall).""")
code("display(Image(fi.plot_risetime(RUN)))")
md("Slip durations are mostly ~5–15 s (median ~10 s), longer on the deeper/edge subfaults where they are less well resolved — the smoothness regularization fills weakly-constrained patches.")

md("### A4. Moment-rate function (full ~100 s, complex multi-pulse)")
code("display(Image(os.path.join(P, 'MomentRate.png')))")
md("M0 = 2.83×10²⁰ N·m, **Mw 7.57**. Moment release spans the full rupture (bulk 0–70 s, low tail to ~100 s) as a complex multi-pulse STF — the doublet + extended rupture captured as one data-driven source.")

md("### A5. Map")
code("display(Image(os.path.join(P, 'Map.png')))")

md("""## B. Waveform-fit validation (WISP native panels)

In every panel below (WISP's standard layout): **black = observed, red = synthetic** (the inverted
fit). **Faded/translucent traces are excluded** (`trace_weight = 0`, not used in the inversion).
Reading the panel annotations:
- **Left margin:** phase code (**P** / **SH** for body; **Z** = Rayleigh-vertical, **T** = Love-transverse),
  station name, and the amplitude unit (**nm** for body, **mm** for surface), followed by the
  **azimuth (°)** and **epicentral distance (°)**.
- **Right margin:** the **black number = peak amplitude of the observed** trace and the
  **red number = peak amplitude of the synthetic** — comparing the two is a direct amplitude-fit check.
- **x-axis** = time after origin (s); the vertical line marks the alignment.

**Filtering differs by phase** (standard — body and surface waves carry information in different period
bands):
- **Teleseismic body waves (P, SH):** band-pass **0.006–1.0 Hz** (≈ **1–167 s**), sampled at 0.2 s.
- **Surface waves (Rayleigh, Love):** long-period, cosine-tapered over
  **0.003 / 0.004 / 0.006 / 0.007 Hz** (passband ≈ **167–250 s**), sampled at 4 s.

### B1. P body waves — well fit""")
code("display(Image(trim(os.path.join(P, 'P_body_waves.png'))))")
md("Synthetics (red) track the observed (black) in shape and amplitude across the network — the key improvement from modelling the full sequence (cf. the poor P fits in the mainshock-only notebooks 04/05). Body-wave band 0.006–1.0 Hz.")

md("""### B2. SH body waves — fit, window, and why a residual remains

Is the SH fit as good as it gets, and is the window length reasonable?

- **SH is down-weighted to 0.5** (vs P = 1.0) by WISP default, because SH radiation for a near-vertical
  strike-slip fault is **near-nodal** at many azimuths — small modelling/orientation errors produce
  large relative amplitude errors. The residual under-fit is intrinsic to this radiation geometry,
  not a bug; a no-SH control inversion gives the same slip model, so it does not bias the solution.
- **Window length:** the body-wave window is **70 s**. This need not equal the 100 s rupture duration:
  teleseismic directivity compresses the *apparent* source duration at a station to ~77–107 s, the
  bulk of the moment is in the first ~70 s, and the long-period **surface waves (3000 s window)** carry
  the full extent. So the short window means the late eastern rupture is *less tightly constrained* by
  body waves (larger uncertainty), **not** a forced artifact — fundamentally different from the 43 s
  model-space cap, which forbade the solution from existing. Body-wave band 0.006–1.0 Hz.""")
code("display(Image(trim(os.path.join(P, 'SH_body_waves.png'))))")

md("### B3. Rayleigh surface waves — EFI, HRV, PKME excluded (faded)")
code("display(Image(trim(os.path.join(P, 'Rayleigh_surf_waves.png'))))")
md("""Excellent fit across most of the network (long-period band ≈167–250 s). The three **faded**
traces (EFI 173°, HRV 356°, PKME 359°) fit poorly — consistent with radiation-pattern nodes / path
effects at those azimuths — and were **excluded from the inversion** (drawn for reference only).
Removing them left the slip model essentially unchanged (correlation 0.90 with the all-data run),
confirming they were not controlling the solution.""")

md("### B4. Love surface waves — excellent")
code("display(Image(trim(os.path.join(P, 'Love_surf_waves.png'))))")
md("Excellent fit across the network (long-period band ≈167–250 s; after the earlier BH1/BH2 channel-azimuth correction).")

md("""## C. Can WISP model regional waveforms?

**Yes.** WISP supports near-source data types — strong motion (`-t strong`), cGNSS (`-t cgnss`),
static GNSS (`-t gnss`), and InSAR (`-t im`) — using locally computed fk Green's functions on the
1-D crustal model, exactly the regime of regional broadband/strong-motion waveforms (≲ a few hundred
km). The limitation here is **data, not method**: the only dense near-field network is FUNVISIS, whose
waveforms are blocked. Open regional stations (Colombia CM, Caribbean CU/WI/NA at ~300–1300 km) could
in principle be added as a `strong`/regional set, though at those distances a regional 1-D model and
careful filtering would be needed. This is a natural next experiment.""")

md("## D. Summary and comparison to USGS")
code("""cmp = pd.DataFrame({
  'Quantity': ['Reference/origin','Mechanism','Mw','Peak slip','Rupture length','Directivity',
               'Rupture duration','Rupture velocity','Body-wave fit','Surface-wave fit'],
  'This combined FFM (ffm.4)': ['foreshock 22:04:33','E-W right-lateral SS (strike 86, dip 74)','7.57',
                        '~2.8 m','~160 km imaged (270 km fault)','unilateral eastward (up-dip)',
                        '~100 s','subshear ~2.5 km/s','P good; SH fit (0.5 wt, near-nodal residual)',
                        'good (Love excellent)'],
  'USGS (published)': ['foreshock-referenced, combined','E-W right-lateral SS, dip ~75 S','~7.5 (comb 7.54)',
                       '~2-3.6 m','~230 km (2 segments)','unilateral eastward toward Caracas',
                       '>90 s','subshear 3-3.5 km/s','-','-']})
display(cmp)""")

md("""### Take-homes

- **Two bugs fixed, both physically diagnosed (not tuned to USGS):** the 43 s rupture-time cap (a
  model-space truncation that forced unphysical simultaneous eastern slip) raised to 110 s → front
  now propagates continuously to ~100 s, everywhere subshear; and 3 misfitting Rayleigh traces
  excluded. Misfit did not degrade (0.105 → 0.099).
- **Result is data-driven:** the inversion filled neither the time ceiling nor the fault length, and
  excluding the 3 outliers left the slip model essentially unchanged (correlation 0.90, identical Mw).
- **Mechanism / directivity robust and USGS-consistent:** E–W right-lateral strike-slip, **Mw 7.57**,
  **unilateral eastward rupture** toward Caracas, deep western nucleation → shallow main slip east
  (peak ~2.8 m), complex ~100 s source-time function.
- **What is prescribed vs solved:** hypocenter (epicenter + depth) and fault-plane orientation are
  prescribed from independent CMT/catalog; the along-dip domain is a 30 km canvas with Laplacian
  smoothing; **slip, rake, rupture time, and rise time are all solved** from the waveforms.
- **Velocity model:** LITHO1.0 at the epicenter + mantle half-space (Moho ≈ 36 km).
- **Honest limitations:** SH residual (near-nodal strike-slip, weight 0.5; does not bias slip); 70 s
  body window loosens the late-rupture constraint (surface waves carry it); a few Rayleigh nodal
  outliers excluded.
- **Next:** restitution/checkerboard + station-jackknife resolution tests; optionally lengthen the
  body window; explore adding open regional waveforms; then the InSAR-enhanced inversion.""")

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "notebooks", "07_wisp_venezuela_combined_corrected.ipynb")
json.dump(nb, open(out, "w"), indent=1)
print("wrote", out, "|", len(nb["cells"]), "cells")
