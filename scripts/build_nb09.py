"""Build notebook 09 — longer body-wave window model (ffm.5) and the window-length effect."""
import json, os

nb = {"cells": [], "metadata": {"kernelspec": {"display_name": "Python 3",
      "language": "python", "name": "python3"}, "language_info": {"name": "python"}},
      "nbformat": 4, "nbformat_minor": 5}
def md(t): nb["cells"].append({"cell_type": "markdown", "metadata": {}, "source": t})
def code(t): nb["cells"].append({"cell_type": "code", "metadata": {}, "execution_count": None,
                                 "outputs": [], "source": t})

md("""# Venezuela 2026 — longer teleseismic window model (ffm.5)

This run repeats the combined inversion of notebook 07 (**ffm.4**) but with a **longer
teleseismic body-wave window — 100 s instead of 70 s** — matching the window length used by
USGS. Everything else (fault geometry, surface waves, the three excluded Rayleigh stations, the
110 s `max_source_dur`) is identical to ffm.4.

**Why.** WISP's default body window is `1.5 × 2 × (time_shift + depth/3.5) ≈ 70 s`. But the
*apparent* P-wave duration at a teleseismic station is the rupture duration modified by directivity
(~77–107 s here for a ~95 s rupture), so a 70 s window truncates the late-arriving energy from the
eastern (late) part of the rupture. The processed records are 480 s long, so we simply re-cut a 100 s
window and re-ran. This tests whether the late/eastern rupture — previously constrained mostly by the
long-period surface waves — is pinned down better when the body waves can also see it.""")

code("""import os, sys, json
import numpy as np, re
import pandas as pd
from IPython.display import Image, display
ROOT = os.path.abspath(os.path.join(os.getcwd(), '..'))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import fig_fault_isochrone as fi, fig_station_geometry as fsg, usgs_compare as uc
from imgutil import trim\nget_ipython().run_line_magic('matplotlib', 'inline')  # imported fig modules set Agg; restore inline rendering

RUN  = os.path.join(ROOT, 'results', 'ffm.5/NP1.big')
PREV = os.path.join(ROOT, 'results', 'ffm.4/NP1.big')
USGS = os.path.join(ROOT, 'data', 'usgs')
P = os.path.join(RUN, 'plots')
print('ffm.5 body window:', json.load(open(os.path.join(RUN,'tele_waves.json')))[0]['duration'],
      'samples x 0.2 s =', json.load(open(os.path.join(RUN,'tele_waves.json')))[0]['duration']*0.2, 's')""")

md("""## A. The window-length effect — moment-rate function

Overlaying the source-time functions of the 70 s window (ffm.4), the 100 s window (ffm.5), and USGS.""")
code("""import matplotlib.pyplot as plt
fi._helvetica() if hasattr(fi,'_helvetica') else None
t4,m4 = uc.parse_mr(os.path.join(PREV,'STF.txt'))
t5,m5 = uc.parse_mr(os.path.join(RUN,'STF.txt'))
tu,mu = uc.parse_mr(os.path.join(USGS,'moment_rate.mr'))
fig,ax=plt.subplots(figsize=(9,4.2))
ax.fill_between(tu,mu/1e19,color='0.8',label='USGS NEIC')
ax.plot(t4,m4/1e19,color='#2980b9',lw=1.6,ls='--',label='ffm.4 (70 s window)')
ax.plot(t5,m5/1e19,color='#c0392b',lw=1.9,label='ffm.5 (100 s window)')
ax.set_xlim(0,140); ax.set_ylim(bottom=0)
ax.set_xlabel('Time after origin (s)'); ax.set_ylabel(r'Moment rate ($\\times10^{19}$ Nm/s)')
ax.set_title('Source-time function vs body-wave window length'); ax.legend(framealpha=1,edgecolor='0.5')
fig.tight_layout(); plt.show()
def dur(t,m): return float(t[m>0.02*m.max()].max())
print('duration: ffm.4 (70s win) ~%.0f s | ffm.5 (100s win) ~%.0f s | USGS ~%.0f s'%(dur(t4,m4),dur(t5,m5),dur(tu,mu)))""")
md("""The longer window **shortens the over-extended tail** of the 70 s model (~115 s → ~97 s),
bringing the rupture duration into close agreement with USGS (~94 s). With the body waves now able to
"see" the late eastern rupture, its timing is pulled in rather than left loosely extended by the
surface waves alone.""")

