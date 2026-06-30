"""
fig_station_geometry.py — Azimuth–distance coverage of the waveforms used in the
WISP inversion, coloured by phase type (teleseismic P / SH body waves, Rayleigh /
Love surface waves). Polar plot: azimuth (from epicentre, N up, clockwise) vs
epicentral distance (deg). Reads tele_waves.json (BHZ=P, BHT=SH) and
surf_waves.json (BHZ=Rayleigh, BHT=Love) from a WISP NP directory.

Usage: python scripts/fig_station_geometry.py <NP_dir> [out.png]
"""

import json
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def _helvetica():
    from matplotlib import font_manager
    for n in ("Helvetica", "Arial", "Nimbus Sans"):
        if any(n in f.name for f in font_manager.fontManager.ttflist):
            matplotlib.rcParams["font.family"] = n; break


def _load(np_dir, fname, comp_map):
    p = os.path.join(np_dir, fname)
    if not os.path.isfile(p):
        return []
    out = []
    for w in json.load(open(p)):
        if float(w.get("trace_weight", 1)) <= 0:
            continue
        phase = comp_map.get(w["component"])
        if phase:
            out.append((phase, float(w["azimuth"]), float(w["distance"]), w["name"]))
    return out


def plot(np_dir, out=None):
    _helvetica()
    out = out or os.path.join(np_dir, "plots", "StationGeometry.png")
    recs = (_load(np_dir, "tele_waves.json", {"BHZ": "P (body)", "BHT": "SH (body)"})
            + _load(np_dir, "surf_waves.json", {"BHZ": "Rayleigh", "BHT": "Love"}))
    styles = {"P (body)": ("o", "#1f78b4"), "SH (body)": ("s", "#e31a1c"),
              "Rayleigh": ("^", "#33a02c"), "Love": ("v", "#ff7f00")}

    fig = plt.figure(figsize=(8.5, 8.5))
    ax = fig.add_subplot(111, projection="polar")
    ax.set_theta_zero_location("N"); ax.set_theta_direction(-1)
    counts = {}
    for phase, (mk, col) in styles.items():
        az = [r[1] for r in recs if r[0] == phase]
        di = [r[2] for r in recs if r[0] == phase]
        counts[phase] = len(az)
        ax.scatter(np.radians(az), di, marker=mk, s=42, facecolor=col,
                   edgecolor="black", linewidth=0.4, alpha=0.85,
                   label=f"{phase} (n={len(az)})", zorder=3)
    ax.plot(0, 0, marker="*", ms=20, mfc="yellow", mec="black", zorder=5)
    ax.set_rmax(100); ax.set_rticks([30, 60, 90])
    ax.set_rlabel_position(135)
    ax.set_title("Station geometry of waveforms used (azimuth vs epicentral distance)\n"
                 "Venezuela M7.5 combined finite-fault inversion", fontsize=11, pad=20)
    ax.legend(loc="upper right", bbox_to_anchor=(1.18, 1.10), fontsize=9,
              edgecolor="black")
    # annotate distance unit + azimuthal-gap note
    n = len(recs)
    az_all = np.sort(np.array([r[1] for r in recs]))
    gap = np.max(np.diff(np.concatenate([az_all, [az_all[0] + 360]]))) if len(az_all) else np.nan
    ax.text(np.radians(135), 118, "radius = distance (°)\n30/60/90°",
            fontsize=8, ha="center", color="0.3")
    fig.text(0.5, 0.02, f"{n} channels total | "
             f"P={counts.get('P (body)',0)}, SH={counts.get('SH (body)',0)}, "
             f"Rayleigh={counts.get('Rayleigh',0)}, Love={counts.get('Love',0)} | "
             f"primary azimuthal gap ≈ {gap:.0f}°", ha="center", fontsize=9)
    fig.savefig(out, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"stations: {counts} | az gap {gap:.0f} deg -> {out}")
    return out


if __name__ == "__main__":
    plot(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
