import datetime
import os
import pickle

import keras
import numpy as np
from keras.callbacks import ReduceLROnPlateau, EarlyStopping
from keras.preprocessing.sequence import pad_sequences

from data_processing.utils.utils import cleansed_sex_data_feed_path, getMappingColumnIndex
from dl_exp.model_architectures.architectures import lstm_model
from dl_exp.train.constant import MAX_LENGTH_TEXT, EMBEDDING_LENGTH, batch_size, number_epochs, units
from dl_exp.utils.data import read_data, createMatrices

label_pos = getMappingColumnIndex(cleansed_sex_data_feed_path, "\t")["category_name"]

data_set = read_data(cleansed_sex_data_feed_path, label_pos=label_pos)

word2id: dict = {"PADDING_TOKEN": 0, "UNKNOWN_TOKEN": 1}
label2id: dict = {}
set_words: set = set()
set_label: set = set()

for item in data_set:
    text, label = item
    for word in text:
        set_words.add(word)
    set_label.add(label)

for word in set_words:
    word2id[word] = len(word2id)

for label in set_label:
    label2id[label] = len(label2id)

id2label = {v: k for k, v in
                label2id.items()}


training_set = data_set[0:200]

training_set = createMatrices(training_set, label2id, word2id)

print(training_set[10])
x_train = []  # list of the text
y_train = []  # list of the labels

for data in training_set:
    text, label = data

    x_train.append(text)
    y_train.append(label)
x_train = np.asarray(x_train)

# add padding
X_train = pad_sequences(x_train, MAX_LENGTH_TEXT, dtype='int32', padding='post', truncating='post'
                        , value=word2id["PADDING_TOKEN"])
Y_train = np.asarray(y_train)


model = lstm_model(VOCAB_SIZE=len(word2id), EMBEDDING_LENGTH=EMBEDDING_LENGTH, MAX_LENGTH=MAX_LENGTH_TEXT,
                   NUM_CLASS=len(id2label), COMPILE_MODE="categorical",
                   UNITS=int(units))

# Train the model
if os.path.exists(r"C:\Users\aurel\repositories\you_conscious\dl_exp\trained_model") != True:
    modelDictionariesPathDirecotry = os.mkdir(r"C:\Users\aurel\repositories\you_conscious\dl_exp\trained_model")
model_path = os.path.join(r"C:\Users\aurel\repositories\you_conscious\dl_exp\trained_model", "model.h5")
callbacks = [
    ReduceLROnPlateau(verbose=1),
    EarlyStopping(patience=100, verbose=1),
    keras.callbacks.ModelCheckpoint(filepath=model_path, monitor='val_loss', save_best_only=True)
]
begin = datetime.datetime.now().replace(microsecond=0)

history_train = model.fit(X_train, [Y_train],
                          batch_size=batch_size,
                          epochs=number_epochs,
                          validation_split=0.3,
                          class_weight="auto",
                          callbacks=callbacks,
                          use_multiprocessing=True
                          )

with open(os.path.join(r"C:\Users\aurel\repositories\you_conscious\dl_exp\trained_model", "word2id.pck"), "wb") as o:
    pickle.dump(word2id, o)
with open(os.path.join(r"C:\Users\aurel\repositories\you_conscious\dl_exp\trained_model", "id2label.pck"), "wb") as o:
    pickle.dump(id2label, o)
