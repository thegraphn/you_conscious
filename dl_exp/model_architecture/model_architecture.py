
from tensorflow.python.keras.utils.multi_gpu_utils import multi_gpu_model
import tensorflow_hub as hub

import tensorflow as tf


def lstm_model(VOCAB_SIZE: int, EMBEDDING_LENGTH: int, MAX_LENGTH: int, NUM_CLASS: int, COMPILE_MODE: str,
               UNITS: int, number_hidden_lstm_layers: int):
    model = tf.keras.Sequential()
    model.add(tf.keras.layers.Embedding(VOCAB_SIZE, EMBEDDING_LENGTH, input_length=MAX_LENGTH))
    model.add(tf.keras.layers.Dropout(0.5))
    model.add(tf.keras.layers.Conv1D(filters=UNITS, kernel_size=3, padding='same', activation='relu'))
    model.add(tf.keras.layers.MaxPooling1D(pool_size=1))
    for i in range(number_hidden_lstm_layers):
        model.add(tf.keras.layers.Dropout(0.5))
        model.add(tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(UNITS, return_sequences=True, recurrent_dropout=0.5)))
    model.add(tf.keras.layers.Dropout(0.5))
    model.add(tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(UNITS, recurrent_dropout=0.5)))
    model.add(tf.keras.layers.Dropout(0.5))
    model.add(tf.keras.layers.Dense(UNITS * 2, activation='relu'))
    model.add(tf.keras.layers.Dropout(0.5))
    optimizer = tf.keras.optimizers.Adam(lr=0.001)
    if COMPILE_MODE == "categorical":
        model.add(tf.keras.layers.Dense(NUM_CLASS, activation="softmax"))
        model.compile(optimizer=optimizer, loss='sparse_categorical_crossentropy', metrics=['accuracy'])

    return model


def simple_neuron():
    embedding = "https://tfhub.dev/google/tf2-preview/gnews-swivel-20dim/1"
    hub_layer = hub.KerasLayer(embedding, input_shape=[],
                               dtype=tf.string, trainable=True)
    model = tf.keras.Sequential()
    model.add(hub_layer)
    model.add(tf.keras.layers.Dense(16, activation='relu'))
    model.add(tf.keras.layers.Dense(1))

    model.summary()
    model.compile(optimizer='adam',
                  loss=tf.keras.losses.BinaryCrossentropy(from_logits=True),
                  metrics=['accuracy'])
    return model


def easy(vocab_size):
    model = tf.keras.Sequential([
        tf.keras.layers.Embedding(vocab_size, 64),
        tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(64)),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dense(1)
    ])
    model.compile(loss=tf.keras.losses.BinaryCrossentropy(from_logits=True),
                  optimizer=tf.keras.optimizers.Adam(1e-4),
                  metrics=['accuracy'])
    return model
