import tweepy
from tweepy import RateLimitError
import time
import json
import pandas as pd
import csv

def authTwitter():
    twitter_auth_data = open("twitter_auth_data.json").read()
    twitter_auth_data_json = json.loads(twitter_auth_data)

    access_token = twitter_auth_data_json["access_token"]
    access_token_secret = twitter_auth_data_json["access_token_secret"]
    consumer_key = twitter_auth_data_json["consumer_key"]
    consumer_secret = twitter_auth_data_json["consumer_secret"]

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)

    return api


"""
  file_path: path to SNScrape File
  Take a file from SNScrape and loads the urls into a list
  Return: list of urls
"""
def loadUlrs(file_path):
    ulrs = []
    with open(file_path) as f:
        urls = f.readlines()

    return [url.strip() for url in urls]


def getTweetId(url):
    return url.split('/')[-1]

def getTweet(api, url):

    tweetid = getTweetId(url)

    try:
        status = api.get_status(tweetid, tweet_mode="extended")
        return parseTweet(status)

    except RateLimitError as err:
        print("Rate Limit Triggerd. Sleeping for 15mins")
        time.sleep(60 * 15)

def parseTweet(status):
    
    data = {
            "id": status.id,
            "username": status.user.screen_name,
            "text": status.full_text.replace('\n', ''),
            "date": str(status.created_at),
            "location": status.user.location
        }

    return data

def generateCSV(tweet_list, output_path):
    data_file = open(output_path, 'w') 
    csv_writer = csv.writer(data_file)

    header = tweet_list[0].keys()
    csv_writer.writerow(header)

    for tweet in tweet_list:
        csv_writer.writerow(tweet.values())

    data_file.close


if __name__ == "__main__":

    urls = loadUlrs('test.txt')
    api = authTwitter()

    tweets = []
    status_counter = 0
    for url in urls:
        tweets.append(getTweet(api, url))
        if(status_counter % 5 == 0 ):
            print(f"Completed: {status_counter}/{len(tweets)}")
        status_counter += 1

    generateCSV(tweets, 'tweetdata.csv')


