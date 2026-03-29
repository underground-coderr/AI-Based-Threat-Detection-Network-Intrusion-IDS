import json
import numpy as np
from src.utils.config import settings
from src.utils.logger import logger
from src.ml.models.random_forest import RFModel


def main():
    logger.info("=" * 45)
    logger.info("Training Random Forest")
    logger.info("=" * 45)

    p = settings.data_processed_dir

    X_train = np.load(p / "X_train.npy")
    X_test  = np.load(p / "X_test.npy")
    y_train = np.load(p / "y_train_binary.npy")
    y_test  = np.load(p / "y_test_binary.npy")

    with open(p / "metadata.json") as f:
        meta = json.load(f)

    model = RFModel()
    model.train(X_train, y_train)

    logger.info("Evaluating on test set...")
    results = model.evaluate(X_test, y_test)
    logger.success(f"F1 Score: {results['f1']:.4f}")

    top = model.top_features(meta["feature_columns"], n=10)
    logger.info("Top 10 most important features:")
    for i, feat in enumerate(top, 1):
        logger.info(f"  {i:>2}. {feat['feature']:<35} {feat['importance']:.4f}")

    model.save()
    logger.info("=" * 45)


if __name__ == "__main__":
    main()