"""Three interchangeable data sources: Simulator (no hardware), SerialReader (ESP32 over USB), CSV loader."""
import json, time
import numpy as np

CLASSES = ["clean", "washed", "pesticide"]

class Simulator:
    """PLACEHOLDER synthetic spectra so the pipeline/UI can be built before hardware exists.
    NOT real physics -- replace with real recorded data (data/real_scans.csv) as soon as the sensor works."""
    BASE = np.array([300, 900, 1300, 1800, 1500, 1100, 1400, 5200, 9000, 900.0])
    def __init__(self, seed=None): self.rng = np.random.default_rng(seed)
    def scan(self, label):
        gain = self.rng.uniform(0.7, 1.3)                       # distance / brightness variation
        v = self.BASE.copy()
        if label == "washed":    v[[1, 2]] *= 1.15; v[7] *= 0.93
        if label == "pesticide": v[[1, 2, 3]] *= 1.7; v[7] *= 0.72; v[0] *= 1.3
        v = v * gain * self.rng.normal(1, 0.06, 10)
        dark = self.rng.uniform(5, 25, 10)
        return {"dark": dark.tolist(), "lit": (v + dark).tolist(), "label": label}

class SerialReader:
    def __init__(self, port, baud=115200):
        import serial
        self.ser = serial.Serial(port, baud, timeout=5); time.sleep(2)
    def scan(self, label=None):
        self.ser.reset_input_buffer(); self.ser.write(b"S")
        line = self.ser.readline().decode(errors="ignore").strip()
        d = json.loads(line)
        if "error" in d: raise RuntimeError(d["error"])
        d["label"] = label
        return d

def sample_to_row(s):
    row = {f"dark_{i}": v for i, v in enumerate(s["dark"])}
    row.update({f"lit_{i}": v for i, v in enumerate(s["lit"])}); row["label"] = s.get("label")
    return row

def row_to_sample(r):
    return {"dark": [r[f"dark_{i}"] for i in range(10)], "lit": [r[f"lit_{i}"] for i in range(10)], "label": r.get("label")}
