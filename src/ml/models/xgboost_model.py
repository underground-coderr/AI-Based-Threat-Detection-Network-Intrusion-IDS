import pickle
import numpy as np
from pathlib import Path
from xgboost import XGBClassifier
from sklearn.metrics import classification_report, f1_score
from src.utils.config import settings
from src.utils.logger import logger


class XGBModel:

    def __init__(self, n_classes: int = 7):
        self.n_classes   = n_classes
        self.class_names = []
        self.model       = XGBClassifier(
            n_estimators=300,
            max_depth=8,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            min_child_weight=5,
            gamma=0.1,
            objective="multi:softprob",
            num_class=n_classes,
            eval_metric="mlogloss",
            tree_method="hist",
            n_jobs=-1,
            random_state=settings.random_seed,
            verbosity=0,
        )

    def train(self, X_train: np.ndarray, y_train: np.ndarray):
        logger.info(f"Training XGBoost on {len(X_train):,} samples, {self.n_classes} classes...")
        self.model.fit(X_train, y_train)
        logger.success("XGBoost training complete")
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict(X)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict_proba(X)

    def predict_single(self, features: np.ndarray) -> dict:
        proba = self.predict_proba(features.reshape(1, -1))[0]
        pred  = int(np.argmax(proba))
        names = self.class_names or [str(i) for i in range(len(proba))]
        label = names[pred] if pred < len(names) else f"class_{pred}"
        return {
            "prediction":        pred,
            "label":             label,
            "confidence":        float(proba[pred]),
            "is_attack":         label != "BENIGN",
            "all_probabilities": {
                names[i]: float(p) for i, p in enumerate(proba)
            },
        }

    def evaluate(self, X_test: np.ndarray, y_test: np.ndarray) -> dict:
        y_pred   = self.predict(X_test)
        macro_f1 = f1_score(y_test, y_pred, average="macro", zero_division=0)
        report   = classification_report(
            y_test, y_pred,
            target_names=self.class_names or None,
            output_dict=True,
        )
        logger.info("\n" + classification_report(
            y_test, y_pred,
            target_names=self.class_names or None,
        ))
        return {"macro_f1": float(macro_f1), "report": report}

    def feature_importance(self, feature_names: list, n: int = 15) -> list:
        scores  = self.model.feature_importances_
        indices = np.argsort(scores)[::-1][:n]
        return [
            {"feature": feature_names[i], "importance": float(scores[i])}
            for i in indices
        ]

    def save(self, path: Path = None) -> Path:
        if path is None:
            path = settings.models_dir / "xgboost.pkl"
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump(self, f)
        logger.success(f"XGBoost saved → {path}")
        return path

    @classmethod
    def load(cls, path: Path = None):
        if path is None:
            path = settings.models_dir / "xgboost.pkl"
        with open(path, "rb") as f:
            obj = pickle.load(f)
        logger.info(f"XGBoost loaded from {path}")
        return obj