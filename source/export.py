import torch
from utils import config
from model import NeuralNetwork
from pathlib import Path

def main():
    # Load the hyperparameters from the params yaml file into a Dictionary
    params = config.Params()

    # Load the parameters from the dictionary into variables
    input_size = params['general']['input_size']
    conv1d_strides = params['model']['conv1d_strides']
    conv1d_filters = params['model']['conv1d_filters']
    hidden_units = params['model']['hidden_units']

    # Define the model (ensure to use the same architecture as in train.py)
    model = NeuralNetwork(conv1d_filters, conv1d_strides, hidden_units)

    # Load the model state
    input_file_path = Path('models/checkpoints/model.pth')
    model.load_state_dict(torch.load(input_file_path, map_location=torch.device('cpu')))

    # Export the model
    example = torch.rand(1, 1, input_size)
    output_file_path = Path('models/exports/model.pth')
    output_file_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(model, output_file_path)
    print("Model exported to .pth format.")

if __name__ == "__main__":
    main()
