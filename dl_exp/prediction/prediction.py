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


folder = os.path.dirname(os.path.realpath(__file__))
print(folder)
folder = folder.replace(r"/you_conscious/dl_exp/prediction", "")
sys.path.append(folder)
from you_conscious.dl_exp.prediction.utils_prediction import chunk_batch, prediction_on_batch, write_results
from absl import flags, app
from tensorflow.keras import models

FLAGS = flags.FLAGS
flags.DEFINE_string("input_trained_modelAndDicts", "",
                    "Directory where the model and dictionaries files you will use for the predictions")
flags.DEFINE_string('input_file', '', 'Your input sentence to be prediction')
flags.DEFINE_integer("max_length_sentence", None, "Maximum length of the sentence, the model has been trained with")
flags.DEFINE_string("output_predictions", "", "Output file where the predictions are written")
flags.DEFINE_integer("batch_size", 5000, "Batch size for the prediction on batch")


def main(argv):
    modelDictionaries_directory = glob.glob(os.path.join(FLAGS.input_trained_modelAndDicts, "*"))
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
                list_sentences.append(line)
    begin = datetime.datetime.now().replace(microsecond=0)
    print("Begin predictions")
    shuffle(list_sentences)
    list_sentences = list_sentences#[100:300]

    list_sentences_chunked = chunk_batch(list_sentences, FLAGS.batch_size)
    batches_prediction = []
    for chunk in list_sentences_chunked:
        batches_prediction.append(prediction_on_batch(input_text=chunk, model=model, word2id=word2id,
                                                      max_length_sentence=FLAGS.max_length_sentence))


    print(batches_prediction)
    print(len(id2label))
    print(model.summary())
    list_predictions = []
    if True:
        print("b")
        for batch_prediction in batches_prediction:
            print("c")
            for prediction in batch_prediction:
                #prediction = prediction[0]
                predicted_label = np.argmax(prediction)
                score_prediction = np.max(prediction)
                list_predictions.append([id2label[predicted_label], score_prediction])


    end = datetime.datetime.now().replace(microsecond=0)
    print("Predictions took :", end - begin)

    for pred, text in zip(list_predictions, list_sentences):
        write_results(output_result=FLAGS.output_predictions,
                      prediction_to_write=pred
                      , text=text)


if __name__ == "__main__":
    app.run(main)
