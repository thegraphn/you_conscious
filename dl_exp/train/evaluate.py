import glob
import pickle
import sys,os
folder = os.path.dirname(os.path.realpath(__file__))

folder = folder.replace(r"/dl_exp/train", "")

sys.path.append(folder)
from dl_exp.utils.loadData import prepareData, createMatrices

import numpy as np
from absl import flags
from absl import app
from keras.preprocessing.sequence import pad_sequences
from tensorflow.keras import models

FLAGS = flags.FLAGS
flags.DEFINE_string("input_data_set", "", "path to the training data set")
flags.DEFINE_string("input_trained_modelAndDicts", "",
                    "The model and dictionaries files you will use for the predictions")
flags.DEFINE_integer("batch_size", 32, "batch size")
flags.DEFINE_string("csv_delimiter", "", "delimiter used in the training data set. If it is \t please write tab")
flags.DEFINE_integer("position_class", None, "position's index of the classes")
flags.DEFINE_integer("position_text", None, "position's index of the texts")
flags.DEFINE_string("optimizer", "", "sgd rmsprop adagrad adadelta adam adamax nadam")


def main(argv):
    MAX_LENGTH_TEXT = 0
    # 1 Load the data
    if FLAGS.csv_delimiter == "tab":
        csv_delimiter = "\t"

        testSet = prepareData(FLAGS.input_data_set, csv_delimiter, FLAGS.position_class,
                              FLAGS.position_text)
    else:
        testSet = prepareData(FLAGS.input_data_set, FLAGS.csv_delimiter, FLAGS.position_class,
                              FLAGS.position_text)

    modelDictionaries_directory = glob.glob(os.path.join(FLAGS.input_trained_modelAndDicts, "*"))
    for file in modelDictionaries_directory:
        if "id2label.pck" in file:
            with open(file, "rb") as o:
                id2label = pickle.load(o)
                print(id2label)
        if "word2id.pck" in file:
            with open(file, "rb") as o:
                word2id = pickle.load(o)
        if "model.h5" in file:
            model = models.load_model(file)
    label2id = {v: k for k, v in id2label.items()}
    print(label2id)
    testSet = createMatrices(testSet, label2id, word2id)
    x_test = []
    y_test = []
    for data in testSet:
        text, label = data
        x_test.append(text)
        y_test.append(label)
    MAX_LENGTH_TEXT = 666
    x_test = np.asarray(x_test)
    # add padding
    X_test = pad_sequences(x_test, MAX_LENGTH_TEXT, dtype='int32', padding='pre', truncating='pre', value=0)
    Y_test = np.asarray(y_test)
    # 3 Train the model
    print("Start Evaluation")
    history = model.evaluate(X_test, [Y_test],
                             verbose=1,
                             batch_size=1024)


if __name__ == "__main__":
    app.run(main)
