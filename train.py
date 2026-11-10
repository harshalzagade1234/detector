"""python train.py            -> trains on data/real_scans.csv if present, else on simulated data
   Compares classifiers, saves best to model.joblib."""
import os, sys, joblib, numpy as np, pandas as pd
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.model_selection import cross_val_score, StratifiedKFold
from features import feature_vector
from sensor_io import Simulator, CLASSES, sample_to_row, row_to_sample

REAL = "data/real_scans.csv"
if os.path.exists(REAL):
    df = pd.read_csv(REAL); source = "REAL"
else:
    sim = Simulator(seed=0)
    df = pd.DataFrame([sample_to_row(sim.scan(c)) for c in CLASSES for _ in range(150)]); source = "SIMULATED"
    os.makedirs("data", exist_ok=True); df.to_csv("data/sim_scans.csv", index=False)

X = np.array([feature_vector(row_to_sample(r)) for r in df.to_dict("records")]); y = df["label"].values
models = {
    "LogReg+PCA": make_pipeline(StandardScaler(), PCA(n_components=0.99), LogisticRegression(max_iter=2000)),
    "SVM-RBF": make_pipeline(StandardScaler(), SVC(probability=True)),
    "RandomForest": RandomForestClassifier(n_estimators=200, random_state=0),
}
cv = StratifiedKFold(5, shuffle=True, random_state=0)
scores = {n: cross_val_score(m, X, y, cv=cv).mean() for n, m in models.items()}
for n, s in scores.items(): print(f"{n:14s} CV accuracy = {s:.3f}")
best = max(scores, key=scores.get); models[best].fit(X, y)
joblib.dump({"model": models[best], "name": best, "source": source, "cv": scores[best]}, "model.joblib")
print(f"Saved {best} trained on {source} data ({len(df)} scans)")
if source == "SIMULATED": print("WARNING: accuracy on simulated data means nothing. Collect real scans!")
