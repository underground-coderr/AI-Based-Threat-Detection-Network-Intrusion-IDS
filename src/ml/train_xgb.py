import json
import numpy as np
from src.utils.config import settings
from src.utils.logger import logger
from src.ml.models.xgboost_model import XGBModel


def main():
    logger.info("=" * 45)
    logger.info("Training XGBoost")
    logger.info("=" * 45)

    p = settings.data_processed_dir

    X_train = np.load(p / "X_train.npy")
    X_test  = np.load(p / "X_test.npy")
    y_train = np.load(p / "y_train_multi.npy")
    y_test  = np.load(p / "y_test_multi.npy")

    with open(p / "metadata.json") as f:
        meta = json.load(f)

    class_names = meta["class_names"]
    n_classes   = len(class_names)

    # XGBoost handles imbalance itself — trim X_train to match y_train size
    n = min(len(X_train), len(y_train))
    X_train = X_train[:n]
    y_train = y_train[:n]

    # Make sure labels are 0-indexed
    from sklearn.preprocessing import LabelEncoder
    le = LabelEncoder()
    y_train = le.fit_transform(y_train)
    y_test  = le.transform(y_test)

    model = XGBModel(n_classes=n_classes)
    model.class_names = class_names
    model.train(X_train, y_train)

    logger.info("Evaluating on test set...")
    results = model.evaluate(X_test, y_test)
    logger.success(f"Macro F1 Score: {results['macro_f1']:.4f}")

    top = model.feature_importance(meta["feature_columns"], n=10)
    logger.info("Top 10 most important features:")
    for i, feat in enumerate(top, 1):
        logger.info(f"  {i:>2}. {feat['feature']:<35} {feat['importance']:.4f}")

    model.save()
    logger.info("=" * 45)


if __name__ == "__main__":
    main()