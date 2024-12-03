from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import tensorflow as tf
import tensorflow_hub as hub
import tensorflow_text as text
import pandas as pd
from django.conf import settings
import os

bert_preprocess = hub.KerasLayer("https://tfhub.dev/tensorflow/bert_en_uncased_preprocess/3")
bert_encoder = hub.KerasLayer("https://tfhub.dev/tensorflow/bert_en_uncased_L-12_H-768_A-12/4")
tr_model = None


def get_sentiment(text):

    tokenizer = AutoTokenizer.from_pretrained('nlptown/bert-base-multilingual-uncased-sentiment')
    model = AutoModelForSequenceClassification.from_pretrained('nlptown/bert-base-multilingual-uncased-sentiment')
    tokens = tokenizer.encode(text, return_tensors='pt')
    result = model(tokens)
    return int(torch.argmax(result.logits))+1


def train_model(tweets):
    df = pd.DataFrame(list(tweets.values()))
    print(df)
    desc = df.groupby('is_emergency').describe()
    print(desc)
    value_count = df['is_emergency'].value_counts()
    print(value_count)

    emergency_df = df[df['is_emergency'] == True ]
    e_df = emergency_df.shape
    non_emergency_df = df[df['is_emergency'] == False ]
    ne_df = non_emergency_df.shape

    print(e_df)
    print(ne_df)

    if e_df[0] < ne_df[0]:
        non_emergency_df = non_emergency_df.sample(e_df[0])
    elif e_df[0] > ne_df[0]:
        emergency_df = emergency_df.sample(ne_df[0])

    print("Sampled dataframes -  Emergency: ", emergency_df.shape, " Non Emergency: ", non_emergency_df.shape)

    df_balanced = pd.concat([non_emergency_df, emergency_df])
    print(df_balanced.shape)
    print(df_balanced['is_emergency'].value_counts())


    df_balanced[True]=df_balanced['is_emergency'].apply(lambda x: 1 if x==True else 0)
    df_balanced.sample(5)

    from sklearn.model_selection import train_test_split

    X_train, X_test, y_train, y_test = train_test_split(df_balanced['text'],df_balanced[True], stratify=df_balanced[True])
    sample = X_train.head(4)
    print(sample)

    # BL
    text_input = tf.keras.layers.Input(shape=(), dtype=tf.string, name='text')
    preprocessed_text = bert_preprocess(text_input)
    outputs = bert_encoder(preprocessed_text)

    # NLP
    l = tf.keras.layers.Dropout(0.1, name="dropout")(outputs['pooled_output'])
    l = tf.keras.layers.Dense(1, activation='sigmoid', name="output")(l)

    # Use inputs and outputs to construct a final model
    model = tf.keras.Model(inputs=[text_input], outputs = [l], name="tweets_classification")

    print(model.summary())
    print(len(X_train))

    METRICS = [
      tf.keras.metrics.BinaryAccuracy(name='accuracy'),
      tf.keras.metrics.Precision(name='precision'),
      tf.keras.metrics.Recall(name='recall')
    ]

    model.compile(optimizer='adam',
              loss='binary_crossentropy',
              metrics=METRICS)

    model.fit(X_train, y_train, epochs=5)
    model.evaluate(X_test, y_test)
    y_predicted = model.predict(X_test)
    y_predicted = y_predicted.flatten()

    import numpy as np

    y_predicted = np.where(y_predicted > 0.5, 1, 0)
    print(y_predicted)

    from sklearn.metrics import confusion_matrix, classification_report

    cm = confusion_matrix(y_test, y_predicted)
    print(cm)

    from matplotlib import pyplot as plt
    import seaborn as sn
    sn.heatmap(cm, annot=True, fmt='d')
    plt.xlabel('Predicted')
    plt.ylabel('Truth')

    model.save("TWEETS_MODEL.model")

    return classification_report(y_test, y_predicted)


def test_model(tweet):
    arr = []
    arr.append(tweet.text)
    model = tf.keras.models.load_model('TWEETS_MODEL.model')
    score = model.predict(arr)
    print(score)
    if float(score) > 0.5:
        review = 'Emergency'
        tweet.is_negative = True
        tweet.is_emergency = True
        tweet.save
    else:
        review = 'Feedback'
        tweet.is_negative = False
        tweet.save

    data = {
        'score': score,
        'is_emergency': True if score > 0.5 else False
    }

    return data
