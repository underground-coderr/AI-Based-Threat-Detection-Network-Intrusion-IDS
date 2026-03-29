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
    logger.info(f"Generating {n_samples:,} synthetic samples with realistic patterns...")

    rng = np.random.default_rng(settings.random_seed)
    rows = []

    attack_configs = {
        "BENIGN":     {"syn": (0,1), "bytes": (500,200),   "pkts": (10,5),   "dur": (50000,20000)},
        "DoS Hulk":   {"syn": (800,100), "bytes": (90000,10000), "pkts": (5000,500), "dur": (5000000,1000000)},
        "DDoS":       {"syn": (900,50), "bytes": (95000,5000),  "pkts": (8000,1000), "dur": (3000000,500000)},
        "PortScan":   {"syn": (1,0),  "bytes": (40,10),    "pkts": (1,0),    "dur": (500,100)},
        "FTP-Patator":{"syn": (1,0),  "bytes": (200,50),   "pkts": (5,2),    "dur": (30000000,5000000)},
        "SSH-Patator":{"syn": (1,0),  "bytes": (180,40),   "pkts": (4,1),    "dur": (28000000,4000000)},
        "Bot":        {"syn": (2,1),  "bytes": (300,100),  "pkts": (8,3),    "dur": (1000000,200000)},
        "Web Attack - Brute Force": {"syn": (1,0), "bytes": (800,200), "pkts": (12,4), "dur": (20000,5000)},
    }

    n_per_class = {
        "BENIGN": int(n_samples * 0.78),
    }
    attack_labels = list(attack_configs.keys())[1:]
    remaining = n_samples - n_per_class["BENIGN"]
    per_attack = remaining // len(attack_labels)
    for label in attack_labels:
        n_per_class[label] = per_attack

    for label, cfg in attack_configs.items():
        count = n_per_class[label]
        for _ in range(count):
            syn   = max(0, int(rng.normal(cfg["syn"][0],   max(1, cfg["syn"][1]))))
            bytes_ = max(0, rng.normal(cfg["bytes"][0], cfg["bytes"][1]))
            pkts  = max(1, int(rng.normal(cfg["pkts"][0],  max(1, cfg["pkts"][1]))))
            dur   = max(0, rng.normal(cfg["dur"][0],   cfg["dur"][1]))

            row = {
                "Destination Port":             rng.integers(1, 65535),
                "Flow Duration":                dur,
                "Total Fwd Packets":            pkts,
                "Total Backward Packets":       max(0, pkts - rng.integers(0, 3)),
                "Total Length of Fwd Packets":  bytes_,
                "Total Length of Bwd Packets":  bytes_ * 0.8,
                "Fwd Packet Length Max":        bytes_ / max(1, pkts),
                "Fwd Packet Length Min":        bytes_ / max(1, pkts) * 0.5,
                "Fwd Packet Length Mean":       bytes_ / max(1, pkts) * 0.8,
                "Fwd Packet Length Std":        bytes_ / max(1, pkts) * 0.1,
                "Bwd Packet Length Max":        bytes_ * 0.4,
                "Bwd Packet Length Min":        bytes_ * 0.1,
                "Bwd Packet Length Mean":       bytes_ * 0.3,
                "Bwd Packet Length Std":        bytes_ * 0.05,
                "Flow Bytes/s":                 bytes_ / max(1, dur) * 1e6,
                "Flow Packets/s":               pkts   / max(1, dur) * 1e6,
                "Flow IAT Mean":                dur / max(1, pkts),
                "Flow IAT Std":                 dur / max(1, pkts) * 0.2,
                "Flow IAT Max":                 dur / max(1, pkts) * 2,
                "Flow IAT Min":                 1.0,
                "Fwd IAT Total":                dur * 0.9,
                "Fwd IAT Mean":                 dur / max(1, pkts),
                "Fwd IAT Std":                  dur / max(1, pkts) * 0.1,
                "Fwd IAT Max":                  dur / max(1, pkts) * 1.5,
                "Fwd IAT Min":                  1.0,
                "Bwd IAT Total":                dur * 0.8,
                "Bwd IAT Mean":                 dur / max(1, pkts) * 0.9,
                "Bwd IAT Std":                  dur / max(1, pkts) * 0.1,
                "Bwd IAT Max":                  dur / max(1, pkts) * 1.2,
                "Bwd IAT Min":                  1.0,
                "Fwd PSH Flags":                rng.integers(0, 2),
                "Bwd PSH Flags":                rng.integers(0, 2),
                "Fwd URG Flags":                0,
                "Bwd URG Flags":                0,
                "Fwd Header Length":            pkts * 20,
                "Bwd Header Length":            pkts * 20,
                "Fwd Packets/s":                pkts / max(1, dur) * 1e6,
                "Bwd Packets/s":                pkts / max(1, dur) * 0.8e6,
                "Min Packet Length":            40.0,
                "Max Packet Length":            bytes_ / max(1, pkts),
                "Packet Length Mean":           bytes_ / max(1, pkts) * 0.7,
                "Packet Length Std":            bytes_ / max(1, pkts) * 0.1,
                "Packet Length Variance":       (bytes_ / max(1, pkts) * 0.1) ** 2,
                "FIN Flag Count":               1 if label == "BENIGN" else 0,
                "SYN Flag Count":               syn,
                "RST Flag Count":               1 if label == "PortScan" else 0,
                "PSH Flag Count":               rng.integers(0, 3),
                "ACK Flag Count":               max(0, pkts - 1),
                "URG Flag Count":               0,
                "Down/Up Ratio":                0.8,
                "Average Packet Size":          bytes_ / max(1, pkts),
                "Avg Fwd Segment Size":         bytes_ / max(1, pkts) * 0.8,
                "Avg Bwd Segment Size":         bytes_ / max(1, pkts) * 0.6,
                "Subflow Fwd Packets":          pkts,
                "Subflow Fwd Bytes":            bytes_,
                "Subflow Bwd Packets":          max(0, pkts - 2),
                "Subflow Bwd Bytes":            bytes_ * 0.8,
                "Init_Win_bytes_forward":       65535,
                "Init_Win_bytes_backward":      65535,
                "act_data_pkt_fwd":             pkts,
                "min_seg_size_forward":         20,
                "Active Mean":                  dur * 0.6,
                "Active Std":                   dur * 0.1,
                "Active Max":                   dur * 0.8,
                "Active Min":                   dur * 0.4,
                "Idle Mean":                    dur * 0.3,
                "Idle Std":                     dur * 0.05,
                "Idle Max":                     dur * 0.4,
                "Idle Min":                     dur * 0.2,
                "Label":                        label,
            }
            rows.append(row)

    df = pd.DataFrame(rows)
    df = df.sample(frac=1, random_state=settings.random_seed).reset_index(drop=True)

    output_path = settings.data_raw_dir / "sample_data.csv"
    df.to_csv(output_path, index=False)
    logger.success(f"Sample data saved → {output_path}  ({len(df):,} rows)")
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