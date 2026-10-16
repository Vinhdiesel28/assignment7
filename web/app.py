from __future__ import annotations

import sys
from pathlib import Path
from flask import Flask, jsonify, render_template, request
import joblib
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.rag_agent import DiabetesAgent

app = Flask(__name__)
agent = DiabetesAgent()
bundle = Path(__file__).resolve().parent / "bundle"
preprocessor = joblib.load(bundle / "preprocessor.joblib")
weights = np.load(bundle / "diabetes_mlp.npz")


def predict_risk(payload):
    row = {
        "year": int(payload.get("year", 2020)), "gender": str(payload.get("gender", "Female")),
        "age": float(payload.get("age", 40)), "location": str(payload.get("location", "Alabama")),
        "race:AfricanAmerican": 0, "race:Asian": 0, "race:Caucasian": 0,
        "race:Hispanic": 0, "race:Other": 1,
        "hypertension": int(payload.get("hypertension", 0)), "heart_disease": int(payload.get("heart_disease", 0)),
        "smoking_history": str(payload.get("smoking_history", "never")), "bmi": float(payload.get("bmi", 25)),
        "hbA1c_level": float(payload.get("hbA1c_level", 5.5)), "blood_glucose_level": float(payload.get("blood_glucose_level", 100)),
    }
    x = np.asarray(preprocessor.transform(pd.DataFrame([row])), dtype=np.float32)
    hidden = np.maximum(0, x @ weights["w1"].T + weights["b1"])
    logits = hidden @ weights["w2"].T + weights["b2"]
    probs = np.exp(logits - logits.max(axis=1, keepdims=True)); probs /= probs.sum(axis=1, keepdims=True)
    return {"class": int(probs[0, 1] >= 0.5), "score": round(float(probs[0, 1]), 4), "model": "PyTorch MLP baseline_lr001 (NumPy inference)", "notice": "Điểm mô hình chưa hiệu chỉnh và không phải xác suất chẩn đoán y khoa."}


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/health")
def health():
    return jsonify({"status": "ok", "documents": len(agent.documents), "triples": len(agent.triples)})


@app.post("/api/chat")
def chat():
    try:
        payload = request.get_json(force=True) or {}
        return jsonify(agent.answer(str(payload.get("question", "")), int(payload.get("top_k", 3))))
    except (ValueError, TypeError) as exc:
        return jsonify({"error": str(exc)}), 400


@app.post("/api/predict")
def predict():
    try:
        return jsonify(predict_risk(request.get_json(force=True) or {}))
    except (ValueError, TypeError) as exc:
        return jsonify({"error": str(exc)}), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5008, debug=True)
