import os
import glob
import pandas as pd
import numpy as np
import torch
from torch import nn
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split
from torchsummary import summary
from tqdm import tqdm
from horse_prize_regressor import HorsePrizeRegressor


save_dir = "checkpoints"
os.makedirs(save_dir, exist_ok=True)


BATCH_SIZE = 4
EPOCHS = 100


# Load data
df = pd.read_csv('output.csv')

# Define features and target
target = 'careerPrizeMoney'
features = [col for col in df.columns if col != target]

X = df[features].values.astype(np.float32)
y = df[target].values.astype(np.float32).reshape(-1, 1)

# Train/test split
X_train, X_val, y_train, y_val = train_test_split(
    X, y, test_size=0.2, random_state=42)


# Define Dataset
class HorseDataset(Dataset):
    def __init__(self, X, y):
        self.X = torch.tensor(X, dtype=torch.float32)
        self.y = torch.tensor(y, dtype=torch.float32)

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]


train_ds = HorseDataset(X_train, y_train)
val_ds = HorseDataset(X_val, y_val)

train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True)
val_loader = DataLoader(val_ds, batch_size=BATCH_SIZE)


model = HorsePrizeRegressor(X_train.shape[1])
summary(model, input_size=(X_train.shape[1],))


device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = model.to(device)

# Training Setup
criterion = nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)

# Train
best_val_loss = float('inf')  # Initialize best validation loss
for epoch in range(EPOCHS):
    model.train()
    train_bar = tqdm(
        train_loader, desc=f"Epoch {epoch+1} [Train]", leave=False)
    for xb, yb in train_bar:
        xb, yb = xb.to(device), yb.to(device)
        pred = model(xb)
        loss = criterion(pred, yb)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        train_bar.set_postfix(loss=loss.item())

    # Validation
    model.eval()
    val_losses = []
    val_bar = tqdm(val_loader, desc=f"Epoch {epoch+1} [Eval]", leave=False)
    with torch.no_grad():
        for xb, yb in val_bar:
            xb, yb = xb.to(device), yb.to(device)
            pred = model(xb)
            batch_loss = criterion(pred, yb).item()
            val_losses.append(batch_loss)
            val_bar.set_postfix(val_loss=batch_loss)
    mean_val_loss = np.mean(val_losses)
    print(f'Epoch {epoch+1}, Val Loss: {mean_val_loss:.4f}')

    # Save model if validation loss improves
    if mean_val_loss < best_val_loss:
        best_val_loss = mean_val_loss
        # Save model with epoch and loss in filename
        save_path = os.path.join(
            save_dir, f"horse_epoch_{epoch+1}_loss_{mean_val_loss:.4f}.pth")
        torch.save(model.state_dict(), save_path)
        print(f"  Saved new best model: {save_path}")

        # --- Keep only the 10 most recent saved models ---
        saved_models = sorted(
            glob.glob(os.path.join(save_dir, "horse_*.pth")),
            key=os.path.getmtime,  # sort by modification time
            reverse=True           # newest first
        )
        # Delete older files if more than 10
        for old_model in saved_models[5:]:
            os.remove(old_model)
            print(f"  Deleted old model: {old_model}")
