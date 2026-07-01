"""
fig_insar.py — InSAR observed vs modeled line-of-sight (LOS) fit for the joint
WISP inversion. Reads imagery_data.txt (observed), imagery_synthetics.txt (fault
deformation), imagery_ramp.txt (orbital ramp); model = synthetic + ramp. Makes,
per Sentinel-1 track, observed / modeled / residual scatter maps on a common scale.

Usage: python scripts/fig_insar.py <NP_dir> [out.png]
"""
import os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def _helvetica():
    from matplotlib import font_manager
    for n in ("Helvetica", "Arial", "Nimbus Sans"):
        if any(n in f.name for f in font_manager.fontManager.ttflist):
            matplotlib.rcParams["font.family"] = n; break


def _col(path, c):
    return np.array([float(l.split()[c]) for l in open(path).read().splitlines()[1:]
                     if len(l.split()) >= c + 1])


def plot(np_dir, out=None):
    _helvetica()
    out = out or os.path.join(np_dir, "plots", "InSAR_fit.png")
    lat = _col(os.path.join(np_dir, "imagery_data.txt"), 2)
    lon = _col(os.path.join(np_dir, "imagery_data.txt"), 3)
    obs = _col(os.path.join(np_dir, "imagery_data.txt"), 4)
    syn = _col(os.path.join(np_dir, "imagery_synthetics.txt"), 4)
    ramp = _col(os.path.join(np_dir, "imagery_ramp.txt"), 4)
    model = syn + ramp
    # track sizes from imagery_weights.txt (lines after the count)
    wl = open(os.path.join(np_dir, "imagery_weights.txt")).read().splitlines()
    sizes = [int(l.split()[0]) for l in wl[1:] if l.split()]
    bounds = np.cumsum([0] + sizes)
    names = ["p106 (S1)", "p25 (S1)"][:len(sizes)] or [f"track{i}" for i in range(len(sizes))]

    vlim = np.percentile(np.abs(obs), 98)
    ntr = len(sizes)
    fig, axes = plt.subplots(ntr, 3, figsize=(13, 3.6 * ntr), squeeze=False)
    for k in range(ntr):
        sl = slice(bounds[k], bounds[k + 1])
        o, m = obs[sl], model[sl]
        vr = 1 - np.sum((o - m) ** 2) / np.sum(o ** 2)
        for j, (val, ttl) in enumerate([(o, "Observed LOS"), (m, "Modeled (slip+ramp)"),
                                        (o - m, "Residual")]):
            ax = axes[k][j]
            cmap = "RdBu_r"
            sc = ax.scatter(lon[sl], lat[sl], c=val, s=10, cmap=cmap, vmin=-vlim, vmax=vlim)
            ax.set_aspect(1.0 / np.cos(np.radians(np.mean(lat[sl]))))
            ax.set_title(f"{names[k]} — {ttl}" + (f"  (VR={vr:.2f})" if j == 1 else ""),
                         fontsize=9)
            if j == 0:
                ax.set_ylabel("Lat (°)")
            ax.set_xlabel("Lon (°)")
        cb = fig.colorbar(sc, ax=axes[k].tolist(), shrink=0.8, pad=0.02)
        cb.set_label("LOS (cm)")
    fig.suptitle("InSAR line-of-sight fit — joint body+surface+InSAR inversion", fontsize=12)
    fig.savefig(out, dpi=170, bbox_inches="tight"); plt.close(fig)
    vr_all = 1 - np.sum((obs - model) ** 2) / np.sum(obs ** 2)
    print(f"InSAR fit: overall VR={vr_all:.3f}, {len(obs)} points, {ntr} tracks -> {out}")
    return out


if __name__ == "__main__":
    plot(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
