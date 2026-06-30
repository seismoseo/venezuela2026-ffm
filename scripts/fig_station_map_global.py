"""
fig_station_map_global.py — Global map of the teleseismic stations used in the WISP
inversion, coloured by phase type, on an azimuthal-equidistant projection centred on
the epicentre (so distance is radial and azimuthal coverage is faithful). Coastlines
+ country borders show which countries the stations are in.

Station lat/lon are computed from the epicentre + (azimuth, distance) stored in
tele_waves.json / surf_waves.json. Run in an env with PyGMT (base / venezuela2026).

Usage: python scripts/fig_station_map_global.py <NP_dir> [out.png]
"""

import json
import os
import sys

import numpy as np
import pandas as pd

EPI_LAT, EPI_LON = 10.436, -68.5277   # foreshock nucleation (sequence reference)


def dest_point(lat0, lon0, az_deg, dist_deg):
    """Destination lat/lon from a start point, azimuth and angular distance (deg)."""
    lat1, lon1 = np.radians(lat0), np.radians(lon0)
    az, d = np.radians(az_deg), np.radians(dist_deg)
    lat2 = np.arcsin(np.sin(lat1) * np.cos(d) + np.cos(lat1) * np.sin(d) * np.cos(az))
    lon2 = lon1 + np.arctan2(np.sin(az) * np.sin(d) * np.cos(lat1),
                             np.cos(d) - np.sin(lat1) * np.sin(lat2))
    return np.degrees(lat2), (np.degrees(lon2) + 180) % 360 - 180


def _load(np_dir, fname, cmap):
    p = os.path.join(np_dir, fname)
    if not os.path.isfile(p):
        return []
    rows = []
    for w in json.load(open(p)):
        if float(w.get("trace_weight", 1)) <= 0:
            continue
        ph = cmap.get(w["component"])
        if ph:
            la, lo = dest_point(EPI_LAT, EPI_LON, float(w["azimuth"]), float(w["distance"]))
            rows.append((ph, la, lo))
    return rows


def plot(np_dir, out=None):
    import pygmt
    out = out or os.path.join(np_dir, "plots", "StationMap_global.png")
    recs = (_load(np_dir, "tele_waves.json", {"BHZ": "P", "BHT": "SH"})
            + _load(np_dir, "surf_waves.json", {"BHZ": "Rayleigh", "BHT": "Love"}))
    df = pd.DataFrame(recs, columns=["phase", "lat", "lon"])
    styles = {"P": ("c0.28c", "#1f78b4"), "SH": ("s0.28c", "#e31a1c"),
              "Rayleigh": ("t0.30c", "#33a02c"), "Love": ("i0.30c", "#ff7f00")}

    fig = pygmt.Figure()
    pygmt.config(FONT="Helvetica", MAP_FRAME_TYPE="plain")
    proj = f"E{EPI_LON}/{EPI_LAT}/150/16c"   # azimuthal equidistant, centred on epicentre
    fig.coast(region="g", projection=proj, land="gray85", water="white",
              shorelines="0.25p,gray55", borders="1/0.25p,gray70", frame="g30")
    # 30 and 90 deg distance rings
    for r in (30, 90):
        fig.plot(x=[EPI_LON], y=[EPI_LAT], style=f"E-{2*r}d", pen="0.8p,gray40,-")
    for ph, (stl, col) in styles.items():
        g = df[df.phase == ph]
        if len(g):
            fig.plot(x=g.lon, y=g.lat, style=stl, fill=col, pen="0.3p,black",
                     label=f"{ph} (n={len(g)})")
    fig.plot(x=EPI_LON, y=EPI_LAT, style="a0.6c", fill="yellow", pen="1p,black")
    fig.legend(position="jBL+o0.2c", box="+gwhite+p0.5p")
    fig.text(x=EPI_LON, y=EPI_LAT, text="dashed rings: 30 deg and 90 deg",
             font="9p,Helvetica", offset="0c/-8.0c", no_clip=True)
    fig.savefig(out, dpi=200)
    print(f"global station map ({len(df)} stations) -> {out}")
    return out


if __name__ == "__main__":
    plot(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
