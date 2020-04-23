import csv
import numpy as np
from keras_preprocessing.sequence import pad_sequences
from nltk import word_tokenize
import random
import pandas as pd


def prepareData(csv_file, DELIMITER_INPUT_DATA, POSITION_LABEL, POSITION_TEXT):
    '''
    Read the csv file and return the labels with theirs words.
    [
    ["Der", "Kampf", "gegen","die" ,"Steuerflucht", "steht", "2016" ...]Wirtschaft,
    ..
    ]
    :param POSITION_TEXT:
    :param POSITION_LABEL:
    :param DELIMITER_INPUT_DATA:
    :param csv_file:
    :return: List

    '''
    trainingSet = []
    with open(csv_file, "r", encoding="utf-8") as f:
        csv_reader = csv.reader(f, delimiter=DELIMITER_INPUT_DATA)
        next(csv_reader, None)  # skip the headers
        i = 0
        for row in csv_reader:
            label_text = []
            categoryLabel = row[POSITION_LABEL]
            if "undecided" not in categoryLabel:
                text = row[POSITION_TEXT].lower()
                text_tokenized = word_tokenize(text)

                label_text.append(text_tokenized)
                label_text.append(categoryLabel)
                trainingSet.append(label_text)
            i += 1
    random.shuffle(trainingSet)
    return trainingSet


def prepareDataWordsFeatured(csv_file, DELIMITER_INPUT_DATA, POSITION_LABEL, POSITION_TEXT):
    '''
    Read the csv file and return the labels with theirs words.
    [
    ["Der", "Kampf", "gegen","die" ,"Steuerflucht", "steht", "2016" ...][Wirtschaft],
    ...
    ]
    :param POSITION_TEXT:
    :param POSITION_LABEL:
    :param DELIMITER_INPUT_DATA:
    :param csv_file:
    :return: List

    '''
    trainingSet = []
    with open(csv_file, "r", encoding="utf-8") as f:
        csv_reader = csv.reader(f, delimiter=DELIMITER_INPUT_DATA)
        next(csv_reader, None)  # skip the headers
        i = 0
        for row in csv_reader:
            if "undecided" not in row[POSITION_LABEL]:
                label_text = []
                categoryLabel = row[POSITION_LABEL]
                text = row[POSITION_TEXT]
                text_tokenized = word_tokenize(text)
                label_text.append(text_tokenized)
                label_text.append(categoryLabel)
                trainingSet.append(label_text)
            i += 1
    return trainingSet


def prepareDataCharacters(csv_file, DELIMITER_INPUT_DATA, POSITION_LABEL, POSITION_TEXT):
    '''
    Read the csv file and return the labels with theirs words.
    [
    ["Der", "Kampf", "gegen","die" ,"Steuerflucht", "steht", "2016" ...][Wirtschaft],
    ...
    ]
    :param POSITION_TEXT:
    :param POSITION_LABEL:
    :param DELIMITER_INPUT_DATA:
    :param csv_file:
    :return: List

    '''
    trainingSet = []
    with open(csv_file, "r", encoding="utf-8") as f:
        csv_reader = csv.reader(f, delimiter=DELIMITER_INPUT_DATA)
        next(csv_reader, None)  # skip the headers
        i = 0
        for row in csv_reader:
            if "undecided" not in row[POSITION_LABEL]:
                label_text = []
                categoryLabel = row[POSITION_LABEL]
                text = row[POSITION_TEXT].lower()
                letters = []
                for letter in text:
                    letters.append(letter)
                label_text.append(letters)
                label_text.append(categoryLabel)
                trainingSet.append(label_text)
            i += 1
    random.shuffle(trainingSet)
    return trainingSet


def createMatrices(trainingData, label2id, word2id):
    '''
    The model works with integer, therefore we need to convert the strings into integers
    :param trainingData:
    :return: The same structure but with integers instead of strings
    '''
    for data in trainingData:
        text = data[0]
        label = data[1]
        if label not in label2id.keys():
            print(label2id)
            data[1] =label2id["UNKNOW_LABEL"]
        else:
            data[1] = label2id[label]
        text_temp = []
        for word in text:
            word = word2id.get(word, word2id["UNKNOWN_TOKEN"])
            text_temp.append(word)
        data[0] = text_temp
    return trainingData


def createMatricesWordsFeatured(sentences, word2id, label2id, case2id, char2id):
    dataset = []
    MAX_LENGTH_WORD = 40
    MAX_LENGTH_TEXT = 300
    wordCount = 0
    unknownWordCount = 0
    sentences_matrices = []

    dataset = []

    wordCount = 0
    unknownWordCount = 0

    for sentence in sentences:
        wordIndices = []
        caseIndices = []
        charIndices = []
        labelIndices = []
        label = sentence[1]
        word_char = sentence[0]
        for word, char in word_char:
            wordCount += 1
            if word in word2id:
                wordIdx = word2id[word]
            elif word.lower() in word2id:
                wordIdx = word2id[word.lower()]
            else:
                wordIdx = 0
                unknownWordCount += 1
            charIdx = []
            for x in char:
                charIdx.append(char2id[x])
            # Get the label and map to int
            wordIndices.append(wordIdx)
            caseIndices.append(getCasing(word, case2id))
            charIndices.append(charIdx)
        labelIndices.append(label2id[label])

        dataset.append([wordIndices, caseIndices, charIndices, labelIndices])

    return dataset


def createSet(input_data, output_data):
    '''
    From an input file return a set of the lines
    :param data:
    :return:
    '''
    sentences = set()
    with open(input_data, "r", encoding="utf-8") as f:
        for line in f:
            sentences.add(line)
    with open(output_data, "w", encoding="utf-8", newline="") as o:
        for sentence in sentences:
            o.write(sentence)


def getCasing(word, caseLookup):
    casing = 'other'

    numDigits = 0
    for char in word:
        if char.isdigit():
            numDigits += 1

    digitFraction = numDigits / float(len(word))

    if word.isdigit():  # Is a digit
        casing = 'numeric'
    elif digitFraction > 0.5:
        casing = 'mainly_numeric'
    elif word.islower():  # All lower case
        casing = 'allLower'
    elif word.isupper():  # All upper case
        casing = 'allUpper'
    elif word[0].isupper():  # is a title, initial char upper, then all lower
        casing = 'initialUpper'
    elif numDigits > 0:
        casing = 'contains_digit'
    return caseLookup[casing]


def addCharInformatioin(Sentences):
    sentences_with_char_info = []
    for i, sentence in enumerate(Sentences):
        sentence_temp = []
        words = sentence[0]
        label = sentence[1]
        for j, word in enumerate(words):
            char = [c for c in word]
            sentence_temp.append([word, char])
        sentences_with_char_info.append([sentence_temp, label])
    return sentences_with_char_info


def iterate_minibatches(dataset, batch_len):
    start = 0
    for i in batch_len:
        tokens = []
        caseing = []
        char = []
        labels = []
        data = dataset[start:i]
        start = i
        for dt in data:
            t, c, ch, l = dt
            l = np.expand_dims(l, -1)
            tokens.append(t)
            caseing.append(c)
            char.append([ch])
            # labels.append(l)
        yield np.asarray(l), np.asarray(tokens), np.asarray(caseing), np.asarray(char)


def createBatches(data):
    l = []
    for i in data:
        l.append(len(i[0]))
    l = set(l)
    batches = []
    batch_len = []
    z = 0
    for i in l:
        for batch in data:
            if len(batch[0]) == i:
                batches.append(batch)
                z += 1
        batch_len.append(z)
    return batches, batch_len
