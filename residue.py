"""Residue-free % and the optional colour-strip Delta-E."""
import numpy as np

def residue_free_percent(proba, classes):
    """Percent = model's probability the sample is NOT pesticide-treated. Screening score, not a lab measurement."""
    return 100.0 * (1.0 - proba[classes.index("pesticide")])

def verdict(pct):
    if pct >= 85: return "PASS", "No residue signature detected"
    if pct >= 60: return "UNCERTAIN", "Re-scan / wash and test again"
    return "FAIL", "Residue signature detected - confirm in a lab"

def rgb_to_lab(rgb):
    c = np.asarray(rgb, float) / 255.0
    c = np.where(c > 0.04045, ((c + 0.055) / 1.055) ** 2.4, c / 12.92)
    M = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]])
    xyz = (M @ c) / np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.array([116 * f[1] - 16, 500 * (f[0] - f[1]), 200 * (f[1] - f[2])])

def delta_e(rgb_ref, rgb_sample):
    """CIE76 Delta-E = Euclidean distance in Lab (for the ESP32-CAM test-strip option)."""
    return float(np.linalg.norm(rgb_to_lab(rgb_ref) - rgb_to_lab(rgb_sample)))
