"""
rerun_ffm_longdur.py — Re-run the combined WISP finite-fault inversion with a
PHYSICALLY ADEQUATE maximum source duration.

The ffm.2/NP1.big run inherited max_source_dur = int(2.5 * time_shift) =
int(2.5 * 17.5) = 43 s (WISP default heuristic; modelling_parameters.py:47).
That cap is far too short for a ~270 km unilateral rupture whose front needs
~85 s at 2.8 km/s to reach the eastern end, so the inversion piled all eastern
slip onto the 43 s ceiling (rupture "velocities" of 3.7-5.4 km/s, violating
max_vel = 3.5). This script clones the run into a new directory, lifts ONLY the
max_source_dur cap, and re-runs the Fortran inversion + plots. Everything else
(data, geometry, weights) is identical, so the effect is isolated.

Usage: <ff-env python> scripts/rerun_ffm_longdur.py [MAX_DUR]
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
SRC = pathlib.Path(RUN_ROOT) / "ffm.2" / "NP1.big"
DST = pathlib.Path(RUN_ROOT) / "ffm.3" / "NP1.big"
CONFIG = os.path.join(WISP_HOME, "config.ini")
MAX_DUR = int(sys.argv[1]) if len(sys.argv) > 1 else 110
DATA_TYPE = ["body", "surf"]


def lift_cap(d, max_dur):
    """Set max_source_dur to max_dur in annealing.txt (field 4 of line 3) and json."""
    # annealing.txt: line 3 is "0 1e-04 0 <max_source_dur>"
    ap = d / "annealing.txt"
    lines = ap.read_text().splitlines()
    parts = lines[2].split()
    old = parts[-1]
    parts[-1] = str(max_dur)
    lines[2] = " ".join(parts)
    ap.write_text("\n".join(lines) + "\n")
    # annealing_prop.json (record only; Fortran reads the .txt)
    jp = d / "annealing_prop.json"
    j = json.load(open(jp))
    j["max_source_dur"] = max_dur
    json.dump(j, open(jp, "w"), sort_keys=True, indent=4,
              separators=(",", ": "), ensure_ascii=False)
    print(f"max_source_dur: {old} -> {max_dur} s")


def main():
    sys.path.insert(0, os.path.join(WISP_HOME, "src"))
    import ffm.management as mng
    import ffm.modulo_logs as ml
    from ffm.inversion_chen_new import inversion, execute_plot

    if DST.exists():
        shutil.rmtree(DST)
    DST.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(SRC, DST)
    # drop stale outputs from the copy so we know the new ones are fresh
    for f in ("Solution.txt", "modelling_summary.txt"):
        (DST / f).unlink(missing_ok=True)
    print(f"cloned -> {DST}")

    lift_cap(DST, MAX_DUR)

    default_dirs = mng.default_dirs(config_path=CONFIG)
    tensor_info = json.load(open(DST / "tensor_info.json"))
    segments_data = json.load(open(DST / "segments_data.json"))
    velmodel = json.load(open(DST / "velmodel_data.json"))

    logger = ml.create_log("rerun_ffm", str(DST / "logs" / "rerun_ffm.log"))
    logger.info(f"Re-run with max_source_dur={MAX_DUR}")
    inversion(DATA_TYPE, default_dirs, logger, directory=DST)
    execute_plot(tensor_info, DATA_TYPE, segments_data, default_dirs,
                 velmodel=velmodel, directory=DST)
    ml.close_log(logger)
    print(f"DONE -> {DST}/Solution.txt")


if __name__ == "__main__":
    main()
