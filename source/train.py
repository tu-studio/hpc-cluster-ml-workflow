import torch
import torchinfo
from utils import logs, config
from pathlib import Path
from model import NeuralNetwork
import tensorboard

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
        writer.add_scalar("Batch_Loss/train", loss.item(), batch + epoch * len(dataloader))
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

    # Load the parameters from the dictionary into variables
    input_size = params['general']['input_size']
    random_seed = params['general']['random_seed']
    epochs = params['train']['epochs']
    train_mode = params['train']['train_mode']
    batch_size = params['train']['batch_size']
    device_request = params['train']['device_request']

    # Create a SummaryWriter object to write the tensorboard logs
    tensorboard_path = logs.return_tensorboard_path()
    metrics = {'Epoch_Loss/train': None, 'Epoch_Loss/test': None, 'Batch_Loss/train': None}
    writer = logs.CustomSummaryWriter(log_dir=tensorboard_path, params=params, metrics=metrics)

    # Set a random seed for reproducibility across all devices. Add more devices if needed
    config.set_random_seeds(random_seed)
    # Prepare the requested device for training. Use cpu if the requested device is not available 
    device = config.prepare_device(device_request)

    # Load preprocessed data from the input file into the training and testing tensors
    input_file_path = Path('data/processed/data.pt')
    data = torch.load(input_file_path)
    X_ordered_training = data['X_ordered_training']
    y_ordered_training = data['y_ordered_training']
    X_ordered_testing = data['X_ordered_testing']
    y_ordered_testing = data['y_ordered_testing']

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

    # Training loop
    for t in range(epochs):
        print(f"Epoch {t+1}\n-------------------------------")
        epoch_loss_train = train_epoch(training_dataloader, model, loss_fn, optimizer, device, writer, epoch=t)
        epoch_loss_test = test_epoch(testing_dataloader, model, loss_fn, device, writer)
        epoch_audio_example = generate_audio_example(model, device, testing_dataloader)
        writer.add_scalar("Epoch_Loss/train", epoch_loss_train, t)
        writer.add_scalar("Epoch_Loss/test", epoch_loss_test, t)
        writer.add_audio("Audio_Pred/test", epoch_audio_example, t, sample_rate=44100)
        writer.step()  

    writer.close()

    # Save the model checkpoint
    output_file_path = Path('models/checkpoints/model.pth')
    output_file_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), output_file_path)
    print("Saved PyTorch Model State to model.pth")

    print("Done with the training stage!")

if __name__ == "__main__":
    main()
