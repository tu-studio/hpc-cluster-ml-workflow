import torch
import random 
import numpy as np
from torch import nn
import torchinfo
from utils import logs, config
import os
from pathlib import Path
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

def set_random_seed(random_seed):
    if 'random' in globals():
        random.seed(random_seed)
    else:
        print("The 'random' package is not imported, skipping random seed.")

    if 'np' in globals():
        np.random.seed(random_seed)
    else:
        print("The 'numpy' package is not imported, skipping numpy seed.")

    if 'torch' in globals():
        torch.manual_seed(random_seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(random_seed)
        if torch.backends.mps.is_available():
            torch.mps.manual_seed(random_seed)
    else:
        print("The 'torch' package is not imported, skipping torch seed.")
    
    if 'tf' in globals():
        tf.random.set_seed(random_seed)
    else:
        print("The 'tensorflow' package is not imported, skipping tensorflow seed.")

    if 'scipy' in globals():
        scipy.random.seed(random_seed)
    else:
        print("The 'scipy' package is not imported, skipping scipy seed.")
    
    if 'sklearn' in globals():
        sklearn.utils.random.seed(random_seed)
    else:
        print("The 'sklearn' package is not imported, skipping sklearn seed.")



def train_epoch(dataloader, model, loss_fn, optimizer, device, writer, epoch):
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

def generate_audio_example(model, device, dataloader):
    print("Running audio prediction...")
    prediction = torch.zeros(0).to(device)
    target = torch.zeros(0).to(device)
    with torch.no_grad():
        for X, y in dataloader:
            X = X.to(device)
            y = y.to(device)
            predicted_batch = model(X)
            prediction = torch.cat((prediction, predicted_batch.flatten()), 0)
            target = torch.cat((target, y.flatten()), 0)
    audio_example = torch.cat((target, prediction), 0)
    return audio_example

def main():
    # Load the hyperparameters from the params yaml file into a Dictionary
    params = config.Params('params.yaml')

    input_size = params['general']['input_size']
    random_seed = params['general']['random_seed']
    epochs = params['train']['epochs']
    train_mode = params['train']['train_mode']
    batch_size = params['train']['batch_size']
    device_request = params['train']['device_request']

    # Define and create the path to the tensorboard logs directory in the source repository
    default_dir = config.get_env_variable('DEFAULT_DIR')
    dvc_exp_name = config.get_env_variable('DVC_EXP_NAME')   
    tensorboard_path = Path(f'{default_dir}/logs/tensorboard/{dvc_exp_name}')
    tensorboard_path.mkdir(parents=True, exist_ok=True)

    # Create a SummaryWriter object to write the tensorboard logs
    writer = logs.CustomSummaryWriter(log_dir=tensorboard_path)

    # Add hyperparameters and metrics to the hparams plugin of tensorboard
    metrics = {'Epoch_Loss/train': None, 'Epoch_Loss/test': None, 'Step_Loss/train': None}
    writer.add_hparams(hparam_dict=params.flattened_copy(), metric_dict=metrics, run_name=tensorboard_path)

    # Set a random seed for reproducibility across all devices
    set_random_seed(random_seed)

    # Load preprocessed data from the input file into the training and testing tensors
    input_file_path = Path('data/processed/data.pt')
    data = torch.load(input_file_path)
    X_ordered_training = data['X_ordered_training']
    y_ordered_training = data['y_ordered_training']
    X_ordered_testing = data['X_ordered_testing']
    y_ordered_testing = data['y_ordered_testing']

    # Prepare the requested device for training. Use cpu if the requested device is not available 
    device = prepare_device(device_request)

    # Get the hyperparameters for the training mode
    learning_rate, conv1d_strides, conv1d_filters, hidden_units = get_train_mode_params(train_mode)

    # Create the model
    model = NeuralNetwork(conv1d_filters, conv1d_strides, hidden_units).to(device)
    summary = torchinfo.summary(model, (1, 1, input_size), device=device)
    print(summary)

    # Add the model graph to the tensorboard logs
    sample_inputs = torch.randn(1, 1, input_size) 
    writer.add_graph(model, sample_inputs.to(device))

    # Define the loss function and the optimizer
    loss_fn = torch.nn.MSELoss(reduction='mean')
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

    # Create the dataloaders
    training_dataset = torch.utils.data.TensorDataset(X_ordered_training, y_ordered_training)
    training_dataloader = torch.utils.data.DataLoader(training_dataset, batch_size=batch_size, shuffle=True)
    testing_dataset = torch.utils.data.TensorDataset(X_ordered_testing, y_ordered_testing)
    testing_dataloader = torch.utils.data.DataLoader(testing_dataset, batch_size=batch_size, shuffle=False)

    # Get the rsync interval from the environment variables
    logs_intervall = config.get_env_variable('TUSTU_LOGS_INTERVALL')
    rsync_logs_enabled = config.get_env_variable('TUSTU_RSYNC_LOGS_ENABLED')
    default_dir =  config.get_env_variable('DEFAULT_DIR')
    tensorboard_host = config.get_env_variable('TUSTU_TENSORBOARD_HOST')
    project_name = config.get_env_variable('TUSTU_PROJECT_NAME')


    # Training loop
    for t in range(epochs):
        print(f"Epoch {t+1}\n-------------------------------")
        epoch_loss_train = train_epoch(training_dataloader, model, loss_fn, optimizer, device, writer, epoch=t)
        epoch_loss_test = test_epoch(testing_dataloader, model, loss_fn, device, writer)
        epoch_audio_example = generate_audio_example(model, device, testing_dataloader)
        # Every logs_intervall epochs, write the metrics to the tensorboard logs
        if t % int(logs_intervall) == 0:
            writer.add_scalar("Epoch_Loss/train", epoch_loss_train, t)
            writer.add_scalar("Epoch_Loss/test", epoch_loss_test, t)
            writer.add_audio("Audio_Pred/test", epoch_audio_example, t, sample_rate=44100)
            if rsync_logs_enabled:
                writer.flush()  # Ensure all logs are written to disk
                # Add your rsync command here to sync logs to the SSH server
                tensorboard_path = Path(f'{default_dir}/logs/tensorboard/{dvc_exp_name}')
                os.system(f"rsync -avz {tensorboard_path} {tensorboard_host}:Data/{project_name}")


    writer.close()

    # Save the model checkpoint
    output_file_path = Path('models/checkpoints/model.pth')
    output_file_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), output_file_path)
    print("Saved PyTorch Model State to model.pth")

    print("Done with the training stage!")

if __name__ == "__main__":
    main()
