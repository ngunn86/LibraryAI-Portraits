"""Measure dot pitch and grid angle of the owner's target portraits by FFT of the alpha channel."""
import sys, numpy as np
from PIL import Image

def measure(path):
    a = np.asarray(Image.open(path).convert("RGBA"))[..., 3].astype(float) / 255
    h, w = a.shape
    # use the central region (face area) where dots are present
    y0, y1, x0, x1 = int(h*.25), int(h*.85), int(w*.2), int(w*.8)
    r = a[y0:y1, x0:x1]
    r = r - r.mean()
    win = np.outer(np.hanning(r.shape[0]), np.hanning(r.shape[1]))
    F = np.abs(np.fft.fftshift(np.fft.fft2(r * win, s=(1024, 1024))))
    cy, cx = 512, 512
    yy, xx = np.mgrid[:1024, :1024]
    rad = np.hypot(yy-cy, xx-cx)
    F[rad < 40] = 0          # drop low frequencies (image content)
    F[:, :cx] = 0            # half-plane (symmetry)
    peaks = []
    Fc = F.copy()
    for _ in range(4):
        iy, ix = np.unravel_index(np.argmax(Fc), Fc.shape)
        fy, fx = (iy-cy)/1024, (ix-cx)/1024
        f = np.hypot(fy, fx)
        peaks.append((1/f, np.degrees(np.arctan2(-fy, fx)), Fc[iy, ix]))
        Fc[max(0,iy-8):iy+9, max(0,ix-8):ix+9] = 0
    return w, peaks

for p in sys.argv[1:]:
    w, peaks = measure(p)
    print(p.split('/')[-1], f"width {w}")
    for per, ang, mag in peaks:
        print(f"   pitch {per:5.2f}px  angle {ang:6.1f}°  -> {w/per:5.1f} per width   (mag {mag:.0f})")
