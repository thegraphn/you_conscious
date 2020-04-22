from keras import Sequential, optimizers
from keras.layers import Embedding, Dropout, Conv1D, MaxPooling1D, Bidirectional, LSTM, Dense
from tensorflow.python.keras.utils.multi_gpu_utils import multi_gpu_model


def lstm_model(VOCAB_SIZE:int, EMBEDDING_LENGTH:int, MAX_LENGTH:int, NUM_CLASS:int, COMPILE_MODE:str, UNITS:int,number_hidden_lstm_layers:int):
    model = Sequential()
    model.add(Embedding(VOCAB_SIZE, EMBEDDING_LENGTH, input_length=MAX_LENGTH))
    model.add(Dropout(0.5))
    model.add(Conv1D(filters=UNITS, kernel_size=3, padding='same', activation='relu'))
    model.add(MaxPooling1D(pool_size=1))
    for i in range(number_hidden_lstm_layers):
        model.add(Dropout(0.5))
        model.add(Bidirectional(LSTM(UNITS, return_sequences=True,recurrent_dropout=0.5)))
    model.add(Dropout(0.5))
    model.add(Bidirectional(LSTM(UNITS,recurrent_dropout=0.5)))
    model.add(Dropout(0.5))
    model.add(Dense(UNITS * 2, activation='relu'))
    model.add(Dropout(0.5))
    optimizer = optimizers.adam(lr=0.001)
    if COMPILE_MODE == "categorical":

        model.add(Dense(NUM_CLASS, activation="softmax"))
        model.compile(optimizer=optimizer, loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    if COMPILE_MODE == "binary":
        model.add(Dense(1, activation="sigmoid"))
        model.compile(optimizer=optimizer, loss='binary_crossentropy', metrics=['accuracy'])

    return model

