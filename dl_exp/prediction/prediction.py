"""
This scripts predicts.

***Summary of the algorithm***
- We start by getting the required files (dictionaries and the model)
- The data to be tagged is read
- Conversion of  the data into the required format (e.g. word to id)
- Predictions can be done (line wise)
- We write the predictions into a file prediction with this format
    prediction \t score \t text
"""
import datetime
import glob
import os
import pickle
import sys
from random import shuffle

import numpy as np
import tokenizer

folder = os.path.dirname(os.path.realpath(__file__))
print(folder)
folder = folder.replace(r"/you_conscious/dl_exp/prediction", "")
sys.path.append(folder)
from absl import flags, app
from tensorflow.keras import models

FLAGS = flags.FLAGS
flags.DEFINE_string("input_trained_modelAndDicts", "",
                    "Directory where the model and dictionaries files you will use for the predictions")
flags.DEFINE_string('input_file', '', 'Your input sentence to be prediction')
flags.DEFINE_integer("max_length_sentence", None, "Maximum length of the sentence, the model has been trained with")
flags.DEFINE_string("output_predictions", "", "Output file where the predictions are written")
flags.DEFINE_integer("batch_size", 5000, "Batch size for the prediction on batch")
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


def main(argv):
    modelDictionaries_directory = glob.glob(os.path.join(FLAGS.input_trained_modelAndDicts, "*"))
    print(modelDictionaries_directory)
    for file in modelDictionaries_directory:
        if "id2label.pck" in file:
            with open(file, "rb") as o:
                id2label = pickle.load(o)
        if "word2id.pck" in file:
            with open(file, "rb") as o:
                word2id = pickle.load(o)
        if "model.h5" in file:
            model = models.load_model(file)
    # Load the requires data
    list_sentences = []
    with open(FLAGS.input_file, "r", encoding="utf-8") as o:
        for line in o:
            if "\n" != line:
                list_sentences.append(line.replace(",", ""))
    list_sentences_prepared = []
    for sentence in list_sentences:
        tokens: list = []

        for token in tokenizer.tokenize(sentence):
            kind, txt, val = token
            if txt is not None:
                tokens.append(txt)

        list_sentences_prepared.append(tokens)

    for s, sentence in enumerate(list_sentences_prepared):
        for t, token in enumerate(sentence):
            if token not in word2id:
                sentence[t] = 1
            else:

                sentence[t] = word2id[token]
        list_sentences_prepared[s] = sentence

    for sentence in list_sentences_prepared:
        prediction = model.predict(np.asarray(sentence))
        prediction = prediction[0]

        label_index = np.argmax(prediction)
        print(prediction, id2label[label_index])

    # write_results(output_result=FLAGS.output_predictions,
    #    prediction_to_write=pred
    #    , text=text)


if __name__ == "__main__":
    app.run(main)
