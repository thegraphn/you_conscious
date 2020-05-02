from tensorflow.python.keras import optimizers
from tensorflow.python.keras.layers import Embedding, Conv1D, Dropout, MaxPooling1D, Bidirectional, LSTM, Dense
from tensorflow.python.keras.models import Sequential
import tensorflow as tf

def lstm_model(VOCAB_SIZE: int, EMBEDDING_LENGTH: int, MAX_LENGTH: int, NUM_CLASS: int, COMPILE_MODE: str, UNITS: int,
               number_hidden_lstm_layers: int,
               multi_label: bool):
    model = Sequential()
    model.add(Embedding(VOCAB_SIZE, EMBEDDING_LENGTH, input_length=MAX_LENGTH))
    model.add(Dropout(0.5))
    model.add(Conv1D(filters=UNITS, kernel_size=3, padding='same', activation='relu'))
    model.add(MaxPooling1D(pool_size=1))
    for i in range(number_hidden_lstm_layers):
        model.add(Dropout(0.5))
        model.add(Bidirectional(LSTM(UNITS, return_sequences=True, recurrent_dropout=0.5)))
    model.add(Dropout(0.5))
    model.add(Bidirectional(LSTM(UNITS, recurrent_dropout=0.5)))
    model.add(Dropout(0.5))
    #model.add(Dense(UNITS * 2, activation='relu'))
    #model.add(Dropout(0.5))
    optimizer = tf.optimizers.Adam(lr=0.001)
    if COMPILE_MODE == "categorical":
        if multi_label:
            model.add(Dense(NUM_CLASS, activation="sigmoid"))
            model.compile(optimizer=optimizer, loss='binary_crossentropy', metrics=['accuracy'])
        else:
            model.add(Dense(NUM_CLASS, activation="softmax"))
            model.compile(optimizer=optimizer, loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    if COMPILE_MODE == "binary":
        model.add(Dense(1, activation="sigmoid"))
        model.compile(optimizer=optimizer, loss='binary_crossentropy', metrics=['accuracy'])

    return model
