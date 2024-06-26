import torch
import numpy as np
import scipy as sp
import os
from ruamel.yaml import YAML
from source.config import load_params
from train import get_train_mode_params
from model import NeuralNetwork

def save_wav(name, data):
    sp.io.wavfile.write(name, 44100, data.flatten().astype(np.float32))

def main():
    # Load parameters from params.yaml
    params = load_params()
    
    name = params.train.name
    input_size = params.preprocess.input_size
    train_mode = params.train.train_mode

    # Get model hyperparameters based on training mode
    _, conv1d_strides, conv1d_filters, hidden_units = get_train_mode_params(train_mode)

    # Define the model (ensure to use the same architecture as in training.py)
    model = NeuralNetwork(conv1d_filters, conv1d_strides, hidden_units)

    # Load the model state
    model.load_state_dict(torch.load(f"models/checkpoints/{name}.pth", map_location=torch.device('cpu')))

    if not os.path.exists('models/exports/'):
        os.makedirs('models/exports/')

    # Export the model
    example = torch.rand(1, 1, input_size)
    filepath = f"models/exports/{name}.onnx"
    torch.onnx.export(model, example, filepath, export_params=True, opset_version=17, do_constant_folding=True,
                      input_names=['input'], output_names=['output'],
                      dynamic_axes={'input': {0: 'batch_size'}, 'output': {0: 'batch_size'}})

    print("Model exported to ONNX format.")

if __name__ == "__main__":
    main()
