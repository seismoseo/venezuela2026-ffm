# Reading list — the WISP finite-fault inversion strategy

WISP (`neic-finitefault`, the USGS NEIC finite-fault code) implements the **Chen Ji
wavelet-domain, simulated-annealing kinematic finite-fault** method. To understand what it does and
why, in roughly the order to read:

## Core method (read these first)

1. **Ji, C., D. J. Wald, & D. V. Helmberger (2002a).** *Source description of the 1999 Hector Mine,
   California, earthquake, Part I: Wavelet domain inversion theory and resolution analysis.*
   **BSSA 92(4), 1192–1207.**
   → **The** paper for WISP. Introduces fitting waveforms in the **wavelet domain** (so different
   frequency bands / arrival times are weighted separately) and the **simulated-annealing** search.
   Explains the resolution analysis — directly relevant to the frequency-band experiment (nb12).

2. **Ji, C., D. J. Wald, & D. V. Helmberger (2002b).** *… Part II: Complexity of slip history.*
   **BSSA 92(4), 1208–1226.**
   → The application companion: how slip amplitude, rake, rupture time, and rise time are
   parameterized and interpreted — the quantities in our `Solution.txt`.

3. **Hartzell, S. H., & T. H. Heaton (1983).** *Inversion of strong motion and teleseismic waveform
   data for the fault rupture history of the 1979 Imperial Valley earthquake.* **BSSA 73, 1553–1583.**
   → The classic **multi-time-window linear finite-fault** framework that everything since builds on;
   read for the fundamentals (Green's functions × slip, time windows, positivity/smoothing).

## Green's functions

4. **Zhu, L., & L. A. Rivera (2002).** *A note on the dynamic and static displacements from a point
   source in multilayered media.* **GJI 148, 619–627.**
   → The **`fk` method** WISP uses to compute layered-Earth Green's functions (both the seismic and
   the static/InSAR responses).

5. **Kikuchi, M., & H. Kanamori (1991).** *Inversion of complex body waves — III.*
   **BSSA 81, 2335–2350.**
   → Foundations of **teleseismic body-wave** source inversion (deconvolution, depth phases) —
   background for the P/SH modeling.

## Joint teleseismic + geodetic/regional (most relevant to this repo)

6. **Goldberg, D. E., P. Koch, D. Melgar, S. Riquelme, W. L. Yeck, & W. D. Barnhart (2022).**
   *Limitations of a teleseismic-only dataset for the 2021 Mw 7.2 Nippes, Haiti, finite-fault
   modeling: improved modeling capability for joint teleseismic and regional inversion.*
   (SSA Annual Meeting 2022; and related USGS NEIC work.)
   → The **modernization of WISP** to ingest regional seismic + geodetic data — exactly the joint
   teleseismic+InSAR (and planned regional) strategy used here. Cited in the USGS data products.

7. **Lohman, R. B., & M. Simons (2005).** *Some thoughts on the use of InSAR data to constrain models
   of surface deformation: noise structure and data downsampling.* **G-cubed 6, Q01007.**
   → How the InSAR interferograms are **resampled** to the ~1000-point datasets we invert (the method
   named in the interferogram file headers).

## Helpful overviews / context

8. **Ide, S. (2007).** *Slip inversion.* In *Treatise on Geophysics*, Vol. 4 (Earthquake
   Seismology), Elsevier.
   → A clear review of kinematic slip-inversion concepts, non-uniqueness, and resolution — good
   orientation before the primary papers.

9. **Beresnev, I. A. (2003).** *Uncertainties in finite-fault slip inversions: to what extent to
   believe? (A critical review).* **BSSA 93, 2445–2458.**
   → A healthy, skeptical read on how much to trust FFM detail — pairs well with the
   frequency/resolution trade-off shown in notebook 12.

---
*This repository's notebooks (07–12) are a worked, reproducible application of the above to the
2026 Venezuela M7.5 doublet.*
