from twython import TwythonStreamer
from .twitter_entities import *

consumer_key = 'GSyntmNWdme7tpGxrwuZlq31J'
consumer_secret = 'yji6bc8yWLfSSb2MlHPhYcHcYASMmlLsAIyIkOdIFsy4UJuZES'
access_token_key = '3301735539-gZnWmQDt9KEUa6NoNWy5SGJvEMvuDEMnSpozyRs'
access_token_secret = 'bJo9uIiCJKxXtbi2HiCJrTsBYNUopgY7eHa1CHVsy5CmS'




class MyStreamer(TwythonStreamer):

    def __init__(self,consumer_key, consumer_secret, access_token_key, access_token_secret, database_name):
        super().__init__(consumer_key, consumer_secret, access_token_key, access_token_secret)
        self.database_name = database_name
        self.i = 1

    def on_success(self, tweet):
        database_name = self.database_name
        if 'text' in tweet:
                if 'metadata' in tweet:
                    tweet.pop('metadata')
                if 'contributors' in tweet:
                    tweet.pop('contributors')
                if 'geo' in tweet:
                    tweet.pop('geo')
                if 'coordinates' in tweet:
                    tweet.pop('coordinates')
                if 'quoted_status' in tweet:
                    tweet.pop('quoted_status')
                if 'quoted_status_id' in tweet:
                    tweet.pop('quoted_status_id')
                if 'quoted_status_id_str' in tweet:
                    tweet.pop('quoted_status_id_str')
                if 'is_quote_status' in tweet:
                    tweet.pop('is_quote_status')
                if 'retweeted_status' in tweet:
                    tweet.pop('retweeted_status')

                t = Tweet()

                for key in tweet:
                    if not (type(tweet[key]) == dict or (type(tweet[key]) == list)):
                        t[key] = tweet[key]

                t.persist_tweet(database_name, tweet_type='stream')
                print(' The {} Stream Tweet was persisted successfully'.format(self.i))
                self.i += 1

                if 'entities' in tweet:
                    entity = tweet['entities']

                    if 'symbols' in entity:
                        entity.pop('symbols')

                    if 'extended_entities' in entity:
                        entity.pop('extended_entities')

                    if database_name == 'neo':
                        if 'media' in entity:
                            for photo in entity['media']:
                                ph = Photo()
                                if 'indices' in photo:
                                    ph['start_indice'] = photo['indices'][0]
                                    ph['end_indice'] = photo['indices'][1]

                                for key in photo:
                                    if not (type(photo[key]) == dict or (type(photo[key]) == list)):
                                        ph[key] = photo[key]
                                ph['tweet_id'] = tweet['id']
                                ph.persist_photo()

                        if 'urls' in entity:
                            for url in entity['urls']:
                                u = Url()
                                if 'indices' in url:
                                    u['start_indice'] = url['indices'][0]
                                    u['end_indice'] = url['indices'][1]

                                for key in url:
                                    if not (type(url[key]) == dict or (type(url[key]) == list)):
                                        u[key] = url[key]
                                u['tweet_id'] = tweet['id']
                                u.persist_Url()

                        if 'user_mentions' in entity:
                            for user_mention in entity['user_mentions']:
                                um = UserMention()
                                if 'indices' in user_mention:
                                    um['start_indice'] = user_mention['indices'][0]
                                    um['end_indice'] = user_mention['indices'][1]

                                for key in user_mention:
                                    if not (type(user_mention[key]) == dict or (type(user_mention[key]) == list)):
                                        um[key] = user_mention[key]
                                um['tweet_id'] = tweet['id']
                                um.persist_UserMention()


                        if 'hashtags' in entity:
                            for hashtag in entity['hashtags']:
                                ht= Hashtag()
                                if 'indices' in hashtag:
                                    ht['start_indice'] = hashtag['indices'][0]
                                    ht['end_indice'] = hashtag['indices'][1]

                                for key in hashtag:
                                    if not (type(hashtag[key]) == dict or (type(hashtag[key]) == list)):
                                        ht[key] = hashtag[key]

                                ht['tweet_id'] = tweet['id']
                                ht.persist_Hashtag()

                            if database_name == 'mongo':
                                entity['tweet_id'] = tweet['id']
                                db_tweet.entities.replace_one({"tweet_id": entity['tweet_id']}, entity, upsert=True)

                    tweet.pop('entities')

                if 'user' in tweet:
                    user = tweet['user']

                    if 'entities' in user:
                        user.pop('entities')

                    u = TwitterUser()

                    for key in user:
                        if not (type(user[key]) == dict or (type(user[key]) == list)):
                            u[key] = user[key]

                    u['tweet_id'] = tweet['id']
                    u.persist_twitter_user(database_name)

                    tweet.pop('user')


    def on_error(self, status_code, data):
        print (status_code)

class TwitterStreamer(object):

    def run_twitter_stream(self, search_list, database_name):

        if database_name == 'neo':
            stream_tweets_node = graph.merge_one("Stream", "name", "STREAM")
            twitter_node = graph.find_one("Twitter", "name", 'TWITTER')
            twitter_has_stream_tweets = Relationship(twitter_node, "HAS TWEETS", stream_tweets_node)
            graph.create_unique(twitter_has_stream_tweets)

        stream = MyStreamer(consumer_key, consumer_secret, access_token_key, access_token_secret, database_name)
        list_word = str(search_list).split('-')

        str_list = ''
        for w in list_word:
            w = w.rstrip().lstrip().lower()
            str_list += w + ','

        str_list = str_list[0:len(str_list)-1]
        print(str_list)
        stream.statuses.filter(track=str_list)