md("### Robustness — the slip model is otherwise unchanged")
code("""def load(run):
    txt=open(os.path.join(run,'Solution.txt')).read().splitlines()
    m=re.search(r'nx\\(Along-strike\\)=\\s*(\\d+).*ny\\(downdip\\)=\\s*(\\d+)',txt[1]); nx,ny=int(m[1]),int(m[2])
    i0=next(i for i,l in enumerate(txt) if 'slip' in l and 'rake' in l)+1
    a=np.array([[float(x) for x in l.split()[:11]] for l in txt[i0:] if len(l.split())>=11])
    return (a[:,3]/100).reshape(ny,nx), a[:,10].sum()
s4,mo4=load(PREV); s5,mo5=load(RUN); mw=lambda m:(2/3)*(np.log10(m)-16.1)
print('                  ffm.4 (70s)   ffm.5 (100s)')
print('Mw                %6.2f       %6.2f'%(mw(mo4),mw(mo5)))
print('peak slip (m)     %6.2f       %6.2f'%(s4.max(),s5.max()))
print('slip-pattern correlation (ffm.4 vs ffm.5): %.3f'%np.corrcoef(s4.ravel(),s5.ravel())[0,1])""")
md("Same Mw (7.57) and slip pattern (correlation 0.92); peak slip relaxes slightly as the moment spreads over the better-resolved duration. So the longer window **refines the timing without changing the gross rupture**.")

md("""## B. Solution (ffm.5)
### B1. Slip distribution""")
code("display(Image(os.path.join(P,'SlipDist_plane0.png')))")
md("### B2. On-fault slip + rupture-front isochrones (true 1:1 scale)")
code("display(Image(fi.plot(RUN)))")
md("### B3. Rise time (per-subfault slip duration)")
code("display(Image(fi.plot_risetime(RUN)))")
md("### B4. Moment-rate function")
code("display(Image(os.path.join(P,'MomentRate.png')))")

md("""## C. Waveform fits over the 100 s window
Black = observed, red = synthetic; faded = excluded. Body band 0.006–1.0 Hz; surface ~167–250 s.
The body panels now extend to ~100 s after the phase arrival.""")
code("display(Image(trim(os.path.join(P,'P_body_waves.png'))))")
code("display(Image(trim(os.path.join(P,'SH_body_waves.png'))))")
code("display(Image(trim(os.path.join(P,'Rayleigh_surf_waves.png'))))")
code("display(Image(trim(os.path.join(P,'Love_surf_waves.png'))))")

md("## D. Comparison with USGS (now with matched window length)")
code("display(Image(uc.plot_stf(RUN, USGS)))")
code("display(Image(uc.plot_slip_map(RUN, USGS)))")
md("""## E. Take-homes

- **Lengthening the teleseismic body window 70 → 100 s (matching USGS) measurably improved the
  rupture-duration constraint:** the over-long tail of the 70 s model (~115 s) shortened to ~97 s,
  in close agreement with USGS (~94 s).
- **The gross rupture is unchanged** (Mw 7.57, slip-pattern correlation 0.92): the longer window
  refines *timing*, not the slip pattern — exactly what one expects when the late rupture moves from
  surface-wave-only control to body+surface control.
- **ffm.5 is the best-constrained teleseismic model** so far and is the basis for the InSAR joint
  inversion (notebook 10).""")

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "notebooks", "09_longwindow_ffm5.ipynb")
json.dump(nb, open(out,"w"), indent=1); print("wrote", out, "|", len(nb["cells"]), "cells")
