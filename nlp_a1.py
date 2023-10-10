# -*- coding: utf-8 -*-
"""NLP_A1.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1q2j-xfjG_ORpCf7xLHcB3eo3usdmwPOu
"""

# Importing the essential libraries
from google.colab import files
import io
import math
import nltk
import re
from nltk.util import ngrams

import numpy as np


!pip install nltk

# Importing the given training and validation dataset
train = files.upload()
validation = files.upload()

# Preprocessing the data!
# Removing the numbers and creating sentence to word list


def process_corpus(data):

    data = io.BytesIO(data).read().decode('utf-8').lower()

    # Remove digits from the text
    data = re.sub(r'\d', '', data)

    # Split the text into sentences and then into words
    sentences = [sentence.split() for sentence in data.split('\n') if sentence.strip()]

    return sentences




train = process_corpus(train['train.txt'])
validation = process_corpus(validation['val.txt'])

from collections import Counter

def get_vocab(review_set):
    counts = Counter(word for sentence in review_set for word in sentence)
    return counts# dictionary containing one entry for each word in the vocad along with its counts

def get_total_word_count(vocab):
    total_count = sum(vocab.values())
    return total_count



train_vocab = get_vocab(train)
train_word_count = sum(len(l) for l in train)

# 3.1 unsmoothed unigram probabilities from the training corpus.


def get_word_unigram_probability(train_set_vocab, word):
  return train_set_vocab[word] / get_total_word_count(train_set_vocab)

def get_sentence_unigram_probability(train_set_vocab, sentence):
  unigram_probability = 1
  for word in sentence:
    unigram_probability *= get_word_unigram_probability(train_set_vocab, word)

  return unigram_probability

print('Unigram probabilities for training corpus')
for sentence_list in train:
  print(get_sentence_unigram_probability(train_vocab, sentence_list))

# 3.2 unsmoothed bigram probabilities from the training corpus.
def get_bigrams_count(train_set, word1, word2):
  bigram_count = 0
  for sentence_list in train_set:
    sentence_bigrams = list(ngrams(sentence_list, 2))
    bigram_count += sentence_bigrams.count((word1, word2))

  return bigram_count

def get_words_bigram_probability(train_set, train_set_vocab, word1, word2):
  bigrams_count = get_bigrams_count(train_set, word1, word2)
  return bigrams_count/train_set_vocab[word1]

def get_sentence_bigram_probability(train_set, train_set_vocab, sentence):
  sentence_bigrams = list(ngrams(sentence, 2))
  bigram_probability = 1

  for bigram in sentence_bigrams:
    bigram_probability *= get_words_bigram_probability(train_set, train_set_vocab, bigram[0], bigram[1])
  return bigram_probability




# print('Bigram probabilities for training corpus')
# for sentence_list in train:
#   print(str(get_sentence_bigram_probability(train, train_vocab, sentence_list)))

# 4 Smoothing and unknown words
def laplace(train_set, alpha=1):
    train_set_vocab = get_vocab(train_set)  # Unique words and their counts in the train_set
    train_set_word_count = sum(len(sentence) for sentence in train_set)  # Total word count in the train_set
    vocab_size = len(train_set_vocab)  # Number of unique words in the train_set

    smoothed_probs = dict()
    for word, count in train_set_vocab.items():
        smoothed_probs[word] = (count + alpha) / (train_set_word_count + vocab_size * alpha)

    return smoothed_probs  # Dictionary of words as keys and smoothed probabilities as values (unigram)

def laplace_step(word, train_set, train_set_vocab, train_set_word_count, alpha=1):
    vocab_size = len(train_set_vocab)  # Number of unique words in the train_set

    occurrences = train_set_vocab.get(word, 0)  # Number of times the word appears in the train set

    scaled_probability = 1000 * ((occurrences + alpha) / (train_set_word_count + (vocab_size * alpha)))
    return scaled_probability  # Scaled smoothed probability to avoid rounding to zero

def compute_perplexity(training_set, validation_set):
    training_vocab = get_vocab(training_set)
    validation_vocab = get_vocab(validation_set)

    total_words_in_validation = get_total_word_count(validation_vocab)
    total_words_in_training = sum(len(sentence) for sentence in training_set)

    total_log_space = 0
    for sentence in validation_set:
        for word in sentence:
            total_log_space += math.log(laplace_step(word, training_set, training_vocab, total_words_in_training, 1))

    perplexity = math.exp((-1 / total_words_in_validation) * total_log_space)
    return perplexity



def compute_perplexity_unsmooth(training_set, validation_set):
    training_vocab = get_vocab(training_set)
    validation_vocab = get_vocab(validation_set)

    total_words_in_validation = get_total_word_count(validation_vocab)
    total_words_in_training = sum(len(sentence) for sentence in training_set)

    total_log_space = 0
    for sentence in validation_set:
        total_log_space += math.log(get_sentence_unigram_probability(training_vocab, sentence))

    perplexity = math.exp((-1 / total_words_in_validation) * total_log_space)
    return perplexity


print(compute_perplexity(train, validation))

