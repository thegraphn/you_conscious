import datetime
import os, sys
import pickle
from collections import defaultdict
from random import shuffle
import sklearn
from sklearn.model_selection import train_test_split
from tensorflow import keras
from tensorflow.python.keras.callbacks import ReduceLROnPlateau, EarlyStopping
from tensorflow.python.keras.preprocessing.sequence import pad_sequences

PROJECT_FOLDER = os.path.dirname(os.path.abspath(os.getcwd()))
print(PROJECT_FOLDER)
PROJECT_FOLDER = PROJECT_FOLDER.replace("dl_xp", "")
sys.path.append(PROJECT_FOLDER)

from dl_xp.data_utils.data_utils import DataLoaderCsvTextClassification
from dl_xp.hyper_parameters.hyper_parameters import HyperParameter
from dl_xp.model_architectures.model_architectures import lstm_model
from dl_xp.pre_processing.pre_processing import PreProcessing


import numpy as np

root_folder = PROJECT_FOLDER
from absl import flags
from absl import app

FLAGS = flags.FLAGS
flags.DEFINE_string("input_data_set", "", "path to the training data set")
flags.DEFINE_string('output_trained_modelAndDicts', 'noName',
                    'where the model and the dictionary will be saved (list of '
                    'objects)')
flags.DEFINE_integer("batch_size", 32, "batch size")





def main(argv):
    # todo create train,dev,test sets
    input_path: str = FLAGS.input_data_set

    position_text: int = 2
    position_label: int = 0
    input_path_delimiter: str = "\t"
    class_delimiter: str = ";"
    hyper_parameters = HyperParameter()
    data_loader = DataLoaderCsvTextClassification(input_path=input_path)

    data_set = data_loader.load_data_set(skip_header=True,input_path_delimiter=input_path_delimiter,position_text=position_text,
                                         position_label=position_label,class_delimiter=class_delimiter,multi_label=False)
    shuffle(data_set)

    # pre process data
    # pre process string ?
    pre_processor = PreProcessing(data_set)
    word2id, label2id = pre_processor.create_x2id(data_set,multi_label=False)
    print("Vocab size: ", len(word2id))
    print(label2id)
    training_set = pre_processor.data_set_2_matrices(data_set, word2id, label2id,
                                                     multi_label=False)


    id2word = {v: k for k, v in word2id.items()}
    id2label = {v: k for k, v in label2id.items()}

    x_train = []  # list of the text
    y_train = []  # list of the labels

    for data in training_set:
        text, label = data

        x_train.append(text)
        y_train.append(label)
    x_train = np.asarray(x_train)
    # add padding
    X_train = pad_sequences(x_train, hyper_parameters.hyper_parameter["max_length"], dtype='int32', padding='post',
                            truncating='post'
                            , value=word2id["PADDING_TOKEN"])
    Y_train = np.array(y_train)
    print(X_train[10])
    print(Y_train[10])
    if len(label2id) == 2:
        compileMode = "binary"
    else:
        compileMode = "categorical"

    # model

    model = lstm_model(VOCAB_SIZE=len(word2id), EMBEDDING_LENGTH=hyper_parameters.hyper_parameter["embedding_length"],
                       MAX_LENGTH=hyper_parameters.hyper_parameter["max_length"], NUM_CLASS=len(label2id),
                       COMPILE_MODE=compileMode, UNITS=hyper_parameters.hyper_parameter["lstm_units"],
                       number_hidden_lstm_layers=hyper_parameters.hyper_parameter["number_hidden_lstm_layers"],
                       multi_label=False)

    # Train the model

    model_trained_directory = FLAGS.output_trained_modelAndDicts + "-" + str(
        hyper_parameters.hyper_parameter["batch_size"]) + "_" + str(
        hyper_parameters.hyper_parameter["number_epochs"]) + "_" + str(
        hyper_parameters.hyper_parameter["number_hidden_lstm_layers"]) + "_" + str(
        hyper_parameters.hyper_parameter["lstm_units"]) + "_" + str(hyper_parameters.hyper_parameter["max_length"])
    if not os.path.exists(model_trained_directory):
        os.mkdir(model_trained_directory)
    model_path = os.path.join(model_trained_directory, "model.h5")
    callbacks = [
        ReduceLROnPlateau(verbose=1),
        EarlyStopping(patience=100, verbose=1),
        keras.callbacks.ModelCheckpoint(filepath=model_path, monitor='val_loss', save_best_only=True)
    ]

    history_train = model.fit(X_train, [Y_train],
                              batch_size=hyper_parameters.hyper_parameter["batch_size"],
                              epochs=hyper_parameters.hyper_parameter["number_epochs"],
                              validation_split=0.3,
                              class_weight="auto",
                              callbacks=callbacks,
                              use_multiprocessing=True
                              )
    with open(os.path.join(model_trained_directory, "word2id.pck"), "wb") as o:
        pickle.dump(word2id, o)
    with open(os.path.join(model_trained_directory, "id2label.pck"), "wb") as o:
        pickle.dump(id2label, o)
    with open(os.path.join(model_trained_directory, "history.history"), "wb") as o:
        pickle.dump(history_train, o)


if __name__ == "__main__":
    app.run(main)
