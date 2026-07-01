"""
rerun_ffm_longwindow.py — Re-run the combined inversion (ffm.4) with a LONGER
teleseismic body-wave window (~100 s, like USGS), to test whether the late/eastern
rupture is better constrained.

WISP's default body window = duration_tele_waves() = 1.5 * 2*(time_shift + depth/3.5)
= ~70 s here. The processed SAC are ~480 s long, so we can re-cut a longer window:
set duration -> 500 samples (100 s at dt 0.2) in tele_waves.json and regenerate the
body input files (channels_body, waveforms_body, wavelets_body) via WISP's own
input_chen_tele_body. Surface waves, geometry, Rayleigh exclusions, and the 110 s
max_source_dur are all inherited unchanged from ffm.4.

Usage: <ff-env python> scripts/rerun_ffm_longwindow.py [NEW_DURATION_SAMPLES]
"""
# NOTE: provenance script — requires WISP (neic-finitefault), NOT included here.
# Set WISP_HOME, FFM_RUN_ROOT (dir with base WISP run), and USGS_DIR before running.
import json, os, pathlib, shutil, sys

SRC = pathlib.Path(os.environ.get("FFM_RUN_ROOT", os.path.expanduser("~/venezuela_ffm_runs"))) / "ffm.4" / "NP1.big"
DST = pathlib.Path(os.environ.get("FFM_RUN_ROOT", os.path.expanduser("~/venezuela_ffm_runs"))) / "ffm.5" / "NP1.big"
CONFIG = os.path.join(os.environ.get("WISP_HOME", os.path.expanduser("~/neic-finitefault")), "config.ini")
NEW_DUR = int(sys.argv[1]) if len(sys.argv) > 1 else 500   # samples; 500*0.2 = 100 s
DATA_TYPE = ["body", "surf"]


def main():
    sys.path.insert(0, os.path.join(os.environ.get("WISP_HOME", os.path.expanduser("~/neic-finitefault")), "src"))
    import ffm.management as mng
    import ffm.modulo_logs as ml
    from ffm.input_files import input_chen_tele_body
    from ffm.inversion_chen_new import inversion, execute_plot

    if DST.exists():
        shutil.rmtree(DST)
    DST.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(SRC, DST)
    for f in ("Solution.txt", "modelling_summary.txt"):
        (DST / f).unlink(missing_ok=True)
    print(f"cloned ffm.4 -> {DST}")

    # 1) lengthen the body-wave window in tele_waves.json
    tw = json.load(open(DST / "tele_waves.json"))
    old = tw[0]["duration"]
    for t in tw:
        t["duration"] = NEW_DUR
    json.dump(tw, open(DST / "tele_waves.json", "w"), indent=4, sort_keys=True)
    print(f"body window: {old} -> {NEW_DUR} samples ({NEW_DUR*0.2:.0f} s); {len(tw)} traces")

    # 2) regenerate body input files (re-cuts observed from the 480 s processed SAC)
    tensor_info = json.load(open(DST / "tensor_info.json"))
    data_prop = json.load(open(DST / "sampling_filter.json"))
    input_chen_tele_body(tensor_info, data_prop, directory=DST)
    print("regenerated channels_body / waveforms_body / wavelets_body")

    # 3) re-run inversion + plot (surf inputs, Rayleigh exclusions, 110 s cap inherited)
    default_dirs = mng.default_dirs(config_path=CONFIG)
    segments_data = json.load(open(DST / "segments_data.json"))
    velmodel = json.load(open(DST / "velmodel_data.json"))
    logger = ml.create_log("rerun_longwin", str(DST / "logs" / "rerun_longwin.log"))
    logger.info(f"Re-run with body window {NEW_DUR} samples")
    inversion(DATA_TYPE, default_dirs, logger, directory=DST)
    execute_plot(tensor_info, DATA_TYPE, segments_data, default_dirs,
                 velmodel=velmodel, directory=DST)
    ml.close_log(logger)
    print(f"DONE -> {DST}/Solution.txt")


if __name__ == "__main__":
    main()
