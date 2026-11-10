"""Sensor datasheet table + signal processing -> feature vector.
Channel centres from the AS7341 datasheet (ams-OSRAM); each has ~40 nm FWHM. Swap this table if you use AS7265x/TCS34725."""
import numpy as np

CHANNELS = ["F1_415", "F2_445", "F3_480", "F4_515", "F5_555", "F6_590", "F7_630", "F8_680", "CLEAR", "NIR"]
IDX = {n.split("_")[0]: i for i, n in enumerate(CHANNELS)}

# Datasheet-driven meaning of each band under 365 nm excitation (used for explanations in the UI)
BAND_INFO = {
    "F8": "680 nm: chlorophyll fluorescence peak (healthy/untreated leaf & skin signal)",
    "NIR": "~910 nm: far-red/NIR tail, surface reflectance & scatter reference",
    "F2": "445 nm: blue fluorescence (many organic residues/phenolics emit here)",
    "F3": "480 nm: blue-green fluorescence",
    "F4": "515 nm: green fluorescence",
    "F1": "415 nm: near-UV leakage / reflected excitation (check filter, should be low)",
}

def clean(sample):
    """sample = {'dark':[10], 'lit':[10]} -> dark-subtracted, non-negative signal."""
    lit, dark = np.asarray(sample["lit"], float), np.asarray(sample["dark"], float)
    return np.clip(lit - dark, 0, None)

def is_saturated(sample, limit=60000):
    return bool(np.max(sample["lit"]) >= limit)

def is_too_dark(sample, minimum=50):
    return float(np.sum(clean(sample))) < minimum

def feature_vector(sample):
    s = clean(sample)
    clear = s[IDX["CLEAR"]] + 1e-6
    norm = s[:8] / clear                      # intensity-independent (distance/brightness cancels)
    e = 1e-6
    ratios = [
        s[IDX["F8"]] / (s[IDX["F4"]] + e),    # chlorophyll vs green
        s[IDX["F2"]] / (s[IDX["F8"]] + e),    # blue vs chlorophyll (residue fluorescence / quenching)
        s[IDX["F3"]] / (s[IDX["F5"]] + e),
        s[IDX["F1"]] / (s[IDX["F8"]] + e),
        s[IDX["NIR"]] / (s[IDX["F8"]] + e),
        s[IDX["F7"]] / (s[IDX["F8"]] + e),
    ]
    return np.concatenate([norm, ratios])

FEATURE_NAMES = [f"{c}/clear" for c in CHANNELS[:8]] + ["F8/F4", "F2/F8", "F3/F5", "F1/F8", "NIR/F8", "F7/F8"]
