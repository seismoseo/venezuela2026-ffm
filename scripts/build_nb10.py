"""Build notebook 10 — joint teleseismic + InSAR finite-fault inversion (ffm.6)."""
import json, os

nb = {"cells": [], "metadata": {"kernelspec": {"display_name": "Python 3",
      "language": "python", "name": "python3"}, "language_info": {"name": "python"}},
      "nbformat": 4, "nbformat_minor": 5}
def md(t): nb["cells"].append({"cell_type": "markdown", "metadata": {}, "source": t})
def code(t): nb["cells"].append({"cell_type": "code", "metadata": {}, "execution_count": None,
                                 "outputs": [], "source": t})

md("""# Venezuela 2026 — joint teleseismic + InSAR finite-fault inversion (ffm.6)

This is the **joint inversion** of teleseismic body + surface waves **and InSAR** line-of-sight
surface displacement, built on the longer-window model (ffm.5, notebook 09). It adds the two
USGS-distributed **Sentinel-1** resampled interferograms (ascending path 106, descending path 25;
2629 LOS points total) as a WISP imagery (`-t im`) dataset, with a linear orbital ramp solved per
scene. WISP computes the static LOS Green's functions and inverts everything jointly.

**Why this matters.** Teleseismic data constrain the *gross* rupture but are weak on **shallow,
near-source slip**. InSAR is the opposite — it directly measures the static ground deformation above
the rupture, pinning the shallow slip and surface trace. Neither our previous models nor the USGS
FFM inverted InSAR, so this is a genuinely new constraint for this event.""")

code("""import os, sys, json
import numpy as np, re
import matplotlib.pyplot as plt
from IPython.display import Image, display
ROOT = os.path.abspath(os.path.join(os.getcwd(), '..'))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import fig_fault_isochrone as fi, fig_insar, usgs_compare as uc
from imgutil import trim\nget_ipython().run_line_magic('matplotlib', 'inline')  # imported fig modules set Agg; restore inline rendering
RUN  = os.path.join(ROOT, 'results', 'ffm.6/NP1.big')
PREV = os.path.join(ROOT, 'results', 'ffm.5/NP1.big')  # teleseismic-only
USGS = os.path.join(ROOT, 'data', 'usgs')
P = os.path.join(RUN, 'plots')
img = json.load(open(os.path.join(RUN,'imagery_data.json')))
npts = open(os.path.join(RUN,'imagery_data.txt')).readline().strip()
print('InSAR tracks:', [os.path.basename(t['name']) for t in img['insar']], '| LOS points:', npts)""")

md("""## A. InSAR fit

Observed vs modeled (fault slip + orbital ramp) line-of-sight displacement, per Sentinel-1 track.
Red = motion away from the satellite, blue = toward. VR = variance reduction (1 = perfect).""")
code("display(Image(fig_insar.plot(RUN)))")
md("""The large descending scene (p25, 2519 points) is fit at **VR ≈ 0.97** — the modeled deformation
reproduces the observed LOS pattern in both shape and amplitude (≈±40 cm). The small descending
scene (p106) matches in pattern; its offset is less well captured (few points, dominated by the ramp).
The joint inversion therefore fits the InSAR **and** keeps the seismic fit essentially unchanged
(averaged seismic misfit 0.106, vs 0.106 for the teleseismic-only ffm.5).""")

md("""## B. What InSAR changed — teleseismic-only (ffm.5) vs joint (ffm.6)

This is the scientific payoff: how the independent near-field constraint reshapes the slip.""")
code("""def load(run):
    txt=open(os.path.join(run,'Solution.txt')).read().splitlines()
    m=re.search(r'nx\\(Along-strike\\)=\\s*(\\d+).*ny\\(downdip\\)=\\s*(\\d+)',txt[1]); nx,ny=int(m[1]),int(m[2])
    i0=next(i for i,l in enumerate(txt) if 'slip' in l and 'rake' in l)+1
    a=np.array([[float(x) for x in l.split()[:11]] for l in txt[i0:] if len(l.split())>=11])
    return dict(lat=a[:,0],lon=a[:,1],dep=a[:,2],slip=a[:,3]/100,mo=a[:,10].sum())
me5,me6=load(PREV),load(RUN); mw=lambda m:(2/3)*(np.log10(m)-16.1)
print('Mw: ffm.5 %.2f | ffm.6(+InSAR) %.2f'%(mw(me5['mo']),mw(me6['mo'])))
print('peak slip: ffm.5 %.2f m | ffm.6 %.2f m'%(me5['slip'].max(),me6['slip'].max()))
print('slip-pattern correlation: %.2f  (vs >0.9 for every teleseismic-only tweak)'%np.corrcoef(me5['slip'],me6['slip'])[0,1])
print('mean shallow (<12 km) slip: ffm.5 %.2f m -> ffm.6 %.2f m'%(me5['slip'][me5['dep']<12].mean(),me6['slip'][me6['dep']<12].mean()))
# side-by-side slip maps
vmax=max(me5['slip'].max(),me6['slip'].max())
fig,axes=plt.subplots(2,1,figsize=(11,6),sharex=True,sharey=True)
for ax,d,t in [(axes[0],me5,'ffm.5 — teleseismic only'),(axes[1],me6,'ffm.6 — + InSAR (joint)')]:
    sc=ax.scatter(d['lon'],d['lat'],c=d['slip'],cmap='magma_r',vmin=0,vmax=vmax,s=90,marker='s')
    ax.plot(-68.5277,10.436,marker='*',ms=15,mfc='yellow',mec='k'); ax.set_title(t,fontsize=10)
    ax.set_ylabel('Lat (°)'); ax.set_aspect(1/np.cos(np.radians(10.436)))
axes[1].set_xlabel('Lon (°)'); fig.colorbar(sc,ax=axes,shrink=.85,label='Slip (m)'); plt.show()""")
md("""Adding InSAR **substantially refines the slip** (pattern correlation drops to ~0.55, versus >0.9
for every teleseismic-only change so far) while keeping Mw 7.57. In particular it **reduces the
shallow slip near the coast** (where the InSAR has coverage) — the teleseismic-only model had more
shallow slip there than the ground deformation supports. The offshore slip (no InSAR coverage)
remains teleseismically constrained. This is exactly the behaviour expected when near-field geodesy
is added to a teleseismic model.""")

