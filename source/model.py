from torch import nn

class NeuralNetwork(nn.Module):
    def __init__(self, conv1d_filters, conv1d_strides, hidden_units):
        super().__init__()
        self.pad = nn.ConstantPad1d(padding=12, value=0)
        self.conv1 = nn.Conv1d(in_channels=1, out_channels=conv1d_filters, kernel_size=12, stride=conv1d_strides)
        self.conv2 = nn.Conv1d(in_channels=conv1d_filters, out_channels=conv1d_filters, kernel_size=12, stride=conv1d_strides)
        self.lstm = nn.LSTM(input_size=16, hidden_size=hidden_units, batch_first=True, bias=True)
        self.linear = nn.Linear(in_features=hidden_units, out_features=1)

    def forward(self, x):
        x = self.pad(x)
        x = self.conv1(x)
        x = self.pad(x)
        x = self.conv2(x)
        x = x.permute(0, 2, 1)
        output, (hidden, cell) = self.lstm(x)
        x = self.linear(output[:, -1, :])
        return x
