import sys
import numpy as np
import pandas as pd
from pathlib import Path
from src.utils.config import settings
from src.utils.logger import logger

ATTACK_LABELS = [
    "BENIGN", "DoS Hulk", "PortScan", "DDoS", "DoS GoldenEye",
    "FTP-Patator", "SSH-Patator", "DoS slowloris", "DoS Slowhttptest",
    "Bot", "Web Attack - Brute Force", "Web Attack - XSS",
    "Web Attack - Sql Injection", "Infiltration",
]

FEATURE_NAMES = [
    "Destination Port", "Flow Duration", "Total Fwd Packets",
    "Total Backward Packets", "Total Length of Fwd Packets",
    "Total Length of Bwd Packets", "Fwd Packet Length Max",
    "Fwd Packet Length Min", "Fwd Packet Length Mean",
    "Fwd Packet Length Std", "Bwd Packet Length Max",
    "Bwd Packet Length Min", "Bwd Packet Length Mean",
    "Bwd Packet Length Std", "Flow Bytes/s", "Flow Packets/s",
    "Flow IAT Mean", "Flow IAT Std", "Flow IAT Max", "Flow IAT Min",
    "Fwd IAT Total", "Fwd IAT Mean", "Fwd IAT Std", "Fwd IAT Max",
    "Fwd IAT Min", "Bwd IAT Total", "Bwd IAT Mean", "Bwd IAT Std",
    "Bwd IAT Max", "Bwd IAT Min", "Fwd PSH Flags", "Bwd PSH Flags",
    "Fwd URG Flags", "Bwd URG Flags", "Fwd Header Length",
    "Bwd Header Length", "Fwd Packets/s", "Bwd Packets/s",
    "Min Packet Length", "Max Packet Length", "Packet Length Mean",
    "Packet Length Std", "Packet Length Variance", "FIN Flag Count",
    "SYN Flag Count", "RST Flag Count", "PSH Flag Count", "ACK Flag Count",
    "URG Flag Count", "Down/Up Ratio", "Average Packet Size",
    "Avg Fwd Segment Size", "Avg Bwd Segment Size",
    "Subflow Fwd Packets", "Subflow Fwd Bytes",
    "Subflow Bwd Packets", "Subflow Bwd Bytes",
    "Init_Win_bytes_forward", "Init_Win_bytes_backward",
    "act_data_pkt_fwd", "min_seg_size_forward",
    "Active Mean", "Active Std", "Active Max", "Active Min",
    "Idle Mean", "Idle Std", "Idle Max", "Idle Min",
    "Label",
]

KAGGLE_INSTRUCTIONS = """
To download the real CICIDS2017 dataset:

  1. Create a free account at https://www.kaggle.com
  2. Go to https://www.kaggle.com/settings and click API > Create New Token
  3. Place the downloaded kaggle.json in C:/Users/YOUR_NAME/.kaggle/
  4. Run:  pip install kaggle
  5. Run:  kaggle datasets download -d cicdataset/cicids2017 -p data/raw --unzip

Total size: ~900MB download, ~2.4GB extracted.
Place all CSV files inside:  data/raw/
"""


def generate_sample_data(n_samples: int = 50000) -> Path:
    logger.info(f"Generating {n_samples:,} synthetic samples for development...")

    rng = np.random.default_rng(settings.random_seed)

    n_benign = int(n_samples * 0.78)
    n_attack = n_samples - n_benign

    labels = ["BENIGN"] * n_benign + rng.choice(
        ATTACK_LABELS[1:], size=n_attack
    ).tolist()
    rng.shuffle(labels)

    data = {}
    for feat in FEATURE_NAMES[:-1]:
        if "Port" in feat:
            data[feat] = rng.integers(0, 65535, n_samples).astype(float)
        elif "Flag" in feat:
            data[feat] = rng.integers(0, 2, n_samples).astype(float)
        else:
            data[feat] = np.abs(rng.exponential(scale=500, size=n_samples)).round(4)

    data["Label"] = labels
    df = pd.DataFrame(data)

    output_path = settings.data_raw_dir / "sample_data.csv"
    df.to_csv(output_path, index=False)

    logger.success(f"Sample data saved → {output_path}  ({n_samples:,} rows)")
    return output_path


def check_data_exists() -> bool:
    csvs = list(settings.data_raw_dir.glob("*.csv"))
    return len(csvs) > 0


def main():
    logger.info("=== CICIDS2017 Dataset Setup ===")

    if check_data_exists():
        csvs = list(settings.data_raw_dir.glob("*.csv"))
        logger.success(f"Dataset found — {len(csvs)} CSV file(s) in data/raw/")
        for f in csvs:
            size_mb = f.stat().st_size / 1_048_576
            logger.info(f"  {f.name}  ({size_mb:.1f} MB)")
        return

    print(KAGGLE_INSTRUCTIONS)

    response = input("Generate SYNTHETIC sample data for now? [y/N]: ").strip().lower()
    if response == "y":
        path = generate_sample_data(n_samples=50000)
        print(f"\nDone! Sample data at: {path}")
        print("NOTE: Use the real CICIDS2017 dataset for final model training.")
    else:
        print("No data generated. Follow the Kaggle instructions above.")
        sys.exit(0)


if __name__ == "__main__":
    main()