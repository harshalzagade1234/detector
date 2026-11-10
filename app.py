"""Run:  streamlit run app.py"""
import os, joblib, numpy as np, pandas as pd, streamlit as st
from features import CHANNELS, FEATURE_NAMES, BAND_INFO, clean, feature_vector, is_saturated, is_too_dark
from sensor_io import Simulator, CLASSES
from residue import residue_free_percent, verdict

st.set_page_config(page_title="Pesticide Residue Scanner", page_icon="🔬", layout="wide")
st.title("🔬 Portable Optical Scanner - Residue Screening")
st.caption("Screening aid only - not a replacement for lab-certified testing.")

if not os.path.exists("model.joblib"):
    import subprocess, sys
    with st.spinner("First run: training demo model..."):
        subprocess.run([sys.executable, "train.py"], check=True)
bundle = joblib.load("model.joblib"); model = bundle["model"]; classes = list(model.classes_)
if bundle["source"] == "SIMULATED":
    st.warning("Model trained on SIMULATED data - results are for demo only.")

with st.sidebar:
    st.header("Input source")
    st.caption("No hardware connected - using simulated sensor readings.")
    src = "Simulator"
    sim_label = st.selectbox("Simulate sample", CLASSES)
    st.caption(f"Model: {bundle['name']} | trained on {bundle['source']} | CV acc {bundle['cv']:.2f}")

if "history" not in st.session_state: st.session_state.history = []

if st.button("▶ Scan", type="primary"):
    try:
        with st.spinner("Scanning..."):
            sample = Simulator().scan(sim_label)
        if is_saturated(sample): st.error("Sensor saturated - lower gain/LED power or move sample away.")
        elif is_too_dark(sample): st.error("Signal too weak - check LED, sample placement, chamber seal.")
        else:
            proba = model.predict_proba([feature_vector(sample)])[0]
            pct = residue_free_percent(proba, classes); v, msg = verdict(pct)
            st.session_state.last = (sample, proba, pct, v, msg)
            st.session_state.history.append({"Residue-free %": round(pct, 1), "Verdict": v})
    except Exception as e:
        st.error(f"Scan failed: {e}")

if "last" in st.session_state:
    sample, proba, pct, v, msg = st.session_state.last
    c1, c2, c3 = st.columns(3)
    c1.metric("Residue-free", f"{pct:.0f}%"); c2.metric("Verdict", v); c3.metric("Top class", classes[int(np.argmax(proba))])
    (st.success if v == "PASS" else st.warning if v == "UNCERTAIN" else st.error)(msg)
    st.progress(int(pct))
    a, b = st.columns(2)
    with a:
        st.subheader("Spectrum (dark-subtracted)")
        st.bar_chart(pd.DataFrame({"intensity": clean(sample)}, index=CHANNELS))
    with b:
        st.subheader("Class probabilities")
        st.bar_chart(pd.DataFrame({"probability": proba}, index=classes))
    with st.expander("Why? Datasheet band meanings & features"):
        for k, t in BAND_INFO.items(): st.write(f"**{k}** - {t}")
        st.dataframe(pd.DataFrame({"feature": FEATURE_NAMES, "value": feature_vector(sample)}))
if st.session_state.history:
    st.subheader("Scan history"); st.dataframe(pd.DataFrame(st.session_state.history).iloc[::-1])
