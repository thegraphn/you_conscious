import datetime
import os, sys
import pickle
from random import shuffle

from you_conscious.dl_exp.model_architecture.model_architecture import lstm_model
from you_conscious.dl_exp.pre_processing.pre_processing import PreProcessing
from you_conscious.dl_exp.utils.data_utils import DataLoaderCsvTextClassification

PROJECT_FOLDER = os.path.dirname(os.path.abspath(os.getcwd()))
PROJECT_FOLDER = PROJECT_FOLDER.replace("text_classification/main_category_de", "")
print(PROJECT_FOLDER)
sys.path.append(PROJECT_FOLDER)
print(PROJECT_FOLDER)
import keras
from keras.callbacks import ReduceLROnPlateau, EarlyStopping
from keras_preprocessing.sequence import pad_sequences

import numpy as np

input_path: str = "/home/aurelien/privat_repositories/you_conscious/dl_exp/data/category_training_data_set.csv"

position_text: int = 1
position_label: int = 0
input_path_delimiter: str = ","
class_delimiter: str = ";"
hyper_parameters = {"max_length":200,
                    "embedding_length":256,
                    "number_epochs":40,
                    "batch_size":12,
                    "number_hidden_lstm_layers":5,
                    "lstm_units":256
                    }
data_loader = DataLoaderCsvTextClassification(input_path=input_path, position_text=position_text,
                                              position_label=position_label, input_path_delimiter=input_path_delimiter,
                                              class_delimiter=class_delimiter)

data_set = data_loader.load_data_set()
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

print(training_set[10])
id2word = {v: k for k, v in word2id.items()}
id2label = {v: k for k, v in labed2id.items()}
print(word2id["Wohnung"])
print(id2word[1634])

x_train = []  # list of the text
y_train = []  # list of the labels

for data in training_set:
    text, label = data

    x_train.append(text)
    y_train.append(label)
x_train = np.asarray(x_train)
# add padding
X_train = pad_sequences(x_train, hyper_parameters["max_length"], dtype='int32', padding='post',
                        truncating='post'
                        , value=word2id["PADDING_TOKEN"])
Y_train = np.asarray(y_train)

if len(labed2id) == 2:
    compileMode = "binary"
else:
    compileMode = "categorical"

# model

model = lstm_model(VOCAB_SIZE=len(word2id), EMBEDDING_LENGTH=hyper_parameters["embedding_length"],
                   MAX_LENGTH=hyper_parameters["max_length"], NUM_CLASS=len(labed2id),
                   COMPILE_MODE=compileMode, UNITS=hyper_parameters["lstm_units"],
                   number_hidden_lstm_layers=hyper_parameters["number_hidden_lstm_layers"])

print(model.summary())
# Train the model
model_trained_directory = "/home/aurelien/privat_repositories/you_conscious/dl_exp/model_trained/test"
if not os.path.exists(model_trained_directory):
    os.mkdir(model_trained_directory)
model_path = os.path.join(model_trained_directory, "model.h5")
callbacks = [
    ReduceLROnPlateau(verbose=1),
    EarlyStopping(patience=100, verbose=1),
    keras.callbacks.ModelCheckpoint(filepath=model_path, monitor='val_loss', save_best_only=True)
]
begin = datetime.datetime.now().replace(microsecond=0)

history_train = model.fit(X_train, [Y_train],
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
