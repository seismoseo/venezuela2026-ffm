"""
rerun_ffm_insar_joint.py — Joint inversion of teleseismic body + surface waves
+ InSAR (Sentinel-1 LOS), building on ffm.5 (the longer-body-window model).

Adds the two USGS-distributed resampled Sentinel-1 interferograms (paths 106 & 25)
as a WISP imagery (-t im) dataset. WISP computes the static LOS Green's functions
(gf_static_f95 'imagery') during gf_retrieve, then inverts body+surf+imagery jointly.
A linear orbital ramp is solved per scene.

Usage: <ff-env python> scripts/rerun_ffm_insar_joint.py
"""
# NOTE: provenance script — requires WISP (neic-finitefault), NOT included here.
# Set WISP_HOME, FFM_RUN_ROOT (dir with base WISP run), and USGS_DIR before running.
import json, os, pathlib, shutil, sys

SRC = pathlib.Path(os.environ.get("FFM_RUN_ROOT", os.path.expanduser("~/venezuela_ffm_runs"))) / "ffm.5" / "NP1.big"
DST = pathlib.Path(os.environ.get("FFM_RUN_ROOT", os.path.expanduser("~/venezuela_ffm_runs"))) / "ffm.6" / "NP1.big"
USGS = os.environ.get("USGS_DIR", os.path.expanduser("~/USGS"))
CONFIG = os.path.join(os.environ.get("WISP_HOME", os.path.expanduser("~/neic-finitefault")), "config.ini")
DATA_TYPE = ["body", "surf", "imagery"]


def main():
    sys.path.insert(0, os.path.join(os.environ.get("WISP_HOME", os.path.expanduser("~/neic-finitefault")), "src"))
    import ffm.management as mng
    import ffm.modulo_logs as ml
    from ffm.input_files import input_chen_imagery
    from ffm.inversion_chen_new import inversion, execute_plot

    if DST.exists():
        shutil.rmtree(DST)
    DST.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(SRC, DST)
    for f in ("Solution.txt", "modelling_summary.txt"):
        (DST / f).unlink(missing_ok=True)
    print(f"cloned ffm.5 -> {DST}")

    # 1) stage the two Sentinel-1 tracks inside the run dir (unzip)
    insar = DST / "insar"; insar.mkdir(exist_ok=True)
    import zipfile
    with zipfile.ZipFile(os.path.join(USGS, "resampled_interferograms.zip")) as z:
        z.extractall(insar)
    tracks = sorted(str(p) for p in insar.glob("*_resampled.txt"))
    print(f"InSAR tracks staged: {[os.path.basename(t) for t in tracks]}")

    # 2) imagery_data.json (linear orbital ramp solved per scene)
    img = {"insar": [{"name": t, "weight": 1.0, "ramp": "linear"} for t in tracks]}
    json.dump(img, open(DST / "imagery_data.json", "w"), indent=2)
    input_chen_imagery(directory=DST)
    npts = open(DST / "imagery_data.txt").readline().strip()
    print(f"imagery_data.txt: {npts} LOS points")

    # 3) joint inversion (gf_retrieve computes the static InSAR GF for 'imagery')
    default_dirs = mng.default_dirs(config_path=CONFIG)
    tensor_info = json.load(open(DST / "tensor_info.json"))
    segments_data = json.load(open(DST / "segments_data.json"))
    velmodel = json.load(open(DST / "velmodel_data.json"))
    logger = ml.create_log("rerun_insar", str(DST / "logs" / "rerun_insar.log"))
    logger.info("Joint body+surf+InSAR inversion")
    inversion(DATA_TYPE, default_dirs, logger, directory=DST)
    execute_plot(tensor_info, DATA_TYPE, segments_data, default_dirs,
                 velmodel=velmodel, directory=DST)
    ml.close_log(logger)
    print(f"DONE -> {DST}/Solution.txt")


if __name__ == "__main__":
    main()
