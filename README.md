# Low-Cost Portable Optical Scanner - Pesticide Residue Screening (Interface)

EDI Project 1, Vishwakarma Institute of Technology, Pune.

Streamlit dashboard that shows a **residue-free %** and a PASS / UNCERTAIN / FAIL verdict from spectral readings.
**Current status:** no sensor hardware yet, so the app uses *simulated* readings (placeholder data, not real measurements).

> Screening aid only - not a replacement for lab-certified testing.

## Run locally
    pip install -r requirements.txt
    streamlit run app.py        # trains a demo model automatically on first run

## Project layout
- `app.py` - dashboard
- `features.py` - band table (AS7341 datasheet) + feature extraction
- `train.py` - model comparison and training
- `residue.py` - residue-free % and Delta-E
- `sensor_io.py` - simulator (and serial reader for later)
- `firmware/`, `collect.py` - ESP32 code and data collection, for when hardware is available

## Roadmap
- [x] Interface + processing pipeline on simulated data
- [ ] Real sensor (AS7341 + 365 nm UV) and real labelled dataset
- [ ] Retrain on real data, tune thresholds
- [ ] TinyML deployment (Edge Impulse)

## Team
Vyankatesh Surnar, Ujwal Wankhade, Yash Tidake, Yukti Patil, Harshal Zagade. Guide: Gajanan Himmatrao Chavhan.
