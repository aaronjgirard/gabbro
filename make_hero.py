"""Synthesize a small seismic section and render it as variable-area wiggle traces.

Real geophysics, not decoration: a reflectivity series with a few dipping
events, convolved with a Ricker wavelet. Positive lobes get filled, which is
exactly how a processor looks at a shot gather.
"""
import numpy as np

rng = np.random.default_rng(11)

N_TRACES = 40
N_SAMPLES = 240          # "time" samples
DT = 0.004               # 4 ms
F0 = 26.0                # Ricker peak frequency, Hz

# --- wavelet ---------------------------------------------------------------
tw = np.arange(-0.06, 0.06 + DT, DT)
a = (np.pi * F0 * tw) ** 2
ricker = (1 - 2 * a) * np.exp(-a)

# --- reflectivity: coherent dipping reflectors + faint scatter -------------
refl = np.zeros((N_SAMPLES, N_TRACES))

events = [
    # (t0_sample, dip_samples_per_trace, amplitude, curvature)
    (35,   0.55,  0.95, 0.004),
    (69, -0.30,  0.62, 0.000),
    (98,  0.18, -0.80, 0.010),
    (131,  0.90,  0.70, 0.000),
    (159, -0.62, -0.55, 0.006),
    (196,  0.25,  0.88, 0.000),
]

for t0, dip, amp, curv in events:
    for x in range(N_TRACES):
        xc = x - N_TRACES / 2
        t = int(round(t0 + dip * xc + curv * xc**2))
        if 0 <= t < N_SAMPLES:
            # gentle amplitude taper with offset, like real AVO fall-off
            refl[t, x] += amp * (1.0 - 0.22 * abs(xc) / (N_TRACES / 2))

refl += rng.normal(0, 0.02, refl.shape)

# --- convolve, normalize ---------------------------------------------------
data = np.apply_along_axis(lambda tr: np.convolve(tr, ricker, mode="same"), 0, refl)
data /= np.abs(data).max()

# --- geometry --------------------------------------------------------------
W, H = 1240.0, 380.0
PAD_X, PAD_Y = 8.0, 6.0
spacing = (W - 2 * PAD_X) / (N_TRACES - 1)
gain = spacing * 1.9              # trace excursion in px
ys = PAD_Y + np.linspace(0, H - 2 * PAD_Y, N_SAMPLES)


def fmt(v):
    return f"{v:.1f}".rstrip("0").rstrip(".")


wiggles, fills = [], []

for x in range(N_TRACES):
    x0 = PAD_X + x * spacing
    tr = data[:, x]
    xs = x0 + tr * gain

    wiggles.append(
        "M" + " L".join(f"{fmt(px)},{fmt(py)}" for px, py in zip(xs, ys))
    )

    # variable-area: fill only the positive (right-deflecting) lobes
    clipped = np.maximum(tr, 0.0)
    inside = clipped > 0.07
    start = None
    for i, flag in enumerate(inside):
        if flag and start is None:
            start = i
        elif not flag and start is not None:
            seg = slice(start, i)
            pts = " L".join(
                f"{fmt(px)},{fmt(py)}"
                for px, py in zip(x0 + clipped[seg] * gain, ys[seg])
            )
            fills.append(f"M{fmt(x0)},{fmt(ys[start])} L{pts} L{fmt(x0)},{fmt(ys[i-1])} Z")
            start = None
    if start is not None:
        seg = slice(start, N_SAMPLES)
        pts = " L".join(
            f"{fmt(px)},{fmt(py)}"
            for px, py in zip(x0 + clipped[seg] * gain, ys[seg])
        )
        fills.append(f"M{fmt(x0)},{fmt(ys[start])} L{pts} L{fmt(x0)},{fmt(ys[-1])} Z")

svg = f'''<svg viewBox="0 0 {fmt(W)} {fmt(H)}" xmlns="http://www.w3.org/2000/svg" role="img"
     aria-label="A synthetic seismic shot gather: six dipping reflectors rendered as variable-area wiggle traces.">
  <style>
    .fill   {{ fill: #a3241d; }}
    .wiggle {{ fill: none; stroke: #101418; stroke-width: 0.75; stroke-linejoin: round; }}
    .sweep  {{ transform-origin: left center; animation: shoot 1.5s cubic-bezier(.2,.7,.2,1) both; }}
    @keyframes shoot {{ from {{ transform: scaleX(0); }} to {{ transform: scaleX(1); }} }}
    @media (prefers-reduced-motion: reduce) {{ .sweep {{ animation: none; }} }}
  </style>
  <clipPath id="sweep"><rect class="sweep" x="0" y="0" width="{fmt(W)}" height="{fmt(H)}"/></clipPath>
  <g clip-path="url(#sweep)">
    <path class="fill" d="{' '.join(fills)}"/>
    <path class="wiggle" d="{' '.join(wiggles)}"/>
  </g>
</svg>
'''

with open("/mnt/user-data/outputs/gabbro.ca/hero.svg", "w") as f:
    f.write(svg)

print(f"{N_TRACES} traces, {len(fills)} filled lobes, {len(svg)/1024:.0f} KB")
