
from abc import ABCMeta, abstractmethod
from Facebook.pages import  PageSearcher
from Facebook.groups import GroupSearcher
from Facebook.events import EventSearcher
from Twitter.twitter_stream import TwitterStreamer
from Twitter.twitter_search import TwitterSearcher
from py2neo import Relationship
from settings import *

from multiprocessing.context import Process
from time import sleep


class SocialNetworkMiner(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_data_from_sn(self, search_list, database_name):
        pass

    @staticmethod
    def factory(sn):
        if sn == 'facebook':
            return FacebookMiner()

        if sn == 'twitter':
            return TwitterMiner()


class FacebookMiner(SocialNetworkMiner):

    def get_data_from_sn(self, search_list, database_name):

        if database_name == 'neo':
            sn_node = graph.find_one("SN", "name", "SOCIALNETWORKS")
            facebook_node = graph.merge_one("Facebook", "name", "FACEBOOK")
            sn_has_facebook = Relationship(sn_node, "HAS", facebook_node)
            graph.create_unique(sn_has_facebook)


        event_searcher = EventSearcher()
        event_process = Process(target=event_searcher.run_facebook_events, args=(search_list, database_name,))

        group_searcher = GroupSearcher()
        group_process = Process(target=group_searcher.run_facebook_groups, args=(search_list, database_name,))

        page_searcher = PageSearcher()
        page_process = Process(target=page_searcher.run_facebook_pages, args=(search_list, database_name,))

        event_process.start()
        group_process.start()
        page_process.start()

        event_process.join()
        group_process.join()
        page_process.join()


class TwitterMiner(SocialNetworkMiner):

    def get_data_from_sn(self, search_list, database_name):

        if database_name == 'neo':
            sn_node = graph.find_one("SN", "name", "SOCIALNETWORKS")
            twitter_node = graph.merge_one("Twitter", "name", "TWITTER")
            sn_has_twitter = Relationship(sn_node, "HAS", twitter_node)
            graph.create_unique(sn_has_twitter)

        twitter_searcher = TwitterSearcher()
        twitter_searcher_process = Process(target=twitter_searcher.run_twitter_search, args=(search_list, database_name,))

        twitter_streamer = TwitterStreamer()
        twitter_streamer_process = Process(target=twitter_streamer.run_twitter_stream, args=(search_list, database_name,))

        twitter_searcher_process.start()
        twitter_streamer_process.start()
        twitter_streamer_process.join()
        twitter_searcher_process.join()