from .twitter_entities import *
import twitter


auth = twitter.OAuth(ACCESS_TOKEN, ACCESS_TOKEN_SECRET, CONSUMER_KEY, CONSUMER_SECRET)
auth2 = twitter.OAuth(ACCESS_TOKEN2, ACCESS_TOKEN_SECRET2, CONSUMER_KEY2, CONSUMER_SECRET2)
auth3 = twitter.OAuth(ACCESS_TOKEN3, ACCESS_TOKEN_SECRET3, CONSUMER_KEY3, CONSUMER_SECRET3)


class TwitterSearcher(object):

    def run_twitter_search(self, search_list, database_name):

        list_words = str(search_list).split('-')

        for search_string in list_words:
            search_string = search_string.rstrip().lstrip().lower()
            if database_name == 'neo':
                search_tweets_node = graph.merge_one("Search", "name", "SEARCH")
                twitter_node = graph.find_one("Twitter", "name", 'TWITTER')
                twitter_has_search_tweets = Relationship(twitter_node, "HAS TWEETS", search_tweets_node)
                graph.create_unique(twitter_has_search_tweets)

            twitter_api = twitter.Twitter(auth=auth)
            search_results = None
            while not search_results:
                try:
                    search_results = twitter_api.search.tweets(q=search_string, count=100)
                    break
                except:
                    pass
            i = 1
            while 'statuses' in search_results:
                x = 1
                list_tweets = search_results['statuses']


                for tweet in list_tweets:


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

                    t.persist_tweet(database_name, tweet_type='search')
                    print(' The {} Search Tweet was persisted successfully'.format(i))

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

                    i += 1

                try:
                    next_results = search_results['search_metadata']['next_results']
                except KeyError:
                    break
                kwargs = dict([kv.split('=') for kv in next_results[1:].split("&")])
                search_results = None
                while not search_results:
                    try:
                        search_results = twitter_api.search.tweets(**kwargs)
                        break
                    except:
                        if x == 1:
                            twitter_api = twitter.Twitter(auth=auth2)
                            x = 2
                        elif x == 2:
                            twitter_api = twitter.Twitter(auth=auth3)
                            x = 3
                        elif x == 3:
                            twitter_api = twitter.Twitter(auth=auth)
                            x = 1

                search_results = None
                while not search_results:
                    try:
                        search_results = twitter_api.search.tweets(**kwargs)
                        break
                    except:
                        pass