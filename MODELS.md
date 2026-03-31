# Models, Dataset & API Reference — ThreatNet IDS

Technical documentation covering the CICIDS2017 dataset,
machine learning model architecture, evaluation results,
dependency rationale, and full API reference.

---

## Table of Contents

- [Dataset](#dataset)
- [ML Models](#ml-models)
- [Model Performance](#model-performance)
- [Feature Importance](#feature-importance)
- [Tech Stack — Full Rationale](#tech-stack--full-rationale)
- [API Reference](#api-reference)
- [Understanding the Features](#understanding-the-features)

---

## Dataset

### CICIDS2017 — Canadian Institute for Cybersecurity

| Property | Value |
|---|---|
| Publisher | University of New Brunswick |
| Year | 2017 |
| Total raw flows | 2,313,810 |
| After cleaning | 2,231,806 |
| Training set (after SMOTE) | 3,032,500 |
| Test set | 446,362 |
| Features per flow | 77 |
| Attack categories | 8 |
| Collection method | CICFlowMeter on a realistic lab network |

### Why CICIDS2017

This dataset is the most widely cited benchmark in network intrusion
detection research. It was generated on a realistic network topology
using actual attack tools — not simulated traffic. Every flow was
labeled by the security team at UNB, making it one of the most
reliable labeled IDS datasets available publicly.

### Label Distribution (Raw)
```
BENIGN        1,895,314  (84.9%)
DoS             193,756  ( 8.7%)
DDoS            128,014  ( 5.7%)
BruteForce        9,150  ( 0.4%)
WebAttack         2,143  ( 0.1%)
PortScan          1,956  ( 0.1%)
Bot               1,437  ( 0.1%)
Infiltration         36  ( 0.0%)
```

This extreme imbalance is a core challenge. Without SMOTE, any model
would achieve 85% accuracy by predicting BENIGN for everything — while
detecting zero attacks. SMOTE synthetically generates minority class
samples so all classes are represented in training.

### Label Mapping
Raw CICIDS2017 labels are mapped to canonical categories:

| Raw Label | Category |
|---|---|
| Benign | BENIGN |
| DoS Hulk, DoS GoldenEye, DoS slowloris, DoS Slowhttptest, Heartbleed | DoS |
| DDoS | DDoS |
| FTP-Patator, SSH-Patator | BruteForce |
| Web Attack – Brute Force, XSS, Sql Injection | WebAttack |
| PortScan | PortScan |
| Bot | Bot |
| Infiltration | Infiltration |

---

## ML Models

### Model 1 — Random Forest (Binary Classifier)

**Task:** Classify each flow as BENIGN or ATTACK

**Architecture:**
```
Input: 77 features (standardized)
       │
       ├── 200 Decision Trees (grown in parallel)
       │   Each tree trained on bootstrap sample
       │   Each split considers sqrt(77) ≈ 9 features
       │
       └── Majority vote across all 200 trees
                 │
                 └── Output: BENIGN / ATTACK + probability
```

**Hyperparameters:**
| Parameter | Value | Reason |
|---|---|---|
| `n_estimators` | 200 | Enough trees for stable predictions |
| `max_features` | sqrt | Classic RF setting, reduces correlation |
| `class_weight` | balanced | Compensates for class imbalance |
| `min_samples_leaf` | 5 | Prevents overfitting on tiny leaves |
| `n_jobs` | -1 | Use all CPU cores |

**Why Random Forest:**
Handles high-dimensional tabular data extremely well with minimal tuning.
Naturally resistant to overfitting through bagging. Provides built-in
feature importance. Fast inference — under 1ms per sample — suitable
for real-time detection. No feature scaling required (though we scale
anyway for pipeline consistency).

---

### Model 2 — XGBoost (Multi-class Classifier)

**Task:** Identify the exact attack type across 8 classes

**Architecture:**
```
Input: 77 features (standardized)
       │
       └── 300 Gradient Boosted Trees
           Objective: multi:softprob
           Each tree corrects residual errors of previous
                 │
                 └── Output: probability vector [8 classes]
                             argmax → predicted class
```

**Hyperparameters:**
| Parameter | Value | Reason |
|---|---|---|
| `n_estimators` | 300 | More trees for multi-class complexity |
| `max_depth` | 8 | Captures complex feature interactions |
| `learning_rate` | 0.1 | Standard conservative rate |
| `subsample` | 0.8 | Row subsampling — reduces overfitting |
| `colsample_bytree` | 0.8 | Column subsampling per tree |
| `objective` | multi:softprob | Returns full probability distribution |
| `tree_method` | hist | Histogram-based — significantly faster |

**Why XGBoost:**
Consistently the top-performing algorithm on tabular data in
research benchmarks and Kaggle competitions. Handles non-linear
feature interactions that Random Forest misses. Supports multi-class
classification natively. The histogram tree method makes training
on 2M+ samples feasible without excessive memory usage.

---

### Model 3 — LSTM (Sequence Anomaly Detector)

**Task:** Detect attacks by analyzing sequences of 20 consecutive flows

**Architecture:**
```
Input: (batch, seq_len=20, features=77)
       │
       └── LSTM Layer 1 (hidden=128, dropout=0.3)
                 │
                 └── LSTM Layer 2 (hidden=128)
                           │
                           └── Last hidden state
                                     │
                                     ├── Linear(128 → 64)
                                     ├── ReLU
                                     ├── Dropout(0.3)
                                     └── Linear(64 → 2)
                                               │
                                               └── Softmax → BENIGN / ATTACK
```

**Training Configuration:**
| Parameter | Value |
|---|---|
| Sequence length | 20 flows |
| Batch size | 256 |
| Epochs | 20 |
| Optimizer | Adam (lr=0.001) |
| Scheduler | StepLR (step=7, gamma=0.5) |
| Gradient clipping | max_norm=1.0 |
| Device | CUDA if available, else CPU |

**Why LSTM:**
Individual flow classifiers (RF, XGBoost) make decisions in isolation.
A port scanner sending one SYN every 10 minutes looks completely
normal per flow. But 20 consecutive flows from the same source
to 20 different ports is obviously a scan. The LSTM captures this
temporal pattern. Sequence length of 20 was chosen to balance
context window size against memory requirements.

---

## Model Performance

All metrics evaluated on **446,362 held-out test flows**
never seen during training.

### Random Forest — Binary
```
              precision    recall  f1-score   support

      BENIGN       1.00      1.00      1.00    379,064
      ATTACK       1.00      1.00      1.00     67,298

    accuracy                           1.00    446,362
   macro avg       1.00      1.00      1.00    446,362

Binary F1 Score: 0.9962
```

### XGBoost — 8-class
```
              precision    recall  f1-score   support

      BENIGN       1.00      1.00      1.00    379,064
         Bot       0.86      0.67      0.75        287
  BruteForce       1.00      1.00      1.00      1,830
        DDoS       1.00      1.00      1.00     25,603
         DoS       1.00      1.00      1.00     38,751
Infiltration       1.00      0.71      0.83          7
    PortScan       0.93      0.92      0.93        391
   WebAttack       0.98      0.98      0.98        429

    accuracy                           1.00    446,362
   macro avg       0.97      0.91      0.94    446,362

Macro F1 Score: 0.9366
```

> **Note on Bot (F1: 0.75) and Infiltration (F1: 0.83):**
> These classes have only 287 and 7 test samples respectively.
> Low sample counts make F1 scores inherently volatile — a
> handful of misclassifications significantly impacts the metric.
> This reflects a real-world IDS challenge, not a model failure.

### LSTM — Binary Sequential
```
              precision    recall  f1-score   support

      BENIGN       1.00      1.00      1.00    379,045
      ATTACK       0.99      0.97      0.98     67,297

    accuracy                           0.99    446,342

Binary F1 Score: 0.9829
```

---

## Feature Importance

Top features identified by both Random Forest and XGBoost:

| Rank | Feature | Description | Why It Matters |
|---|---|---|---|
| 1 | `Bwd Packet Length Std` | Std deviation of return packet sizes | Attacks have very uniform or very chaotic return sizes |
| 2 | `Bwd Packet Length Mean` | Average return packet size | DoS/DDoS returns are tiny or zero |
| 3 | `Avg Bwd Segment Size` | Backward TCP segment size | Normal traffic has consistent segments |
| 4 | `Packet Length Variance` | Overall variance in packet sizes | High in scans, low in floods |
| 5 | `Flow Bytes/s` | Data transfer rate | DoS has extreme rates, scans have near-zero |
| 6 | `Idle Mean` | Mean idle time between flows | Brute force has very regular idle intervals |
| 7 | `Subflow Fwd Packets` | Packets in forward subflow | Differs significantly across attack types |
| 8 | `Total Fwd Packets` | Total packets sent forward | DoS sends thousands; scans send one |
| 9 | `Flow Packets/s` | Packets per second | Extreme values indicate flooding |
| 10 | `SYN Flag Count` | Number of SYN flags | >100 SYNs = almost certainly a flood |

---

## Tech Stack — Full Rationale

### Data Science Layer

**`numpy==2.1.0`**
Foundation of all numerical operations. Every feature matrix, model input,
and prediction output is a numpy array. All ML libraries interoperate through
numpy. Version 2.1.0 is the minimum with Python 3.13 pre-built wheels.

**`pandas==2.2.3`**
Best tool for loading, cleaning, and transforming tabular data at scale.
Used to load parquet files, strip column whitespace, map labels, and handle
missing values before converting to numpy arrays.

**`scikit-learn==1.5.2`**
Provides Random Forest, StandardScaler, LabelEncoder, train_test_split,
and all evaluation metrics (F1, precision, recall, ROC-AUC, confusion matrix).
The most comprehensive general-purpose ML library in Python.

**`imbalanced-learn==0.12.4`**
Provides SMOTE (Synthetic Minority Oversampling Technique). Critical for this
dataset — without it, all models predict BENIGN and appear 85% accurate while
detecting zero attacks. SMOTE generates synthetic minority class samples by
interpolating between existing samples in feature space.

**`xgboost==2.1.1`**
Gradient boosted tree implementation. Consistently outperforms plain decision
trees and random forests on tabular classification tasks. The histogram-based
tree method (`tree_method=hist`) enables training on 2M+ samples without
excessive memory consumption.

**`torch==2.6.0`**
PyTorch for the LSTM model. Chosen over TensorFlow because of its more
Pythonic API, easier debugging with standard Python tools, and dominant
adoption in both research and industry as of 2025-2026. Version 2.6.0
is the minimum supporting Python 3.13.

**`pyarrow==16.1.0`**
Required to read the CICIDS2017 parquet files. Parquet is a columnar
binary format that loads 8x faster than CSV and uses 3x less disk space
for the same data.

### API Layer

**`fastapi==0.115.0`**
Modern async Python web framework. Auto-generates Swagger UI at `/docs`
from type annotations alone. Significantly faster than Flask due to async
request handling. Native Pydantic integration for automatic request validation.

**`uvicorn==0.30.6`**
ASGI server that runs FastAPI. The `[standard]` extras install `watchfiles`
for hot-reload during development and `websockets` for future WebSocket support.

**`pydantic==2.9.2`**
Validates all incoming API data before it reaches the ML models. If someone
sends a string where a float is expected, Pydantic rejects it automatically
with a clear error message. Also powers the response serialization.

**`pydantic-settings==2.5.2`**
Extension that reads configuration from `.env` files with full type validation.
Powers the `Settings` class in `config.py` — every setting has a type, a
default, and is loaded from the environment automatically.

**`sqlalchemy==2.0.35`**
ORM that lets us define `Alert` and `AnalysisLog` as Python classes instead
of raw SQL. The async engine allows database queries to run without blocking
the API event loop during concurrent requests.

**`aiosqlite==0.20.0`**
Async SQLite driver. Without this, every database read/write would block the
entire API thread while waiting for disk I/O, defeating the purpose of async.

**`greenlet==3.1.1`**
Required by SQLAlchemy's async engine on Python 3.13. Provides the coroutine
switching primitives that SQLAlchemy's async implementation depends on.

### Utilities

**`loguru==0.7.2`**
Structured coloured logging with one line of setup. Produces human-readable
coloured output in the terminal and structured log files simultaneously.
Replaces Python's verbose built-in `logging` module entirely.

**`python-dotenv==1.0.1`**
Loads variables from `.env` into the Python environment at startup. Keeps
secrets (database URLs, API keys) out of source code and version control.

**`tqdm==4.66.5`**
Progress bars. Wraps any Python iterator with a live progress bar in one line.
Used during CSV/parquet loading so training runs show meaningful progress.

**`httpx==0.27.2`**
Async HTTP client used in integration tests to make requests to the running
FastAPI server. The async version of the popular `requests` library.

**`pytest==8.3.3` + `pytest-asyncio==0.24.0`**
Standard Python testing framework with async support. Required because all
FastAPI routes and database operations are async functions.

---

## API Reference

Base URL: `http://localhost:8000`

### POST /api/detect
Submit a network flow for real-time threat analysis.

**Request:**
```json
{
  "features": {
    "SYN Flag Count": 850,
    "Flow Duration": 5000000,
    "Total Fwd Packets": 5000,
    "Flow Bytes/s": 9000000,
    "FIN Flag Count": 0
  },
  "source_ip": "192.168.1.100",
  "dest_ip": "10.0.0.1"
}
```

You may provide any subset of the 77 features.
Missing features default to 0.

**Response:**
```json
{
  "is_attack": true,
  "attack_type": "DoS",
  "confidence": 0.9821,
  "severity_score": 5,
  "severity_label": "Critical",
  "should_alert": true,
  "ensemble_votes": {"attack": 3, "total": 3},
  "model_results": {
    "rf":   {"label": "ATTACK", "confidence": 0.97, "is_attack": true},
    "xgb":  {"label": "DoS",   "confidence": 0.98, "is_attack": true},
    "lstm": {"label": "ATTACK", "confidence": 0.96, "is_attack": true}
  },
  "timestamp": "2026-03-30T14:30:00",
  "alert_id": "42"
}
```

---

### GET /api/alerts
Retrieve stored alerts.

**Query Parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `limit` | int | 50 | Max results (max 500) |
| `offset` | int | 0 | Pagination offset |
| `severity` | string | — | Filter: Critical / High / Medium / Low |
| `attack_type` | string | — | Filter: DoS / DDoS / BruteForce / etc. |
| `hours` | int | — | Only last N hours |
| `unacknowledged_only` | bool | false | Only unreviewed alerts |

**Response:**
```json
{
  "total": 342,
  "alerts": [
    {
      "id": 42,
      "timestamp": "2026-03-30T14:30:00",
      "attack_type": "DoS",
      "severity_label": "Critical",
      "severity_score": 5,
      "confidence": 0.9821,
      "source_ip": "192.168.1.100",
      "dest_ip": "10.0.0.1",
      "is_acknowledged": false
    }
  ]
}
```

---

### GET /api/stats
System-wide detection statistics.

**Response:**
```json
{
  "total_analyzed": 15420,
  "total_alerts": 342,
  "attack_rate": 0.0222,
  "by_attack_type": {
    "DoS": 180,
    "DDoS": 92,
    "BruteForce": 70
  },
  "by_severity": {
    "Critical": 272,
    "High": 70
  },
  "recent_24h": 28
}
```

---

### GET /api/model-report
Returns loaded model status and class names.

---

### GET /api/health
Engine health check.

**Response:**
```json
{
  "status": "ok",
  "version": "1.0.0",
  "engine": {
    "loaded": true,
    "models": {
      "random_forest": true,
      "xgboost": true,
      "lstm": true
    },
    "n_features": 77,
    "class_names": ["BENIGN", "Bot", "BruteForce", "DDoS",
                    "DoS", "Infiltration", "PortScan", "WebAttack"]
  }
}
```

---

### PATCH /api/alerts/{id}/acknowledge
Mark an alert as reviewed.

**Response:**
```json
{"id": 42, "acknowledged": true}
```

---

## Understanding the Features

Each feature in the detection request corresponds to a
real measurement from a network flow:

| Feature | Unit | What It Measures |
|---|---|---|
| `SYN Flag Count` | count | TCP connection initiation attempts |
| `FIN Flag Count` | count | TCP connection terminations |
| `RST Flag Count` | count | TCP connection resets (often port scan indicator) |
| `ACK Flag Count` | count | TCP acknowledgements |
| `Flow Duration` | microseconds | Total connection lifetime |
| `Total Fwd Packets` | count | Packets sent from source to destination |
| `Total Backward Packets` | count | Packets returned from destination |
| `Flow Bytes/s` | bytes/sec | Data transfer rate |
| `Flow Packets/s` | packets/sec | Packet transmission rate |
| `Bwd Packet Length Mean` | bytes | Average size of return packets |
| `Bwd Packet Length Std` | bytes | Variance in return packet sizes |
| `Idle Mean` | microseconds | Average idle time between flow activity |

**Providing more features = higher confidence predictions.**
The model was trained on all 77 features simultaneously.
Missing features are filled with 0, which may reduce confidence
but will not cause errors.

---

*Back to [README.md](README.md)*
*Setup instructions in [SETUP.md](SETUP.md)*

---

<div align="center">

**Author:** Rehan Khan

© 2026 Rehan Khan. All rights reserved.
Unauthorized copying, distribution, or modification of this project
without explicit written permission is prohibited.

See [SECURITY.md](SECURITY.md) for full legal terms.

</div>