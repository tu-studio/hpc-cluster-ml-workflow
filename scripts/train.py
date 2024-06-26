import torch
from torch import nn
import torchinfo
import os
from source.config import load_params
from model import NeuralNetwork

def get_train_mode_params(train_mode):
    if train_mode == 0:
        learning_rate = 0.01
        conv1d_strides = 12
        conv1d_filters = 16
        hidden_units = 36
    elif train_mode == 1:
        learning_rate = 0.01
        conv1d_strides = 4
        conv1d_filters = 36
        hidden_units = 64
    else:
        learning_rate = 0.0005
        conv1d_strides = 3
        conv1d_filters = 36
        hidden_units = 96
    return learning_rate, conv1d_strides, conv1d_filters, hidden_units

def prepare_device():
    cpu_device = torch.device("cpu")
    device = cpu_device
    if torch.backends.mps.is_available():
        device = torch.device("mps")
    print(f"Using {device} device")
    return device

def create_dataloaders(X_ordered_training, y_ordered_training, X_ordered_testing, y_ordered_testing, batch_size):
    training_dataset = torch.utils.data.TensorDataset(X_ordered_training, y_ordered_training)
    training_dataloader = torch.utils.data.DataLoader(training_dataset, batch_size=batch_size, shuffle=True)

    testing_dataset = torch.utils.data.TensorDataset(X_ordered_testing, y_ordered_testing)
    testing_dataloader = torch.utils.data.DataLoader(testing_dataset, batch_size=batch_size, shuffle=False)

    return training_dataloader, testing_dataloader

def train_epoch(dataloader, model, loss_fn, optimizer, device):
    size = len(dataloader.dataset)
    model.train()
    for batch, (X, y) in enumerate(dataloader):
        X, y = X.to(device), y.to(device)
        pred = model(X)
        loss = loss_fn(pred, y)
        loss.backward()
        optimizer.step()
        optimizer.zero_grad()
        if batch % 100 == 0:
            loss, current = loss.item(), (batch + 1) * len(X)
            print(f"loss: {loss:>7f}  [{current:>5d}/{size:>5d}]")

def test_epoch(dataloader, model, loss_fn, device):
    num_batches = len(dataloader)
    model.eval()
    test_loss = 0
    with torch.no_grad():
        for X, y in dataloader:
            X, y = X.to(device), y.to(device)
            pred = model(X)
            test_loss += loss_fn(pred, y).item()
    test_loss /= num_batches
    print(f"Test Error: \n Avg loss: {test_loss:>8f} \n")

def main():
    params = load_params()
    input_file = params.train.input_file
    name = params.train.name
    epochs = params.train.epochs
    train_mode = params.train.train_mode
    batch_size = params.train.batch_size
    input_size = params.preprocess.input_size

    # Load preprocessed data
    data = torch.load(input_file)
    X_ordered_training = data['X_ordered_training']
    y_ordered_training = data['y_ordered_training']
    X_ordered_testing = data['X_ordered_testing']
    y_ordered_testing = data['y_ordered_testing']

    device = prepare_device()

    if not os.path.exists('models/checkpoints/'):
        os.makedirs('models/checkpoints/')

    learning_rate, conv1d_strides, conv1d_filters, hidden_units = get_train_mode_params(train_mode)

    model = NeuralNetwork(conv1d_filters, conv1d_strides, hidden_units).to(device)
    summary = torchinfo.summary(model, (1, 1, input_size), device=device)
    print(summary)

    loss_fn = nn.MSELoss(reduction='mean')
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

    training_dataset = torch.utils.data.TensorDataset(X_ordered_training, y_ordered_training)
    training_dataloader = torch.utils.data.DataLoader(training_dataset, batch_size=batch_size, shuffle=True)
    testing_dataset = torch.utils.data.TensorDataset(X_ordered_testing, y_ordered_testing)
    testing_dataloader = torch.utils.data.DataLoader(testing_dataset, batch_size=batch_size, shuffle=False)

    for t in range(epochs):
        print(f"Epoch {t+1}\n-------------------------------")
        train_epoch(training_dataloader, model, loss_fn, optimizer, device)
        test_epoch(testing_dataloader, model, loss_fn, device)
    print("Done!")

    # Save the model
    torch.save(model.state_dict(), "models/checkpoints/" + name + ".pth")
    print("Saved PyTorch Model State to model.pth")

if __name__ == "__main__":
    main()
