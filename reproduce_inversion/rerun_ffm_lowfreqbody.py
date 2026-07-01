"""
rerun_ffm_lowfreqbody.py — Test the effect of the teleseismic body-wave frequency
band on the P/SH fits (and on model resolution), building on ffm.5 (seismic-only,
100 s window).

WISP fits body waves in the wavelet domain over scales 1-8 (scale 1 = highest
frequency). ffm.5 uses P: scales 2-8, SH: scales 2-7. Here we turn OFF the two
highest active scales (2 and 3), i.e. restrict the body-wave misfit to LONGER
periods (high-cut ~0.3 Hz instead of ~0.6-1.0 Hz). This is applied identically to
the observed and the Green's functions via wavelets_body.txt, so it is a clean band
change. Surface waves and geometry are unchanged.

Usage: <ff-env python> scripts/rerun_ffm_lowfreqbody.py
"""
# NOTE: provenance script — requires WISP. Set WISP_HOME, FFM_RUN_ROOT.
import json, os, pathlib, shutil, sys

SRC = pathlib.Path(os.environ.get("FFM_RUN_ROOT", os.path.expanduser("~/venezuela_ffm_runs"))) / "ffm.5" / "NP1.big"
DST = pathlib.Path(os.environ.get("FFM_RUN_ROOT", os.path.expanduser("~/venezuela_ffm_runs"))) / "ffm.7" / "NP1.big"
CONFIG = os.path.join(os.environ.get("WISP_HOME", os.path.expanduser("~/neic-finitefault")), "config.ini")
DATA_TYPE = ["body", "surf"]
# new wavelet-scale weights (scales 1..8; 1=highest freq). Drop scales 2-3.
P_W  = "0 0 0 1 1 1 1 1"   # P: scales 4-8  (~<0.3 Hz)
SH_W = "0 0 0 1 1 1 1 0"   # SH: scales 4-7


def edit_wavelets(path):
    """Rewrite the weight line (2nd line after each 'STA BHZ/BHT') in wavelets_body.txt."""
    lines = path.read_text().splitlines()
    out, i, npz, nsh = [], 0, 0, 0
    while i < len(lines):
        out.append(lines[i])
        parts = lines[i].split()
        if len(parts) == 2 and parts[1] in ("BHZ", "BHT"):
            out.append(lines[i + 1])                      # the "3 3 3 ..." type line
            new = P_W if parts[1] == "BHZ" else SH_W      # replace the weight line
            out.append(new)
            if parts[1] == "BHZ": npz += 1
            else: nsh += 1
            i += 3
        else:
            i += 1
    path.write_text("\n".join(out) + "\n")
    print(f"rewrote wavelet weights: {npz} P (->{P_W}), {nsh} SH (->{SH_W})")


def main():
    sys.path.insert(0, os.path.join(os.environ.get("WISP_HOME", os.path.expanduser("~/neic-finitefault")), "src"))
    import ffm.management as mng
    import ffm.modulo_logs as ml
    from ffm.inversion_chen_new import inversion, execute_plot

    if DST.exists():
        shutil.rmtree(DST)
    DST.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(SRC, DST)
    for f in ("Solution.txt", "modelling_summary.txt"):
        (DST / f).unlink(missing_ok=True)
    print(f"cloned ffm.5 -> {DST}")

    edit_wavelets(DST / "wavelets_body.txt")

    default_dirs = mng.default_dirs(config_path=CONFIG)
    tensor_info = json.load(open(DST / "tensor_info.json"))
    segments_data = json.load(open(DST / "segments_data.json"))
    velmodel = json.load(open(DST / "velmodel_data.json"))
    logger = ml.create_log("rerun_lowfreq", str(DST / "logs" / "rerun_lowfreq.log"))
    logger.info("Re-run with long-period body band (scales 4-8/4-7)")
    inversion(DATA_TYPE, default_dirs, logger, directory=DST)
    execute_plot(tensor_info, DATA_TYPE, segments_data, default_dirs,
                 velmodel=velmodel, directory=DST)
    ml.close_log(logger)
    print(f"DONE -> {DST}/Solution.txt")


if __name__ == "__main__":
    main()
