import torch


# Build the Model
class HorsePrizeRegressor(torch.nn.Module):
    def __init__(self, in_features):
        super().__init__()
        self.net = torch.nn.Sequential(
            torch.nn.Linear(in_features, 32),
            torch.nn.ReLU(),
            torch.nn.Linear(32, 16),
            torch.nn.ReLU(),
            torch.nn.Linear(16, 1)
        )

    def forward(self, x):
        return self.net(x)
