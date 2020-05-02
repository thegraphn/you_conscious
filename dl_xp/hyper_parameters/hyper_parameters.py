class HyperParameter:
    def __init__(self):
        self.hyper_parameter: dict = self.create_hyper_parameters()

    def create_hyper_parameters(self):
        hp = {"embedding_length": 400,
              "lstm_units": 300,
              "lr": 0.001,
              "max_length": 200,
              "batch_size": 32,
              "number_epochs": 50,
              "number_hidden_lstm_layers": 4}
        return hp
