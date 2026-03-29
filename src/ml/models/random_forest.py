import pickle
import numpy as np
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, f1_score
from src.utils.config import settings
from src.utils.logger import logger


class RFModel:

    def __init__(self):
        self.model = RandomForestClassifier(
            n_estimators=200,
            max_depth=None,
            min_samples_split=10,
            min_samples_leaf=5,
            max_features="sqrt",
            class_weight="balanced",
            n_jobs=-1,
            random_state=settings.random_seed,
        )
        self.feature_importances_ = None

    def train(self, X_train: np.ndarray, y_train: np.ndarray):
        logger.info(f"Training Random Forest on {len(X_train):,} samples...")
        self.model.fit(X_train, y_train)
        self.feature_importances_ = self.model.feature_importances_
        logger.success("Random Forest training complete")
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict(X)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict_proba(X)

    def predict_single(self, features: np.ndarray) -> dict:
        proba = self.predict_proba(features.reshape(1, -1))[0]
        pred  = int(np.argmax(proba))
        return {
            "prediction":    pred,
            "label":         "ATTACK" if pred == 1 else "BENIGN",
            "confidence":    float(proba[pred]),
            "proba_benign":  float(proba[0]),
            "proba_attack":  float(proba[1]),
            "is_attack":     pred == 1,
        }

    def evaluate(self, X_test: np.ndarray, y_test: np.ndarray) -> dict:
        y_pred  = self.predict(X_test)
        f1      = f1_score(y_test, y_pred, average="binary", zero_division=0)
        report  = classification_report(
            y_test, y_pred,
            target_names=["BENIGN", "ATTACK"],
            output_dict=True,
        )
        logger.info("\n" + classification_report(
            y_test, y_pred, target_names=["BENIGN", "ATTACK"]
        ))
        return {"f1": float(f1), "report": report}

    def top_features(self, feature_names: list, n: int = 15) -> list:
        if self.feature_importances_ is None:
            return []
        indices = np.argsort(self.feature_importances_)[::-1][:n]
        return [
            {"feature": feature_names[i], "importance": float(self.feature_importances_[i])}
            for i in indices
        ]

    def save(self, path: Path = None) -> Path:
        if path is None:
            path = settings.models_dir / "random_forest.pkl"
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump(self.model, f)
        logger.success(f"Random Forest saved → {path}")
        return path

    def load(self, path: Path = None):
        if path is None:
            path = settings.models_dir / "random_forest.pkl"
        with open(path, "rb") as f:
            self.model = pickle.load(f)
        self.feature_importances_ = self.model.feature_importances_
        logger.info(f"Random Forest loaded from {path}")
        return self