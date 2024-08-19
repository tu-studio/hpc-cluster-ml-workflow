import numpy as np
import torch
from source.utils import config
from pathlib import Path
from pedalboard.io import AudioFile

def normalize(data):
    data_norm = max(max(data), abs(min(data)))
    return data / data_norm

def load_and_process_audio(file_path):
    with AudioFile(file_path) as f:
        data = f.read(f.frames).flatten().astype(np.float32)
    return normalize(data)

def split_data(data, test_split):
    split_idx = int(len(data) * (1 - test_split))
    return np.split(data, [split_idx])

def create_ordered_data(data, input_size):
    indices = np.arange(input_size) + np.arange(len(data)-input_size+1)[:, np.newaxis]
    indices = torch.from_numpy(indices)
    data = torch.from_numpy(data)
    ordered_data = torch.zeros_like(indices, dtype=torch.float32)
    for i, idx in enumerate(indices):
        ordered_data[i] = torch.gather(data, 0, idx)
    return ordered_data.unsqueeze(1)

def main():
    # Load the hyperparameters from the params yaml file into a Dictionary
    params = config.Params('params.yaml')

    # Load the parameters from the dictionary into variables
    input_size = params['general']['input_size']
    input_file = params['preprocess']['input_file']
    target_file = params['preprocess']['target_file']
    test_split = params['preprocess']['test_split']

    X_all = load_and_process_audio(input_file)
    y_all = load_and_process_audio(target_file)
    print("Data loaded and normalized.")

    X_training, X_testing = split_data(X_all, test_split)
    y_training, y_testing = split_data(y_all, test_split)
    print("Data split into training and testing sets.")

    X_ordered_training = create_ordered_data(X_training, input_size)
    X_ordered_testing = create_ordered_data(X_testing, input_size)
    print("Input data ordered.")

    y_ordered_training = torch.from_numpy(y_training[input_size-1:]).unsqueeze(1)
    y_ordered_testing = torch.from_numpy(y_testing[input_size-1:]).unsqueeze(1)
    print("Target data ordered.")

    output_file_path = Path('data/processed/data.pt')
    output_file_path.parent.mkdir(parents=True, exist_ok=True)

    torch.save({
        'X_ordered_training': X_ordered_training,
        'y_ordered_training': y_ordered_training,
        'X_ordered_testing': X_ordered_testing,
        'y_ordered_testing': y_ordered_testing
    }, output_file_path)
    print("Preprocessing done and data saved.")

if __name__ == "__main__":
    main()