import json
import pickle
from pathlib import Path
from typing import Optional
import numpy as np
from src.utils.config import settings
from src.utils.logger import logger

ATTACK_SEVERITY = {
    "BENIGN":     0,
    "DoS":        4,
    "DDoS":       5,
    "BruteForce": 3,
    "WebAttack":  3,
    "PortScan":   2,
    "Bot":        4,
    "Infiltration": 5,
    "ATTACK":     3,
}

SEVERITY_LABELS = {
    0: "None",
    1: "Info",
    2: "Low",
    3: "Medium",
    4: "High",
    5: "Critical",
}


class DetectionEngine:

    _instance: Optional["DetectionEngine"] = None

    def __init__(self):
        self.scaler        = None
        self.rf_model      = None
        self.xgb_model     = None
        self.lstm_model    = None
        self.feature_cols  = []
        self.class_names   = []
        self._loaded       = False

    @classmethod
    def get_instance(cls) -> "DetectionEngine":
        if cls._instance is None:
            cls._instance = cls()
            cls._instance.load()
        return cls._instance

    def load(self):
        processed  = settings.data_processed_dir
        models_dir = settings.models_dir

        scaler_path = processed / "scaler.pkl"
        meta_path   = processed / "metadata.json"

        if not scaler_path.exists() or not meta_path.exists():
            logger.warning("Scaler or metadata missing — run preprocessor first")
            return

        with open(scaler_path, "rb") as f:
            self.scaler = pickle.load(f)

        with open(meta_path) as f:
            meta = json.load(f)

        self.feature_cols = meta.get("feature_columns", [])
        self.class_names  = meta.get("class_names", [])

        # Load Random Forest
        rf_path = models_dir / "random_forest.pkl"
        if rf_path.exists():
            try:
                from src.ml.models.random_forest import RFModel
                self.rf_model = RFModel().load(rf_path)
                logger.info("  Random Forest : loaded")
            except Exception as e:
                logger.warning(f"  Random Forest load failed: {e}")

        # Load XGBoost
        xgb_path = models_dir / "xgboost.pkl"
        if xgb_path.exists():
            try:
                from src.ml.models.xgboost_model import XGBModel
                self.xgb_model = XGBModel.load(xgb_path)
                self.xgb_model.class_names = self.class_names
                logger.info("  XGBoost       : loaded")
            except Exception as e:
                logger.warning(f"  XGBoost load failed: {e}")

        # Load LSTM
        lstm_path = models_dir / "lstm.pt"
        if lstm_path.exists():
            try:
                from src.ml.models.lstm_model import LSTMModel
                self.lstm_model = LSTMModel.load(lstm_path)
                logger.info("  LSTM          : loaded")
            except Exception as e:
                logger.warning(f"  LSTM load failed: {e}")

        self._loaded = True
        n = sum([
            self.rf_model   is not None,
            self.xgb_model  is not None,
            self.lstm_model is not None,
        ])
        logger.success(f"Detection Engine ready — {n}/3 models loaded")

    def _preprocess(self, features: dict | list | np.ndarray) -> np.ndarray:
        if isinstance(features, dict):
            arr = np.array(
                [features.get(col, 0.0) for col in self.feature_cols],
                dtype=np.float32,
            )
        elif isinstance(features, list):
            arr = np.array(features, dtype=np.float32)
        else:
            arr = features.astype(np.float32)

        arr = np.nan_to_num(arr, nan=0.0, posinf=0.0, neginf=0.0)

        if self.scaler is not None:
            arr = self.scaler.transform(arr.reshape(1, -1))[0]

        return arr

    def _severity(self, attack_type: str, confidence: float) -> dict:
        base     = ATTACK_SEVERITY.get(attack_type, 3)
        boosted  = min(5, base + 1) if confidence > settings.high_severity_threshold else base
        is_attack = attack_type != "BENIGN"
        score    = boosted if is_attack else 0
        return {
            "severity_score": score,
            "severity_label": SEVERITY_LABELS[score],
            "is_attack":      is_attack,
        }

    def predict(self, features: dict | list | np.ndarray) -> dict:
        if not self._loaded:
            raise RuntimeError("Engine not loaded — call load() first")

        arr     = self._preprocess(features)
        results = {}

        if self.rf_model:
            results["rf"] = self.rf_model.predict_single(arr)

        if self.xgb_model:
            results["xgb"] = self.xgb_model.predict_single(arr)

        if self.lstm_model:
            results["lstm"] = self.lstm_model.predict_single(arr)

        # Ensemble vote
        attack_votes = sum(
            1 for r in results.values()
            if r.get("is_attack", r.get("label") == "ATTACK")
        )
        total_votes      = len(results)
        ensemble_attack  = attack_votes > total_votes / 2

        # Primary label from XGBoost (most specific), fallback to RF
        primary      = results.get("xgb") or results.get("rf") or {}
        attack_type  = primary.get("label", "UNKNOWN") if ensemble_attack else "BENIGN"
        confidence   = primary.get("confidence", 0.0)
        should_alert = ensemble_attack and confidence >= settings.alert_confidence_min

        severity = self._severity(attack_type, confidence)

        return {
            "is_attack":      ensemble_attack,
            "attack_type":    attack_type,
            "confidence":     round(confidence, 4),
            "should_alert":   should_alert,
            "model_results":  results,
            "ensemble_votes": {"attack": attack_votes, "total": total_votes},
            **severity,
        }

    @property
    def is_ready(self) -> bool:
        return self._loaded and any([
            self.rf_model, self.xgb_model, self.lstm_model
        ])

    def status(self) -> dict:
        return {
            "loaded": self._loaded,
            "models": {
                "random_forest": self.rf_model   is not None,
                "xgboost":       self.xgb_model  is not None,
                "lstm":          self.lstm_model  is not None,
            },
            "n_features":  len(self.feature_cols),
            "class_names": self.class_names,
        }