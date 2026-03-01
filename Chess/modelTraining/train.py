# train.py
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
import glob
import random
from tqdm import tqdm

class ChessNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(12, 32, 3, padding=1), nn.BatchNorm2d(32), nn.ReLU(),
            nn.Conv2d(32, 64, 3, padding=1), nn.BatchNorm2d(64), nn.ReLU(),
            nn.Conv2d(64, 64, 3, padding=1), nn.BatchNorm2d(64), nn.ReLU(),
        )
        self.fc = nn.Sequential(
            nn.Flatten(),
            nn.Linear(64*8*8, 256), nn.ReLU(), nn.Dropout(0.3),
            nn.Linear(256, 64),     nn.ReLU(),
            nn.Linear(64, 1),       nn.Tanh()
        )
    def forward(self, x):
        return self.fc(self.conv(x)).squeeze(1)

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}")

model     = ChessNet().to(device)
optimizer = torch.optim.Adam(model.parameters(), lr=1e-3, weight_decay=1e-4)
scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=3, gamma=0.5)
criterion = nn.MSELoss()

all_chunks = list(zip(sorted(glob.glob('dataset_X_*.npy')),
                      sorted(glob.glob('dataset_y_*.npy'))))
random.shuffle(all_chunks)
val_chunks   = all_chunks[:2]
train_chunks = all_chunks[2:]
print(f"Train chunks: {len(train_chunks)}, Val chunks: {len(val_chunks)}")

best_val_loss = float('inf')
EPOCHS   = 15
patience = 3
no_improve = 0

for epoch in range(EPOCHS):
    model.train()
    train_loss    = 0
    train_batches = 0

    chunk_bar = tqdm(train_chunks, total=len(train_chunks),
                     desc=f"Epoch {epoch+1}/{EPOCHS}", unit="chunk")

    for x_file, y_file in chunk_bar:
        X = torch.tensor(np.load(x_file))
        y = torch.tensor(np.load(y_file))
        loader = DataLoader(TensorDataset(X, y), batch_size=1024, shuffle=True)
        for xb, yb in loader:
            xb, yb = xb.to(device), yb.to(device)
            pred = model(xb)
            loss = criterion(pred, yb)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            train_loss    += loss.item()
            train_batches += 1
        chunk_bar.set_postfix(loss=f"{train_loss/train_batches:.4f}")

    # walidacja na stałych 2 chunkach
    model.eval()
    val_loss    = 0
    val_batches = 0
    with torch.no_grad():
        for x_file, y_file in val_chunks:
            X = torch.tensor(np.load(x_file))
            y = torch.tensor(np.load(y_file))
            for xb, yb in DataLoader(TensorDataset(X, y), batch_size=1024):
                xb, yb = xb.to(device), yb.to(device)
                val_loss   += criterion(model(xb), yb).item()
                val_batches += 1

    train_loss /= train_batches
    val_loss   /= val_batches
    scheduler.step()

    print(f"Epoch {epoch+1:2d} | train: {train_loss:.4f} | val: {val_loss:.4f}")

    if val_loss < best_val_loss:
        best_val_loss = val_loss
        no_improve    = 0
        torch.save(model.state_dict(), 'chess_model_hard.pth')
        print("  -> saved best model")
    else:
        no_improve += 1
        print(f"  no improvement ({no_improve}/{patience})")
        if no_improve >= patience:
            print("Early stopping!")
            break

print(f"Training complete! Best val loss: {best_val_loss:.4f}")