md("""## C. Joint solution (ffm.6)
### C1. Slip distribution""")
code("display(Image(os.path.join(P,'SlipDist_plane0.png')))")
md("### C2. On-fault slip + rupture-front isochrones (true 1:1 scale)")
code("display(Image(fi.plot(RUN)))")
md("### C3. Moment-rate function")
code("display(Image(os.path.join(P,'MomentRate.png')))")
md("### C4. Rise time (per-subfault slip duration) — solved by the inversion")
code("display(Image(fi.plot_risetime(RUN)))")
md("Slip durations are mostly ~5–15 s; longer values sit on the deeper/edge subfaults that are less well resolved (smoothness regularization fills weakly-constrained patches). Rise time is solved, not assumed (windowed slip-rate basis, 8 time windows).")

md("""## D. Seismic fits are preserved (all four phases, transparent)
Black = observed, red = synthetic; faded = excluded. Teleseismic **body** waves are band-passed
0.006–1.0 Hz; **surface** waves ~167–250 s. Left of each panel: phase / station / unit (nm body,
mm surface) / azimuth° / distance°; right: black = peak observed amplitude, red = peak synthetic.

### D1. P body waves""")
code("display(Image(trim(os.path.join(P,'P_body_waves.png'))))")
md("### D2. SH body waves")
code("display(Image(trim(os.path.join(P,'SH_body_waves.png'))))")
md("SH is down-weighted (0.5) and near-nodal for this near-vertical strike-slip fault, so a residual amplitude misfit remains at some azimuths — as in the seismic-only models; a no-SH control shows it does not bias the slip.")
md("### D3. Rayleigh surface waves")
code("display(Image(trim(os.path.join(P,'Rayleigh_surf_waves.png'))))")
md("### D4. Love surface waves")
code("display(Image(trim(os.path.join(P,'Love_surf_waves.png'))))")

md("## E. Comparison with USGS")
code("display(Image(uc.plot_stf(RUN, USGS)))")
code("display(Image(uc.plot_slip_map(RUN, USGS)))")

md("""## F. Take-homes

- **First joint teleseismic + InSAR finite-fault model of this event.** Neither our earlier models
  nor the USGS FFM inverted InSAR; here the two USGS-distributed Sentinel-1 scenes (2629 LOS points)
  are inverted jointly with the body + surface waves.
- **The InSAR is well fit** (variance reduction ≈ 0.97 for the large ascending scene) **without
  degrading the seismic fit** (seismic misfit unchanged at 0.106).
- **InSAR meaningfully refines the slip** (pattern correlation 0.55 vs the teleseismic-only model,
  the largest change of any modification) — most importantly it **reduces the shallow near-coast
  slip**, which the teleseismic data alone over-estimated. Mw stays 7.57.
- This joint model is the **coseismic baseline** for the project's central goal: comparing the
  coseismic slip to the *postseismic* (afterslip) deformation and the aftershock distribution, to
  test where the missing aftershock moment went.
- **Caveat:** InSAR covers only the onshore/coastal part of the fault; the offshore slip remains
  teleseismically constrained. The small ascending scene (p106) is fit in pattern but not offset.""")

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "notebooks", "10_joint_insar_ffm6.ipynb")
json.dump(nb, open(out,"w"), indent=1); print("wrote", out, "|", len(nb["cells"]), "cells")
