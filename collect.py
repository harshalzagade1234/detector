"""Record labelled real scans from the ESP32:  python collect.py COM5 pesticide 30
   Appends to data/real_scans.csv. Labels: clean | washed | pesticide. Keep distance/chamber identical."""
import sys, os, pandas as pd
from sensor_io import SerialReader, sample_to_row
port, label, n = sys.argv[1], sys.argv[2], int(sys.argv[3])
r = SerialReader(port); rows = []
for i in range(n):
    input(f"[{i+1}/{n}] place '{label}' sample, press Enter...")
    rows.append(sample_to_row(r.scan(label)))
os.makedirs("data", exist_ok=True); f = "data/real_scans.csv"
pd.DataFrame(rows).to_csv(f, mode="a", header=not os.path.exists(f), index=False); print("saved", f)
