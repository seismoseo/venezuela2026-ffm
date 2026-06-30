"""
rerun_ffm_exclude_rayleigh.py — Re-run the corrected combined inversion (ffm.3)
with the three poorly-fit Rayleigh stations (EFI, HRV, PKME) EXCLUDED, i.e.
trace_weight = 0, so they no longer constrain the slip model. Everything else
(110 s cap, geometry, all other traces) is identical to ffm.3. The Love (BHT)
components of those stations are kept.

This is a robustness check: if the slip model is data-driven and not controlled
by a few traces, removing 3 of 120 should leave it essentially unchanged.

Usage: <ff-env python> scripts/rerun_ffm_exclude_rayleigh.py
"""
# NOTE: provenance script — requires WISP (neic-finitefault), NOT included here.
# Set WISP_HOME (WISP install dir) and FFM_RUN_ROOT (dir holding the base WISP run)
# for your environment before running. See README -> "Reproducing the inversion".
import json
import os
import pathlib
import shutil
import sys

WISP_HOME = os.environ.get("WISP_HOME", os.path.expanduser("~/neic-finitefault"))
RUN_ROOT = os.environ.get("FFM_RUN_ROOT", os.path.expanduser("~/venezuela_ffm_runs"))
SRC = pathlib.Path(RUN_ROOT) / "ffm.3" / "NP1.big"
DST = pathlib.Path(RUN_ROOT) / "ffm.4" / "NP1.big"
CONFIG = os.path.join(WISP_HOME, "config.ini")
EXCLUDE = {"EFI", "HRV", "PKME"}   # Rayleigh (BHZ) only
DATA_TYPE = ["body", "surf"]


def zero_rayleigh(d):
    """Set weight columns to 0 for the excluded stations' BHZ rows in
    channels_surf.txt (what the Fortran reads), and in surf_waves.json (plotting)."""
    # channels_surf.txt: columns ... Io_s Weight Weight Weight <flag>; BHZ row has H1/V flags
    cs = d / "channels_surf.txt"
    out = []
    n = 0
    for line in cs.read_text().splitlines():
        p = line.split()
        # data rows: index, STA, lat, lon, ... ; STA in field 1; BHZ rows have "1 0 0" after M
        if len(p) >= 13 and p[1] in EXCLUDE:
            # M V H1 H2 = p[4..7]; V(vertical)=1 marks the BHZ (Rayleigh) trace
            if p[5] == "1":
                # the three weight columns are the 3 values before the trailing flag
                p[-4], p[-3], p[-2] = "0.00", "0.00", "0.00"
                line = "    ".join(p)
                n += 1
        out.append(line)
    cs.write_text("\n".join(out) + "\n")
    print(f"channels_surf.txt: zeroed {n} Rayleigh (BHZ) rows for {sorted(EXCLUDE)}")
    # json (for figure fading / custom gray)
    sj = d / "surf_waves.json"
    js = json.load(open(sj))
    m = 0
    for x in js:
        if x["name"] in EXCLUDE and x["component"] == "BHZ":
            x["trace_weight"] = 0.0
            m += 1
    json.dump(js, open(sj, "w"))
    print(f"surf_waves.json: trace_weight=0 on {m} Rayleigh traces")


def main():
    sys.path.insert(0, os.path.join(WISP_HOME, "src"))
    import ffm.management as mng
    import ffm.modulo_logs as ml
    from ffm.inversion_chen_new import inversion, execute_plot

    if DST.exists():
        shutil.rmtree(DST)
    DST.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(SRC, DST)
    for f in ("Solution.txt", "modelling_summary.txt"):
        (DST / f).unlink(missing_ok=True)
    print(f"cloned ffm.3 -> {DST}")

    zero_rayleigh(DST)

    default_dirs = mng.default_dirs(config_path=CONFIG)
    tensor_info = json.load(open(DST / "tensor_info.json"))
    segments_data = json.load(open(DST / "segments_data.json"))
    velmodel = json.load(open(DST / "velmodel_data.json"))

    logger = ml.create_log("rerun_excl", str(DST / "logs" / "rerun_excl.log"))
    logger.info("Re-run ffm.3 with EFI/HRV/PKME Rayleigh excluded")
    inversion(DATA_TYPE, default_dirs, logger, directory=DST)
    execute_plot(tensor_info, DATA_TYPE, segments_data, default_dirs,
                 velmodel=velmodel, directory=DST)
    ml.close_log(logger)
    print(f"DONE -> {DST}/Solution.txt")


if __name__ == "__main__":
    main()
