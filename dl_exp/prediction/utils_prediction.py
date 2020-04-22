"""
This script contains helpful function in order to run the prediction scripts.

"""
import tokenizer
from keras_preprocessing.sequence import pad_sequences
import numpy as np
from tqdm import tqdm


def write_results(output_result, prediction_to_write, text):
    with open(output_result, "a", encoding="utf-8") as o:
        label = prediction_to_write[0]
        score = prediction_to_write[1]
        o.write(label + "\t" + str(score) + "\t" + text.replace("\n", "") + "\n")


def prediction(input_text, model, word2id, id2label, max_length_sentence):
    text_tokenized: list = []
    for token in tokenizer.tokenize(input_text):
        kind, txt, val = token
        if txt is not None:
            text_tokenized.append(txt)
    # text_tokenized = word_tokenize(input_text)
    text = []
    for word in text_tokenized:
        text.append(word2id.get(word, word2id["UNKNOWN_TOKEN"]))
    text = pad_sequences([text], max_length_sentence, dtype='int32', padding='post', truncating='post', value=0)
    predictions = model.predict(text)
    predictions = predictions[0]
    predicted_label = np.argmax(predictions)
    score_prediction = np.max(predictions)

    return id2label[predicted_label], score_prediction


def prediction_binary(input_text, above_05, bellow_05, model, word2id, id2label, max_length_sentence):
    # text_tokenized = word_tokenize(input_text.lower())
    text_tokenized: list = []
    for token in tokenizer.tokenize(input_text):
        kind, txt, val = token
        if txt is not None:
            text_tokenized.append(txt)

    text = []
    for word in text_tokenized:
        text.append(word2id.get(word, word2id["UNKNOWN_TOKEN"]))
    text = pad_sequences([text], max_length_sentence, dtype='int32', padding='post', truncating='post', value=0)
    predictions = model.predict(text)
    predictions = predictions[0]
    if predictions > 0.5:
        return above_05, predictions
    if predictions < 0.5:
        return bellow_05, predictions


def chunk_batch(lst, n):
    return [lst[i:i + n] for i in range(0, len(lst), n)]


def prediction_on_batch(input_text, model, word2id, max_length_sentence):
    array_to_predict = []
    for txt in tqdm(input_text):
        txt = txt.replace(",", " ")
        text = []
        text_tokenized: list = []
        for token in tokenizer.tokenize(input_text):
            kind, txt, val = token
            if txt is not None:
                text_tokenized.append(txt)
        for word in text_tokenized:
            print(word)
            text.append(word2id.get(word, word2id["UNKNOWN_TOKEN"]))
        array_to_predict.append(text)
    array_to_predict = np.asarray(array_to_predict)
    text = pad_sequences(array_to_predict, max_length_sentence, dtype='int32', padding='post', truncating='post',
                         value=0)
    predictions = model.predict_on_batch(text)

    return predictions
