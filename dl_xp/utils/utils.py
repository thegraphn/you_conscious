import glob
import os
import pickle

from tensorflow.python.keras.api._v2.keras import models


def load_model(model_path: str):
    modelDictionaries_directory = glob.glob(os.path.join(model_path, "*"))
    for file in modelDictionaries_directory:
        if "model.h5" in file:
            model = models.load_model(file)
    return model


def load_model_dependencies(model_path_dependencies: str):
    modelDictionaries_directory = glob.glob(os.path.join(model_path_dependencies, "*"))
    for file in modelDictionaries_directory:
        if "id2label.pck" in file:
            with open(file, "rb") as o:
                id2label = pickle.load(o)
        if "word2id.pck" in file:
            with open(file, "rb") as o:
                word2id = pickle.load(o)

    return word2id, id2label