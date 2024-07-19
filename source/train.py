import torch
import random 
import numpy as np
from torch import nn
import torchinfo
from torch.utils.tensorboard import SummaryWriter
import shutil
import os
from dvclive import Live
from utils.config import load_params
import utils.helpers
from model import NeuralNetwork
import time
import socket

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

def prepare_device(request):
    if request == "mps":
        if torch.backends.mps.is_available():
            device = torch.device("mps")
            print("Using MPS device")
        else:
            device = torch.device("cpu")
            print("MPS requested but not available. Using CPU device")
    elif request == "cuda":
        if torch.cuda.is_available():
            device = torch.device("cuda")
            print("Using CUDA device")
        else:
            device = torch.device("cpu")
            print("CUDA requested but not available. Using CPU device")
    else:
        device = torch.device("cpu")
        print("Using CPU device")
    return device


def train_epoch(dataloader, model, loss_fn, optimizer, device, live, writer, epoch):
    size = len(dataloader.dataset)
    num_batches = len(dataloader)
    train_loss = 0 
    model.train()
    for batch, (X, y) in enumerate(dataloader):
        X, y = X.to(device), y.to(device)
        pred = model(X)
        loss = loss_fn(pred, y)
        loss.backward()
        optimizer.step()
        optimizer.zero_grad()
        writer.add_scalar("Step_Loss/train", loss.item(), batch + epoch * len(dataloader))
        train_loss += loss.item()
        if batch % 100 == 0:
            loss_value = loss.item()
            current = (batch + 1) * len(X)
            print(f"loss: {loss_value:>7f}  [{current:>5d}/{size:>5d}]")
            live.log_metric("train: mse loss", loss_value)
            live.next_step() 
    train_loss /=  num_batches
    return train_loss
    

def test_epoch(dataloader, model, loss_fn, device, writer):
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
    return test_loss

def main():
    # Get the path to the tensorboard directory
    tustu_logs_path = os.environ.get('TUSTU_LOGS_PATH')
    if tustu_logs_path is None:
        raise EnvironmentError("The environment variable ‘TUSTU_LOGS_PATH’ is not set.")
    tensorboard_path = os.path.join(tustu_logs_path, 'tensorboard')
    if not os.path.exists(tensorboard_path):
        os.makedirs(tensorboard_path)

    # Get the hostname and the current time to identify the tensorboard log file to copy to experiment branch
    hostname = socket.gethostname()
    time_now = time.time()

    # Create a SummaryWriter object to write the tensorboard logs
    writer = SummaryWriter(tensorboard_path)

    # Load the parameters from the config file
    params = load_params()
    input_file = params.train.input_file
    name = params.train.name
    epochs = params.train.epochs
    train_mode = params.train.train_mode
    batch_size = params.train.batch_size
    input_size = params.preprocess.input_size
    random_seed = params.general.random_seed
    device_request = params.train.device

    # Set random seed for reproducibility
    random.seed(random_seed)
    np.random.seed(random_seed)
    torch.manual_seed(random_seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(random_seed)

    # Load preprocessed data
    data = torch.load(input_file)
    X_ordered_training = data['X_ordered_training']
    y_ordered_training = data['y_ordered_training']
    X_ordered_testing = data['X_ordered_testing']
    y_ordered_testing = data['y_ordered_testing']

    device = prepare_device(device_request)

    if not os.path.exists('models/checkpoints/'):
        os.makedirs('models/checkpoints/')

    learning_rate, conv1d_strides, conv1d_filters, hidden_units = get_train_mode_params(train_mode)

    model = NeuralNetwork(conv1d_filters, conv1d_strides, hidden_units).to(device)
    summary = torchinfo.summary(model, (1, 1, input_size), device=device)
    print(summary)
    sample_inputs = torch.randn(1, 1, input_size) 
    writer.add_graph(model, sample_inputs.to(device))

    loss_fn = nn.MSELoss(reduction='mean')
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

    training_dataset = torch.utils.data.TensorDataset(X_ordered_training, y_ordered_training)
    training_dataloader = torch.utils.data.DataLoader(training_dataset, batch_size=batch_size, shuffle=True)
    testing_dataset = torch.utils.data.TensorDataset(X_ordered_testing, y_ordered_testing)
    testing_dataloader = torch.utils.data.DataLoader(testing_dataset, batch_size=batch_size, shuffle=False)

    live = Live()  

    for t in range(epochs):
        print(f"Epoch {t+1}\n-------------------------------")
        epoch_loss_train = train_epoch(training_dataloader, model, loss_fn, optimizer, device, live, writer, epoch=t)
        epoch_loss_test = test_epoch(testing_dataloader, model, loss_fn, device, writer)
        writer.add_scalar("Epoch_Loss/train", epoch_loss_train, t)
        writer.add_scalar("Epoch_Loss/test", epoch_loss_test, t)
        # live.next_step()  # Indicate the end of an epoch
    
    writer.close()

    # Save the model
    torch.save(model.state_dict(), "models/checkpoints/" + name + ".pth")
    print("Saved PyTorch Model State to model.pth")

    # Copy the tensorboard log file with the closest timestamp into the exp-logs directory
    utils.helpers.copy_tensorboard_log(tensorboard_path, 'exp-logs', hostname, time_now)

    print("Done!")

if __name__ == "__main__":
    main()
