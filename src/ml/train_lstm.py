import json
import numpy as np
from src.utils.config import settings
from src.utils.logger import logger
from src.ml.models.lstm_model import LSTMModel


def main():
    logger.info("=" * 45)
    logger.info("Training LSTM")
    logger.info("=" * 45)

    p = settings.data_processed_dir

    X_train = np.load(p / "X_train.npy")
    X_test  = np.load(p / "X_test.npy")
    y_train = np.load(p / "y_train_binary.npy")
    y_test  = np.load(p / "y_test_binary.npy")

    with open(p / "metadata.json") as f:
        meta = json.load(f)

    n_features = meta["n_features"]

    # Trim to match binary labels length
    n = min(len(X_train), len(y_train))
    X_train = X_train[:n]
    y_train = y_train[:n]

    model = LSTMModel(input_size=n_features)
    model.train(X_train, y_train)

    logger.info("Evaluating on test set...")
    results = model.evaluate(X_test, y_test)
    logger.success(f"F1 Score: {results['f1']:.4f}")

    model.save()
    logger.info("=" * 45)


if __name__ == "__main__":
    main()
    