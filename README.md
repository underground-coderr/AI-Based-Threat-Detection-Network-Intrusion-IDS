<div align="center">

<img src="https://img.shields.io/badge/ThreatNet-IDS%20v1.0-00d4ff?style=for-the-badge" />

# ThreatNet — AI-Based Network Intrusion Detection System

![Python](https://img.shields.io/badge/Python-3.13-blue?style=flat-square&logo=python)
![PyTorch](https://img.shields.io/badge/PyTorch-2.6-red?style=flat-square&logo=pytorch)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi)
![React](https://img.shields.io/badge/React-18.3-61dafb?style=flat-square&logo=react)
![XGBoost](https://img.shields.io/badge/XGBoost-2.1-orange?style=flat-square)
![Dataset](https://img.shields.io/badge/Dataset-CICIDS2017-purple?style=flat-square)
![License](https://img.shields.io/badge/License-All%20Rights%20Reserved-red?style=flat-square)

**A production-grade, end-to-end AI system for real-time network intrusion detection.**
Trained on 2.3 million real network flows from the CICIDS2017 dataset using an ensemble
of Random Forest, XGBoost, and LSTM models — served through a REST API with a live dashboard.

</div>

---

## What Is This Project

ThreatNet is a full-stack AI security system that detects network intrusions in real time.
It ingests network flow data — statistical summaries of network connections — and classifies
them as either benign traffic or one of 7 attack types using an ensemble of three machine
learning models. Detected threats are stored, scored by severity, and visualized on a
live React dashboard.

This project was built for two purposes:

- **Cybersecurity Portfolio** — demonstrates practical knowledge of intrusion detection
  systems, network traffic analysis, threat classification, and API development
- **Machine Learning Course** — demonstrates supervised learning, class imbalance handling,
  multi-model comparison, deep learning with sequential data, and production ML deployment

---

## Why This Matters

Traditional signature-based IDS tools like Snort can only detect known attacks by matching
traffic against a fixed rule database. They fail completely against zero-day exploits and
novel attack variants. AI-based detection learns the statistical fingerprint of attack
behavior from real data — making it capable of flagging attacks it has never explicitly seen.

### Attacks Detected

| Attack Type | Description | Severity |
|---|---|---|
| **DoS** | Flooding a target to cause denial of service | High |
| **DDoS** | Distributed flooding from multiple sources | Critical |
| **PortScan** | Probing for open ports and services | Low |
| **BruteForce** | Credential cracking via SSH or FTP | Medium |
| **WebAttack** | SQL injection, XSS, web-based brute force | Medium |
| **Bot** | Compromised machine contacting C&C server | High |
| **Infiltration** | Authorized-looking malicious lateral movement | Critical |

---

## System Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                        DATA LAYER                           │
│                                                             │
│  CICIDS2017 (2.3M flows) → Preprocessor → 77 Features      │
└───────────────────────────────┬─────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────┐
│                         ML LAYER                            │
│                                                             │
│  ┌──────────────┐  ┌─────────────┐  ┌───────────────────┐  │
│  │ Random Forest│  │   XGBoost   │  │       LSTM        │  │
│  │   F1: 0.996  │  │  F1: 0.937  │  │    F1: 0.983      │  │
│  └──────┬───────┘  └──────┬──────┘  └─────────┬─────────┘  │
│         └────────────────▼──────────────────┘             │
│                  Ensemble Voting Engine                     │
└───────────────────────────────┬─────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────┐
│                        API LAYER                            │
│                                                             │
│   FastAPI :8000  →  Detection Engine  →  SQLite Database   │
└───────────────────────────────┬─────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────┐
│                     DASHBOARD LAYER                         │
│                                                             │
│   React :5173  →  Live Charts  →  Alerts  →  Detect UI    │
└─────────────────────────────────────────────────────────────┘
```

---

## How It Works

### Step 1 — Data Ingestion
Network traffic is converted into flow records. Each flow summarizes one connection
using 77 statistical features: packet counts, byte rates, flag counts, inter-arrival
times, and more.

### Step 2 — Preprocessing Pipeline
```
Raw Parquet/CSV
      │
      ├── Strip whitespace from column names
      ├── Drop identifier columns (IP, port, timestamp)
      ├── Replace inf / NaN values
      ├── Remove duplicate rows
      ├── Encode labels into 8 categories
      ├── Train/test split — 80/20 stratified
      ├── StandardScaler — normalize all features
      └── SMOTE — oversample minority attack classes
```

### Step 3 — Parallel Model Inference
```
Network Flow (77 features)
        │
        ├──→ Random Forest ──→ BENIGN / ATTACK
        │
        ├──→ XGBoost ──→ BENIGN / DoS / DDoS / BruteForce
        │                  PortScan / WebAttack / Bot / Infiltration
        │
        └──→ LSTM (20-flow sequence) ──→ BENIGN / ATTACK
```

### Step 4 — Ensemble Voting
```
RF     → ATTACK   ✓
XGB    → DoS      ✓   (is_attack = True)
LSTM   → ATTACK   ✓

Votes  : 3 / 3 attack
Verdict: ATTACK
Label  : DoS (from XGBoost — most specific)
Confidence: 0.9821
```

### Step 5 — Severity Scoring
```
PortScan     → base 2  → Low / Medium
BruteForce   → base 3  → Medium / High
WebAttack    → base 3  → Medium / High
DoS          → base 4  → High / Critical
Bot          → base 4  → High / Critical
DDoS         → base 5  → Critical
Infiltration → base 5  → Critical

If confidence > 0.92 → severity bumped up one level
If BENIGN           → severity = 0 (None)
```

### Step 6 — Alert & Dashboard
```
confidence ≥ 0.75 + ensemble says attack
          │
          └──→ Alert saved to SQLite
                    │
                    └──→ React dashboard polls /api/alerts
                         every 5-10 seconds and updates live
```

---

## Project Structure
```
ai-threat-detection/
│
├── data/                        # Git-ignored — too large for Git
│   ├── raw/                     # CICIDS2017 parquet files
│   ├── processed/               # Cleaned numpy arrays + scaler
│   └── models/                  # Trained model files (.pkl, .pt)
│
├── src/
│   ├── data/
│   │   ├── downloader.py        # Dataset setup + synthetic generator
│   │   └── preprocessor.py      # Full preprocessing pipeline
│   ├── ml/
│   │   ├── models/
│   │   │   ├── random_forest.py
│   │   │   ├── xgboost_model.py
│   │   │   └── lstm_model.py
│   │   ├── train_rf.py
│   │   ├── train_xgb.py
│   │   ├── train_lstm.py
│   │   └── detection_engine.py  # Ensemble + severity scoring
│   ├── api/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── database.py          # SQLAlchemy + aiosqlite
│   │   ├── models.py            # Pydantic schemas
│   │   └── routes/
│   │       ├── detect.py        # POST /api/detect
│   │       ├── alerts.py        # GET /api/alerts
│   │       └── stats.py         # GET /api/stats
│   └── utils/
│       ├── config.py            # Settings from .env
│       └── logger.py            # Loguru setup
│
├── frontend/                    # React dashboard
│   └── src/
│       ├── pages/               # Overview, Alerts, Detect, Models
│       ├── components/          # Sidebar, StatCard
│       ├── hooks/               # usePolling
│       └── utils/               # api.js, helpers.js
│
├── tests/
│   └── test_engine.py
│
├── README.md                    # You are here
├── SETUP.md                     # Installation and running guide
├── MODELS.md                    # Dataset, model details, API reference
├── SECURITY.md                  # Security policy and legal
├── requirements.txt
└── .gitignore
```

---

## Documentation

| Document | Description |
|---|---|
| [SETUP.md](SETUP.md) | Installation, dataset download, training, running |
| [MODELS.md](MODELS.md) | Dataset details, model architecture, performance metrics, API reference |
| [SECURITY.md](SECURITY.md) | Security policy, responsible disclosure, legal |

---

## Dashboard Preview

The dashboard has four pages:

- **Overview** — Live KPI cards, attack distribution chart, severity breakdown, recent alerts table
- **Alerts** — Filterable full alert history with acknowledge functionality
- **Detect** — Submit any network flow manually and see all 3 model results instantly
- **Models** — F1 scores, accuracy bars, feature list, training configuration

---

## Tech Stack

| Layer | Technology |
|---|---|
| ML Models | scikit-learn · XGBoost · PyTorch |
| API | FastAPI · Uvicorn · SQLAlchemy · SQLite |
| Dashboard | React · Recharts · Vite |
| Data | pandas · numpy · imbalanced-learn (SMOTE) |
| Logging | Loguru |
| Validation | Pydantic |

Full dependency rationale in [MODELS.md](MODELS.md).

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit with clear messages
4. Test: `python -m tests.test_engine`
5. Open a Pull Request

### Ideas
- CICFlowMeter integration for live traffic capture
- WebSocket push for real-time dashboard updates
- Docker + docker-compose deployment
- Model retraining via API endpoint
- Expanded pytest coverage

---

---

*For installation instructions see [SETUP.md](SETUP.md)*
*For model details and API reference see [MODELS.md](MODELS.md)*
*For security policy see [SECURITY.md](SECURITY.md)*

---

<div align="center">

**Author:** Rehan Khan

Built as a 6th semester Machine Learning course project and Cybersecurity Portfolio piece.

© 2026 Rehan Khan. All rights reserved.
Unauthorized copying, distribution, or modification of this project
without explicit written permission is prohibited.

See [SECURITY.md](SECURITY.md) for full legal terms.

</div>