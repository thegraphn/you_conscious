import datetime
import os, sys
import pickle
from random import shuffle

from tensorflow import keras
from tensorflow.python.keras.callbacks import ReduceLROnPlateau, EarlyStopping
from tensorflow.python.keras.preprocessing.sequence import pad_sequences

PROJECT_FOLDER = os.path.dirname(os.path.abspath(os.getcwd()))
print(PROJECT_FOLDER)
PROJECT_FOLDER = PROJECT_FOLDER.replace("dl_exp", "")

sys.path.append(PROJECT_FOLDER)
print(PROJECT_FOLDER)
from dl_exp.model_architecture.model_architecture import lstm_model, easy
from dl_exp.pre_processing.pre_processing import PreProcessing
from dl_exp.utils.data_utils import DataLoaderCsvTextClassification


import numpy as np
import tensorflow as tf

gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
    try:
        # Currently, memory growth needs to be the same across GPUs
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
        logical_gpus = tf.config.experimental.list_logical_devices('GPU')
        print(len(gpus), "Physical GPUs,", len(logical_gpus), "Logical GPUs")
    except RuntimeError as e:
        # Memory growth must be set before GPUs have been initialized
        print(e)

input_path: str = "/home/graphn/repositories/you_conscious/dl_exp/data/train_data_set.csv"

position_text: int = 2
position_label: int = 1
input_path_delimiter: str = ";"
class_delimiter: str = ";"
hyper_parameters = {"max_length": 200,
                    "embedding_length": 256,
                    "number_epochs": 1,
                    "batch_size": 256,
                    "number_hidden_lstm_layers": 1,
                    "lstm_units": 64
                    }
data_loader = DataLoaderCsvTextClassification(input_path=input_path, position_text=position_text,
                                              position_label=position_label, input_path_delimiter=input_path_delimiter,
                                              class_delimiter=class_delimiter)

data_set = data_loader.load_data_set(skip_header=False)
shuffle(data_set)
print(len(data_set))
print(data_set[10])

# pre process data
# pre process string ?
# put input into int matrices
pre_processor = PreProcessing(data_set)
word2id, labed2id = pre_processor.create_x2id(data_set)
print("Vocab size: ", len(word2id))
print(labed2id)
training_set = pre_processor.data_set_2_matrices(data_set, pre_processor.word2id, pre_processor.label2id)

id2word = {v: k for k, v in word2id.items()}
id2label = {v: k for k, v in labed2id.items()}

x_train = []  # list of the text
y_train = []  # list of the labels

for data in training_set:
    text, label = data

    x_train.append(text)
    y_train.append([label])
x_train = np.asarray(x_train)
# add padding
X_train = pad_sequences(x_train, hyper_parameters["max_length"], dtype='int32', padding='post',
                        truncating='post'
                        , value=word2id["PADDING_TOKEN"])
print(X_train[10])
Y_train = np.asarray(y_train)

if len(labed2id) == 2:
    compileMode = "binary"
else:
    compileMode = "categorical"

# model

model = lstm_model(VOCAB_SIZE=len(word2id), EMBEDDING_LENGTH=hyper_parameters["embedding_length"],
                   MAX_LENGTH=hyper_parameters["max_length"], NUM_CLASS=len(labed2id),
                   COMPILE_MODE="categorical", UNITS=hyper_parameters["lstm_units"],
                   number_hidden_lstm_layers=hyper_parameters["number_hidden_lstm_layers"])
model = easy(len(word2id))

print(model.summary())
# Train the model
model_trained_directory = "/home/graphn/repositories/you_conscious/dl_exp/model_trained/test"
if not os.path.exists(model_trained_directory):
    os.mkdir(model_trained_directory)
model_path = os.path.join(model_trained_directory, "model.h5")
callbacks = [
    ReduceLROnPlateau(verbose=1),
    EarlyStopping(patience=100, verbose=1),
    keras.callbacks.ModelCheckpoint(filepath=model_path, monitor='val_loss', save_best_only=True)
]
begin = datetime.datetime.now().replace(microsecond=0)

history_train = model.fit(X_train, Y_train,
                          batch_size=hyper_parameters["batch_size"],
                          epochs=hyper_parameters["number_epochs"],
                          validation_split=0.3,
                          class_weight="auto",
                          callbacks=callbacks,
                          use_multiprocessing=True
                          )


with open(os.path.join(model_trained_directory, "word2id.pck"), "wb") as o:
    pickle.dump(word2id, o)
with open(os.path.join(model_trained_directory, "id2label.pck"), "wb") as o:
    pickle.dump(id2label, o)
