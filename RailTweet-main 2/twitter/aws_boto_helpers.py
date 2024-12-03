import boto3
import csv
import pandas as pd


def aws_comprehend(list_of_tweet):
    """
    This method will return the sentiment analysis using AWS Comprehend
    :param list_of_tweet: (list) list of tweets
    :return: None
    """
    comprehend = boto3.client(service_name='comprehend', region_name='eu-west-1', aws_access_key_id=AWS_ACCESS_KEY_ID,
                              aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

    # text = "It is raining today in Seattle"

    print('Calling DetectSentiment')
    
    sentiment = []
    # testing first 50 comments in AWS comprehend
    #f = open("sentiment_analysis.csv", "w", encoding='utf-8')
    for text in list_of_tweet:
        json_data = comprehend.detect_sentiment(Text=text, LanguageCode='en')
        sentiment.append(str(json_data['Sentiment']))

    dict_data = {'tweet': list_of_tweet, 'sentiment': sentiment}
    df = pd.DataFrame(dict_data, columns=['tweet','sentiment'])

    return df


    print('End of DetectSentiment\n')
