\# Setup Guide — ThreatNet IDS



Complete installation and usage guide for ThreatNet.



\---



\## Table of Contents



\- \[Prerequisites](#prerequisites)

\- \[Installation](#installation)

\- \[Dataset Download](#dataset-download)

\- \[Preprocessing](#preprocessing)

\- \[Training the Models](#training-the-models)

\- \[Running the System](#running-the-system)

\- \[Testing the Detection Engine](#testing-the-detection-engine)

\- \[Environment Variables](#environment-variables)

\- \[Troubleshooting](#troubleshooting)



\---



\## Prerequisites



| Requirement | Minimum Version | Check Command |

|---|---|---|

| Python | 3.13 | `python --version` |

| Node.js | 18.0 | `node --version` |

| Git | any | `git --version` |

| RAM | 8GB | — |

| Disk Space | 5GB free | — |



\---



\## Installation



\### 1. Clone the Repository

```bash

git clone https://github.com/YOUR\_USERNAME/ai-threat-detection.git

cd ai-threat-detection

```



\### 2. Create Virtual Environment

```bash

python -m venv venv

```



Activate it:



\*\*Windows (PowerShell):\*\*

```powershell

venv\\Scripts\\activate

```



\*\*macOS / Linux:\*\*

```bash

source venv/bin/activate

```



You should see `(venv)` at the start of your terminal prompt.



\### 3. Install Python Dependencies

```bash

pip install -r requirements.txt --prefer-binary

```



The `--prefer-binary` flag ensures pre-built wheels are used

and avoids compilation issues on Windows with Python 3.13.



> \*\*Note:\*\* PyTorch (\~2.5GB) will take several minutes to download.



\### 4. Install Frontend Dependencies

```bash

cd frontend

npm install

cd ..

```



\### 5. Set Up Environment Variables

```bash

\# Windows

copy .env.example .env



\# macOS / Linux

cp .env.example .env

```



The defaults in `.env.example` work out of the box for local development.

Edit `.env` only if you need to change ports or thresholds.



\---



\## Dataset Download



\### Option A — Kaggle (Recommended, Real Data)



1\. Create a free account at \[kaggle.com](https://www.kaggle.com)

2\. Go to Settings → API → Create New Token

3\. You will receive a token — set it as an environment variable:



\*\*Windows:\*\*

```powershell

$env:KAGGLE\_API\_TOKEN="your\_token\_here"

```



\*\*macOS / Linux:\*\*

```bash

export KAGGLE\_API\_TOKEN="your\_token\_here"

```



4\. Install the Kaggle CLI and download:

```bash

pip install kaggle

kaggle datasets download -d dhoogla/cicids2017 -p data/raw --unzip

```



This downloads \~227MB and extracts 8 parquet files totaling \~2.3M flows.



\---



\### Option B — Synthetic Data (Quick Testing)



If you want to test the pipeline without downloading the real dataset:

```bash

python -m src.data.downloader

```



Type `y` when prompted. This generates 50,000 synthetic flows with

realistic statistical patterns for each attack type. Sufficient for

testing but not for final model evaluation.



> \*\*Important:\*\* Always retrain on the real dataset before presenting

> results academically or in a portfolio.



\---



\## Preprocessing



Run the full preprocessing pipeline:

```bash

python -m src.data.preprocessor

```



\*\*What this does:\*\*

1\. Loads all parquet/CSV files from `data/raw/`

2\. Strips whitespace from column names

3\. Removes inf, NaN, and duplicate rows

4\. Maps raw labels to 8 canonical categories

5\. Applies StandardScaler (fit on train, transform both)

6\. Applies SMOTE to balance minority attack classes

7\. Saves numpy arrays, scaler, label encoder, and metadata to `data/processed/`



\*\*Expected output:\*\*

```

Total: 2,313,810 rows

After cleaning: 2,231,806 rows

After SMOTE: 3,032,500 training samples

Test samples: 446,362

Classes: \['BENIGN', 'Bot', 'BruteForce', 'DDoS', 'DoS',

&#x20;         'Infiltration', 'PortScan', 'WebAttack']

```



\---



\## Training the Models



Train each model separately. Run them in this order:



\### Random Forest (\~8 minutes)

```bash

python -m src.ml.train\_rf

```

Trains a 200-tree binary classifier. Saves to `data/models/random\_forest.pkl`.



\### XGBoost (\~6 minutes)

```bash

python -m src.ml.train\_xgb

```

Trains a 300-tree 8-class classifier. Saves to `data/models/xgboost.pkl`.



\### LSTM (\~3.5 hours on CPU)

```bash

python -m src.ml.train\_lstm

```

Trains a 2-layer LSTM on 3M sequences of 20 flows each.

Saves to `data/models/lstm.pt`.



> \*\*GPU Note:\*\* If you have an NVIDIA GPU with CUDA installed,

> PyTorch will automatically use it. Training time reduces to \~20 minutes.

> Check with: `python -c "import torch; print(torch.cuda.is\_available())"`



> \*\*Skip LSTM:\*\* The system operates normally with just RF and XGBoost.

> LSTM adds the deep learning component but is not required for the API to function.



\---



\## Running the System



You need \*\*two terminals\*\* running simultaneously.

Make sure your virtual environment is activated in the first terminal.



\### Terminal 1 — API Server

```bash

uvicorn src.api.main:app --reload --port 8000

```



Wait until you see:

```

Detection Engine ready — 3/3 models loaded

Application startup complete.

Uvicorn running on http://127.0.0.1:8000

```



\### Terminal 2 — React Dashboard

```bash

cd frontend

npm run dev

```



Wait until you see:

```

VITE v5.x  ready

→  Local:   http://localhost:5173/

```



\### Open in Browser



| URL | Description |

|---|---|

| `http://localhost:5173` | Live Dashboard |

| `http://localhost:8000/docs` | Swagger API Documentation |

| `http://localhost:8000/api/health` | Engine Health Check |



\---



\## Testing the Detection Engine



Run the integration test to verify all models load and predict correctly:

```bash

python -m tests.test\_engine

```



Expected output:

```

Detection Engine ready — 3/3 models loaded



\--- Normal Traffic ---

&#x20; Label      : BENIGN

&#x20; Is Attack  : False

&#x20; Confidence : 0.9953



\--- DoS Attack ---

&#x20; Label      : BruteForce

&#x20; Is Attack  : True

&#x20; Confidence : 0.8389

&#x20; Votes      : {'attack': 3, 'total': 3}

```



\---



\## Environment Variables



All settings live in `.env`. Here is what each one controls:



| Variable | Default | Description |

|---|---|---|

| `APP\_NAME` | AI Threat Detection System | Application name |

| `APP\_VERSION` | 1.0.0 | Version string |

| `DEBUG` | true | Enables debug logging |

| `DATABASE\_URL` | sqlite+aiosqlite:///./data/alerts.db | SQLite path |

| `API\_HOST` | 0.0.0.0 | API bind address |

| `API\_PORT` | 8000 | API port |

| `CORS\_ORIGINS` | localhost:5173,localhost:3000 | Allowed frontend origins |

| `RANDOM\_SEED` | 42 | Reproducibility seed |

| `TEST\_SIZE` | 0.2 | Train/test split ratio |

| `SMOTE\_ENABLED` | true | Toggle SMOTE balancing |

| `ALERT\_CONFIDENCE\_MIN` | 0.75 | Minimum confidence to raise alert |

| `HIGH\_SEVERITY\_THRESHOLD` | 0.92 | Confidence level for severity boost |



\---



\## Troubleshooting



\### `pip install` fails with compilation errors

```bash

pip install -r requirements.txt --prefer-binary

```

The `--prefer-binary` flag prevents pip from trying to compile packages from source.



\### `greenlet` not found error

```bash

pip install greenlet

```



\### Port 8000 already in use

```bash

uvicorn src.api.main:app --reload --port 8001

```

Update `CORS\_ORIGINS` in `.env` accordingly.



\### LSTM training runs out of memory

Reduce batch size in `src/ml/models/lstm\_model.py`:

```python

BATCH\_SIZE = 128   # default is 256

```



\### `kaggle` command not recognized

```bash

pip install kaggle

\# Then set your API token before running the download command

```



\### Models not found on API startup

Make sure you have trained all models before starting the API:

```bash

python -m src.ml.train\_rf

python -m src.ml.train\_xgb

python -m src.ml.train\_lstm

```



\---



\*Back to \[README.md](README.md)\*



\---



<div align="center">



\*\*Author:\*\* Rehan Khan



© 2026 Rehan Khan. All rights reserved.

Unauthorized copying, distribution, or modification of this project

without explicit written permission is prohibited.



</div>

