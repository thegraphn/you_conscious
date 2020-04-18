from keras.preprocessing.sequence import pad_sequences
from nltk import word_tokenize
import numpy as np
from data_processing.utils.file_paths import file_paths
from dl_exp.train.constant import MAX_LENGTH_TEXT
from dl_exp.utils.data import create_data_set, createMatrices

data_set: list = create_data_set(file_paths["filtered_only_matching_categories_datafeed"])
data_set = data_set[1:]
length_test_set = round(len(data_set) * 0.1)
train_set: list = data_set
test_set: list = data_set[length_test_set:]

set_words: set = set()
word2id: dict = {"PADDING_TOKEN": 0, "UNKNOWN_TOKEN": 1}
set_labels: set = set()
label2id: dict = dict()
for item in data_set:
    label, text = item
    tokens = word_tokenize(text)
    set_labels.add(label)
    for word in tokens:
        set_words.add(word)
for word in set_words:
    word2id[word] = len(word2id)
for label in set_labels:
    label2id[label] = len(label2id)
id2label: dict = {v: k for k, v in label2id.items()}
id2word: dict = {v: k for k, v in word2id.items()}

print("Vocabulary size: ", len(word2id))
print("Number of labels: ", len(label2id))

train_set = createMatrices(training_data=train_set, label2id=label2id, word2id=word2id, label_pos=0, text_pos=1)
#test_set = createMatrices(training_data=test_set, label2id=label2id, word2id=word2id, label_pos=0, text_pos=1)

x_train: list = []
y_train: list = []
x_test: list = []
y_test: list = []
for data in train_set:
    label, text = data
    x_train.append(text)
    y_train.append(label)
for data in test_set:
    label, text = data
    x_test.append(text)
    y_test.append(label)

x_train = np.asarray(x_train)
x_train =pad_sequences(x_train,MAX_LENGTH_TEXT,dtype='int32', padding='post', truncating='post'
                            , value=word2id["PADDING_TOKEN"])