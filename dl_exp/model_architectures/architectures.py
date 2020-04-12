
from keras import Model, Input, Sequential, layers
from keras.layers import Dense, Activation, LSTM, Bidirectional, Embedding, TimeDistributed, Conv1D, \
    Dropout, MaxPooling1D, concatenate, Flatten
import keras



def simple(MAX_LENGTH, NUM_LABELS):
    """
    Simple model for classification
    :param MAX_LENGTH: Maximum length of a sentence
    :param NUM_LABELS: Number of classes
    :return: Compiled Model
    """
    model = tf.keras.Sequential()
    model.add(Dense(2048, input_shape=(MAX_LENGTH,)))
    model.add(Activation('relu'))
    model.add(Dense(4096, input_shape=(MAX_LENGTH,)))
    model.add(Activation('relu'))
    model.add(Dense(8192, input_shape=(MAX_LENGTH,)))
    model.add(Activation('relu'))
    model.add(Dense(16384, input_shape=(MAX_LENGTH,)))
    model.add(Activation('relu'))
    model.add(Dense(NUM_LABELS))
    model.add(Activation('softmax'))
    model.compile(loss='sparse_categorical_crossentropy',
                  optimizer='adam',
                  metrics=['accuracy'])
    return model

def lstm_model(VOCAB_SIZE, EMBEDDING_LENGTH, MAX_LENGTH, NUM_CLASS, COMPILE_MODE, UNITS):
    model = Sequential()
    model.add(Embedding(VOCAB_SIZE, EMBEDDING_LENGTH, input_length=MAX_LENGTH))
    model.add(Dropout(0.5))
    model.add(Conv1D(filters=UNITS, kernel_size=3, padding='same', activation='relu'))
    model.add(MaxPooling1D(pool_size=1))
    model.add(Dropout(0.5))
    # model.add(Bidirectional(LSTM(UNITS, return_sequences=True)))
    model.add(Bidirectional(LSTM(UNITS)))
    model.add(Dense(UNITS * 2, activation='relu'))
    model.add(Dropout(0.5))
    if COMPILE_MODE == "categorical":
        model.add(Dense(NUM_CLASS, activation="softmax"))
        model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    if COMPILE_MODE == "binary":
        model.add(Dense(1, activation="sigmoid"))
        model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

    return model



