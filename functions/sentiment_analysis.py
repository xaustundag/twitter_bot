import json
import os

import tweepy
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

def handler(event, context):
    bearer_token = os.environ['BEARER_TOKEN']
    consumer_key = os.environ['CONSUMER_KEY']
    consumer_secret = os.environ['CONSUMER_SECRET']
    access_token = os.environ['ACCESS_TOKEN']
    access_token_secret = os.environ['ACCESS_TOKEN_SECRET']

    tweepy_client = tweepy.Client(bearer_token=bearer_token, consumer_key=consumer_key, consumer_secret=consumer_secret, \
                                  access_token=access_token, access_token_secret=access_token_secret, wait_on_rate_limit=True)

    keyword = event['queryStringParameters']['keyword']
    query = f"{keyword} lang:en -is:retweet"
    tweets = tweepy_client.search_recent_tweets(query=query, tweet_fields=['id', 'created_at', 'text', 'public_metrics'], max_results=100)

    tweets_df = pd.DataFrame()
    for tweet in tweets.data:
        row = pd.DataFrame({'id': [tweet.id], 'created_at': [tweet.created_at], 'text': [tweet.text], \
                            'retweet_count': [tweet.public_metrics['retweet_count']], 'reply_count': [tweet.public_metrics['reply_count']], \
                            'like_count': [tweet.public_metrics['like_count']], 'quote_count': [tweet.public_metrics['quote_count']]})
        tweets_df = pd.concat([tweets_df, row], axis=0, ignore_index=True)

    results_df = perform_sentiment_analysis(tweets_df)
    avg_positive = results_df['positive'].mean()
    avg_negative = results_df['negative'].mean()
    avg_neutral = results_df['neutral'].mean()
    avg_ratio = results_df['pos_neg_ratio'].mean()
    avg_likes = tweets_df['like_count'].mean()
    avg_replies = tweets_df['reply_count'].mean()
    avg_retweets = tweets_df['retweet_count'].mean()
    avg_quotes = tweets_df['quote_count'].mean()

    sentiment_stats = {
        "avg_likes": avg_likes,
        "avg_replies": avg_replies,
        "avg_retweets": avg_retweets,
        "avg_quotes": avg_quotes,
        "avg_positive": avg_positive,
        "avg_negative": avg_negative,
        "avg_neutral": avg_neutral,
        "avg_ratio": avg_ratio
    }

    return {
        "statusCode": 200,
        "body": json.dumps(sentiment_stats)
    }

def perform_sentiment_analysis(tweets_df):
    results_df = pd.DataFrame()
    for index, row in tweets_df.iterrows():
        text = row["text"]
        if len(text) == 0:
            continue
        sid_obj = SentimentIntensityAnalyzer()
        sentiment_dict = sid_obj.polarity_scores(text)
        pos_neg_ratio = 1 if sentiment_dict['neg'] == 0 else (sentiment_dict['pos'] / sentiment_dict['neg'])
        row_df = pd.DataFrame({'id': [row['id']], 'created_at': [row['created_at']], 'text': [text], 'positive': [sentiment_dict['pos']], \
                               'negative': [sentiment_dict['neg']], 'neutral': [sentiment_dict['neu']], 'pos_neg_ratio': [pos_neg_ratio]})
        results_df = pd.concat([results_df, row_df], axis=0, ignore_index=True)
    return results_df
