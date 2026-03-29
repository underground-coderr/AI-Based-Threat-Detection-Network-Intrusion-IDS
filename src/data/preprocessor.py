import json
import pickle
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from imblearn.over_sampling import SMOTE
from tqdm import tqdm
from src.utils.config import settings
from src.utils.logger import logger

LABEL_MAP = {
    "BENIGN": "BENIGN",
    "DoS Hulk": "DoS",
    "DoS GoldenEye": "DoS",
    "DoS slowloris": "DoS",
    "DoS Slowhttptest": "DoS",
    "DDoS": "DDoS",
    "PortScan": "PortScan",
    "FTP-Patator": "BruteForce",
    "SSH-Patator": "BruteForce",
    "Bot": "Bot",
    "Web Attack - Brute Force": "WebAttack",
    "Web Attack - XSS": "WebAttack",
    "Web Attack - Sql Injection": "WebAttack",
    "Infiltration": "Infiltration",
}

DROP_COLS = [
    "Flow ID", "Source IP", "Source Port",
    "Destination IP", "Timestamp",
]


def load_raw() -> pd.DataFrame:
    raw_dir = settings.data_raw_dir
    csv_files = sorted(raw_dir.glob("*.csv"))

    if not csv_files:
        raise FileNotFoundError(
            "No CSV files found in data/raw/. "
            "Run: python -m src.data.downloader"
        )

    logger.info(f"Loading {len(csv_files)} CSV file(s)...")
    dfs = []
    for f in tqdm(csv_files, desc="Loading"):
        df = pd.read_csv(f, low_memory=False)
        df.columns = df.columns.str.strip()
        dfs.append(df)
        logger.info(f"  {f.name}: {len(df):,} rows")

    combined = pd.concat(dfs, ignore_index=True)
    logger.info(f"Total: {len(combined):,} rows")
    return combined


def clean(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Cleaning data...")
    original = len(df)

    df.drop(columns=[c for c in DROP_COLS if c in df.columns], inplace=True)
    df.replace([float("inf"), float("-inf")], float("nan"), inplace=True)
    df.dropna(inplace=True)
    df.drop_duplicates(inplace=True)

    removed = original - len(df)
    logger.info(f"Removed {removed:,} rows — {len(df):,} remain")
    return df.reset_index(drop=True)


def encode_labels(df: pd.DataFrame, le: LabelEncoder) -> pd.DataFrame:
    logger.info("Encoding labels...")

    df["label_category"] = df["Label"].map(LABEL_MAP).fillna("Unknown")
    df["label_binary"]   = (df["label_category"] != "BENIGN").astype(int)
    df["label_encoded"]  = le.fit_transform(df["label_category"])

    logger.info("Label distribution:")
    for cls, cnt in df["label_category"].value_counts().items():
        logger.info(f"  {cls:<20} {cnt:>8,}  ({cnt/len(df)*100:.1f}%)")

    df.drop(columns=["Label"], inplace=True)
    return df


def run():
    logger.info("=" * 45)
    logger.info("Starting preprocessing pipeline")
    logger.info("=" * 45)

    scaler = StandardScaler()
    le     = LabelEncoder()

    df = load_raw()
    df = clean(df)
    df = encode_labels(df, le)

    label_cols = ["label_category", "label_binary", "label_encoded"]
    feature_cols = [c for c in df.columns if c not in label_cols]

    X = df[feature_cols].astype(np.float32)
    y_binary = df["label_binary"].values
    y_multi  = df["label_encoded"].values

    logger.info(f"Features: {X.shape[1]}  Samples: {X.shape[0]:,}")

    # Split — stratify on multi-class labels
    X_train, X_test, y_train_b, y_test_b, y_train_m, y_test_m = train_test_split(
        X, y_binary, y_multi,
        test_size=settings.test_size,
        random_state=settings.random_seed,
        stratify=y_multi,
    )

    # Scale
    logger.info("Scaling features...")
    X_train_s = scaler.fit_transform(X_train)
    X_test_s  = scaler.transform(X_test)

    # SMOTE on training set only
    if settings.smote_enabled:
        logger.info("Applying SMOTE...")
        smote = SMOTE(random_state=settings.random_seed, k_neighbors=5)
        X_train_s, y_train_b = smote.fit_resample(X_train_s, y_train_b)
        logger.info(f"After SMOTE: {len(X_train_s):,} training samples")

    # Save arrays
    out = settings.data_processed_dir
    np.save(out / "X_train.npy", X_train_s)
    np.save(out / "X_test.npy",  X_test_s)
    np.save(out / "y_train_binary.npy", y_train_b)
    np.save(out / "y_test_binary.npy",  y_test_b)
    np.save(out / "y_train_multi.npy",  y_train_m)
    np.save(out / "y_test_multi.npy",   y_test_m)

    # Save scaler and encoder
    with open(out / "scaler.pkl", "wb") as f:
        pickle.dump(scaler, f)
    with open(out / "label_encoder.pkl", "wb") as f:
        pickle.dump(le, f)

    # Save metadata
    meta = {
        "n_features":      X.shape[1],
        "feature_columns": feature_cols,
        "class_names":     list(le.classes_),
        "n_train":         len(X_train_s),
        "n_test":          len(X_test_s),
    }
    with open(out / "metadata.json", "w") as f:
        json.dump(meta, f, indent=2)

    logger.success("Preprocessing complete!")
    logger.info(f"  Train: {len(X_train_s):,}  Test: {len(X_test_s):,}")
    logger.info(f"  Classes: {meta['class_names']}")
    logger.info("=" * 45)


if __name__ == "__main__":
    run()