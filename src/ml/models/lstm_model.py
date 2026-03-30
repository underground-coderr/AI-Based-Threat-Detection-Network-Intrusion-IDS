import numpy as np
import torch
import torch.nn as nn
from pathlib import Path
from torch.utils.data import DataLoader, TensorDataset
from src.utils.config import settings
from src.utils.logger import logger

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


class LSTMNet(nn.Module):

    def __init__(self, input_size: int, hidden_size: int = 128,
                 num_layers: int = 2, num_classes: int = 2, dropout: float = 0.3):
        super().__init__()
        self.hidden_size = hidden_size
        self.num_layers  = num_layers

        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0.0,
        )
        self.classifier = nn.Sequential(
            nn.Linear(hidden_size, 64),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(64, num_classes),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        out, _ = self.lstm(x, (h0, c0))
        return self.classifier(out[:, -1, :])


class LSTMModel:

    SEQ_LEN    = 20
    BATCH_SIZE = 256
    EPOCHS     = 20
    LR         = 1e-3

    def __init__(self, input_size: int = 69):
        self.input_size = input_size
        self.net        = None

    def _build_sequences(self, X: np.ndarray, y: np.ndarray):
        seq_X, seq_y = [], []
        for i in range(len(X) - self.SEQ_LEN):
            seq_X.append(X[i: i + self.SEQ_LEN])
            seq_y.append(y[i + self.SEQ_LEN - 1])
        return np.array(seq_X, dtype=np.float32), np.array(seq_y, dtype=np.int64)

    def train(self, X_train: np.ndarray, y_train: np.ndarray):
        logger.info(f"Building sequences (seq_len={self.SEQ_LEN})...")
        seq_X, seq_y = self._build_sequences(X_train, y_train)
        logger.info(f"Training LSTM on {len(seq_X):,} sequences | device={DEVICE}")

        self.net = LSTMNet(input_size=self.input_size).to(DEVICE)

        dataset = TensorDataset(
            torch.tensor(seq_X),
            torch.tensor(seq_y),
        )
        loader = DataLoader(dataset, batch_size=self.BATCH_SIZE, shuffle=True)

        criterion = nn.CrossEntropyLoss()
        optimizer = torch.optim.Adam(self.net.parameters(), lr=self.LR)
        scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=7, gamma=0.5)

        self.net.train()
        for epoch in range(1, self.EPOCHS + 1):
            total_loss, correct, total = 0.0, 0, 0

            for Xb, yb in loader:
                Xb, yb = Xb.to(DEVICE), yb.to(DEVICE)
                optimizer.zero_grad()
                out  = self.net(Xb)
                loss = criterion(out, yb)
                loss.backward()
                nn.utils.clip_grad_norm_(self.net.parameters(), max_norm=1.0)
                optimizer.step()

                total_loss += loss.item() * len(yb)
                correct    += (out.argmax(1) == yb).sum().item()
                total      += len(yb)

            scheduler.step()
            acc = correct / total
            avg = total_loss / total

            if epoch % 5 == 0 or epoch == 1:
                logger.info(f"  Epoch {epoch:>2}/{self.EPOCHS} | loss={avg:.4f} | acc={acc:.4f}")

        logger.success("LSTM training complete")
        return self

    def _batch_predict(self, seq_X: np.ndarray) -> np.ndarray:
        self.net.eval()
        dataset = TensorDataset(torch.tensor(seq_X, dtype=torch.float32))
        loader  = DataLoader(dataset, batch_size=self.BATCH_SIZE * 2, shuffle=False)
        preds   = []
        with torch.no_grad():
            for (Xb,) in loader:
                out = self.net(Xb.to(DEVICE))
                preds.extend(out.argmax(1).cpu().numpy().tolist())
        return np.array(preds)

    def predict_single(self, features: np.ndarray) -> dict:
        self.net.eval()
        seq = np.tile(features, (self.SEQ_LEN, 1)).reshape(1, self.SEQ_LEN, -1)
        tensor = torch.tensor(seq, dtype=torch.float32).to(DEVICE)
        with torch.no_grad():
            logits = self.net(tensor)
            proba  = torch.softmax(logits, dim=-1).cpu().numpy()[0]
        pred = int(np.argmax(proba))
        return {
            "prediction":   pred,
            "label":        "ATTACK" if pred == 1 else "BENIGN",
            "confidence":   float(proba[pred]),
            "proba_benign": float(proba[0]),
            "proba_attack": float(proba[1]),
            "is_attack":    pred == 1,
            "model":        "LSTM",
        }

    def evaluate(self, X_test: np.ndarray, y_test: np.ndarray) -> dict:
        from sklearn.metrics import classification_report, f1_score
        seq_X, seq_y = self._build_sequences(X_test, y_test)
        y_pred = self._batch_predict(seq_X)
        f1     = f1_score(seq_y, y_pred, average="binary", zero_division=0)
        logger.info("\n" + classification_report(
            seq_y, y_pred, target_names=["BENIGN", "ATTACK"]
        ))
        return {"f1": float(f1)}

    def save(self, path: Path = None) -> Path:
        if path is None:
            path = settings.models_dir / "lstm.pt"
        path.parent.mkdir(parents=True, exist_ok=True)
        torch.save({
            "net_state":  self.net.state_dict(),
            "input_size": self.input_size,
            "seq_len":    self.SEQ_LEN,
        }, path)
        logger.success(f"LSTM saved → {path}")
        return path

    @classmethod
    def load(cls, path: Path = None):
        if path is None:
            path = settings.models_dir / "lstm.pt"
        ckpt = torch.load(path, map_location=DEVICE)
        obj  = cls(input_size=ckpt["input_size"])
        obj.SEQ_LEN = ckpt["seq_len"]
        obj.net     = LSTMNet(input_size=obj.input_size).to(DEVICE)
        obj.net.load_state_dict(ckpt["net_state"])
        obj.net.eval()
        logger.info(f"LSTM loaded from {path}")
        return obj