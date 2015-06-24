from py2neo import Relationship

from settings import *


class TwitterUser(dict):

    def persist_twitter_user(self, database_name):
        if (database_name == 'mongo'):
            db_tweet.users.replace_one({'id': self['id']}, self, upsert=True)
        elif (database_name == 'neo'):
            user = graph.merge_one("Twitter_User", "id", self['id'])
            for key in self:
                user[key] = self[key]
            user.push()
            tweet_node = graph.find_one("Tweet", "id", self['tweet_id'])

            user_tweeted = Relationship(user, "TWEETED", tweet_node)
            graph.create_unique(user_tweeted)




class Tweet(dict):
    def persist_tweet(self, database_name, tweet_type):
        if (database_name == 'mongo'):
            db_tweet.tweets.replace_one({'id': self['id']}, self, upsert=True)
        elif (database_name == 'neo'):
            tweet_node = graph.merge_one("Tweet", "id", self['id'])
            for key in self:
                tweet_node[key] = self[key]
            tweet_node.push()

            if tweet_type == 'search':
                tweets_node = graph.find_one("Search", "name", "SEARCH")
                tweets_has_search_tweet = Relationship(tweets_node, "HAS", tweet_node)
                graph.create_unique(tweets_has_search_tweet)
            elif tweet_type == 'stream':
                tweets_node = graph.find_one("Stream", "name", "STREAM")
                tweets_has_stream_tweet = Relationship(tweets_node, "HAS", tweet_node)
                graph.create_unique(tweets_has_stream_tweet)

            photos_node = graph.merge_one("Photos", "tweet_id", self['id'])
            photos_node['name'] = "Photos"
            photos_node.push()
            tweet_has_photos = Relationship(tweet_node, "HAS", photos_node)
            graph.create_unique(tweet_has_photos)


            urls_node = graph.merge_one("Urls", "tweet_id", self['id'])
            urls_node['name'] = "Urls"
            urls_node.push()
            tweet_has_urls = Relationship(tweet_node, "HAS", urls_node)
            graph.create_unique(tweet_has_urls)



            hashtags_node = graph.merge_one("Hashtags", "tweet_id", self['id'])
            hashtags_node['name'] = "Hashtags"
            hashtags_node.push()
            tweet_has_hashtags = Relationship(tweet_node, "HAS", hashtags_node)
            graph.create_unique(tweet_has_hashtags)


            user_mentions_node = graph.merge_one("User_mentions", "tweet_id", self['id'])

            user_mentions_node['name'] = "User_mentions"
            user_mentions_node.push()
            tweet_has_user_mentions = Relationship(tweet_node, "HAS", user_mentions_node)
            graph.create_unique(tweet_has_user_mentions)



class Photo(dict):

    def persist_photo(self):
        photo = graph.merge_one("Photo", "tweet_id", self['tweet_id'])
        for key in self:
            photo[key] = self[key]
        photo.push()

        photos_node = graph.find_one("Photos", "tweet_id", self['tweet_id'])
        photos_has_photo = Relationship(photos_node, "HAS", photo)
        graph.create_unique(photos_has_photo)


class Url(dict):
    def persist_Url(self):
        url = graph.merge_one("Url", "tweet_id", self['tweet_id'])
        for key in self:
            url[key] = self[key]
        url.push()

        urls_node = graph.find_one("Urls", "tweet_id", self['tweet_id'])
        urls_has_url = Relationship(urls_node, "HAS", url)
        graph.create_unique(urls_has_url)



class Hashtag(dict):
    def persist_Hashtag(self):
        ht = graph.merge_one("Hashtag", "tweet_id", self['tweet_id'])
        for key in self:
            ht[key] = self[key]
        ht.push()

        hashtags_node = graph.find_one("Hashtags", "tweet_id", self['tweet_id'])
        hashtags_has_hashtag = Relationship(hashtags_node, "HAS", ht)
        graph.create_unique(hashtags_has_hashtag)

class UserMention(dict):
    def persist_UserMention(self):
        um = graph.merge_one("UserMention", "tweet_id", self['tweet_id'])
        for key in self:
            um[key] = self[key]
        um.push()


        user_mentions_node = graph.find_one("User_mentions", "tweet_id", self['tweet_id'])

        user_mentions_has_user_mention = Relationship(user_mentions_node, "HAS", um)
        graph.create_unique(user_mentions_has_user_mention)