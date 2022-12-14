# -*- coding: utf-8 -*-
"""LSTM Model

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/17NOuFAcqeDGGMWc5mCrJTigDSMWsAKK_
"""

from google.colab import drive
drive.mount('/content/drive')

import pandas as pd

df = pd.read_csv('/content/drive/MyDrive/platinum/train.csv')
df

df.head()

df.shape

df.label.value_counts()

df.duplicated().sum()

df=df.drop_duplicates()

df.shape

df.head()

df.label.value_counts()

label_sent =['Positive','Neutral','Negative']
Value = [3412,1493,1138]

plt.bar(label_sent, Value)
plt.title('Sentiment Label')
plt.xlabel('Sentiment Label')
plt.ylabel('Value')
plt.show()

df['total_word'] = df.text.apply(lambda sent :len(sent.split()))

df.head()

df['total_char']=df.text.apply(len)

df.head()

import seaborn as sns
sns.scatterplot(data=df,y="total_word",x="total_char")

import re

def cleansing(sent):
  string = sent.lower()
  string = re.sub(r'[^a-zA-Z0-9]', ' ', string)
  return string
df['text_clean'] = df.text.apply(cleansing)

df.head()

neg = df.loc[df['label'] == 'negative'].text_clean.tolist()
neu = df.loc[df['label'] == 'neutral'].text_clean.tolist()
pos = df.loc[df['label'] == 'positive'].text_clean.tolist()

neg_label = df.loc[df['label'] == 'negative'].label.tolist()
neu_label = df.loc[df['label'] == 'neutral'].label.tolist()
pos_label = df.loc[df['label'] == 'positive'].label.tolist()

total_data = pos + neu + neg
labels = pos_label + neu_label + neg_label

print("Pos: %s, Neu: %s, Neg: %s" % (len(pos), len(neu), len(neg)))
print("Total data: %s" % len(total_data))

import pickle
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from collections import defaultdict

max_features = 100000
tokenizer = Tokenizer(num_words=max_features, split=' ', lower=True)
tokenizer.fit_on_texts(total_data)
with open('tokenizer.pickle', 'wb') as handle:
  pickle.dump(tokenizer, handle, protocol=pickle.HIGHEST_PROTOCOL)
  print("tokenizer.pickle has created!")

X = tokenizer.texts_to_sequences(total_data)

vocab_size = len(tokenizer.word_index)
maxlen = max(len(x) for x in X)

X = pad_sequences(X)
with open('x_pad_sequences.pickle', 'wb') as handle:
  pickle.dump(X, handle, protocol=pickle.HIGHEST_PROTOCOL)
  print("x_pad_sequences.pickle has created!")

Y = pd.get_dummies(labels)
Y = Y.values

with open('y_labels.pickle', 'wb') as handle:
  pickle.dump(Y, handle, protocol=pickle.HIGHEST_PROTOCOL)
  print("y_labels.pickle has created!")

from sklearn.model_selection import train_test_split
file = open("x_pad_sequences.pickle", 'rb')
X = pickle.load(file)
file.close()

file = open("y_labels.pickle", 'rb')
Y = pickle.load(file)
file.close()

X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.3, random_state=1)

import numpy as np
from tensorflow.keras import layers
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Embedding, LSTM, SpatialDropout1D, SimpleRNN, Activation
from tensorflow.keras import optimizers
from tensorflow.keras.callbacks import EarlyStopping, TensorBoard
from tensorflow.keras.layers import Flatten
from tensorflow.keras import backend as K

embed_dim = 100
units  = 64

model = Sequential()
model.add(Embedding(max_features, embed_dim, input_length=X.shape[1]))
model.add(LSTM(units, dropout=0.5))
model.add(Dense(3,activation='softmax'))
model.compile(loss = 'binary_crossentropy', optimizer='adam', metrics=['accuracy'])
print(model.summary())

adam = optimizers.Adam(lr = 0.001)
model.compile(loss = 'binary_crossentropy', optimizer = adam, metrics = ['accuracy'])

es = EarlyStopping(monitor='val_loss', mode='min', verbose=1, patience=1)
history = model.fit(X_train, y_train, epochs=10, batch_size=32, validation_data=(X_test, y_test), verbose=1, callbacks=[es])

from sklearn import metrics

predictions = model.predict(X_test)
y_pred = predictions
matrix_test = metrics.classification_report(y_test.argmax(axis=1), y_pred.argmax(axis=1))
print("Testing selesai")
print(matrix_test)

import numpy as np
from sklearn.metrics import classification_report
from sklearn.metrics import accuracy_score
from sklearn.model_selection import KFold

kf = KFold(n_splits=5, random_state=42, shuffle=True)

accuracies = []

y = Y

embed_dim = 100
units = 64
        
for iteration, data in enumerate(kf.split(X), start=1):

  data_train = X[data[0]]
  target_train = y[data[0]]

  data_test = X[data[1]]
  target_test = y[data[1]]

  model = Sequential()
  model.add(Embedding(max_features, embed_dim, input_length=X.shape[1]))
  model.add(LSTM(units, dropout=0.5))
  model.add(Dense(3,activation='softmax'))
  model.compile(loss = 'binary_crossentropy', optimizer='adam', metrics = ['accuracy'])

  adam = optimizers.Adam(lr = 0.001)
  model.compile(loss = 'binary_crossentropy', optimizer = adam, metrics = ['accuracy'])

  es = EarlyStopping(monitor='val_loss', mode='min', verbose=0, patience=1)
  history = model.fit(X_train, y_train, epochs=10, batch_size=32, validation_data=(X_test, y_test), verbose=0, callbacks=[es])

  predictions = model.predict(X_test)
  y_pred = predictions
  accuracy = accuracy_score(y_test.argmax(axis=1), y_pred.argmax(axis=1))

  print("Training ke-", iteration)
  print(classification_report(y_test.argmax(axis=1), y_pred.argmax(axis=1)))
  print("=======================================================")

  accuracies.append(accuracy)

average_accuracy = np.mean(accuracies)

print()
print()
print()
print("Rata-rata Accuracy: ", average_accuracy)

# Commented out IPython magic to ensure Python compatibility.
import matplotlib.pyplot as plt
plt.style.use('ggplot')

def plot_history(history):
  acc = history.history['accuracy']
  val_acc = history.history['val_accuracy']
  loss = history.history['loss']
  val_loss = history.history['val_loss']
  x = range(1, len(acc) + 1)

  plt.figure(figsize=(12, 5))
  plt.subplot(1, 2, 1)
  plt.plot(x, acc, 'b', label='Training acc')
  plt.plot(x, val_acc, 'r', label='Validation acc')
  plt.title('Training and validation accuracy')
  plt.legend()
  plt.subplot(1, 2, 2)
  plt.plot(x, loss, 'b', label='Training loss')
  plt.plot(x, val_loss, 'r', label='Validation loss')
  plt.title('Training and validation loss')
  plt.legend()

# %matplotlib inline
plot_history(history)

model.save('model.h5')
print("Model has created!")

import re
from keras.models import load_model

input_text = """
Cantik
"""

def cleansing(sent):
  string = sent.lower()

  string = re.sub(r'[^a-zA-Z0-9]',' ', string)
  return string

sentiment = ['negative', 'neutral', 'positive']

text = [cleansing(input_text)]
predicted = tokenizer.texts_to_sequences(text)
guess = pad_sequences(predicted, maxlen=X.shape[1])

model = load_model('model.h5')
prediction = model.predict(guess)
polarity = np.argmax(predictions[0])

print("Text: ", text[0])
print("Sentiment: ", sentiment[polarity])

