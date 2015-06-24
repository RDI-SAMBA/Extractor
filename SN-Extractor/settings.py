from pymongo import MongoClient
import facebook

APP_ID = '348074078715485'
APP_SECRET = '2060b7714f1fd0ade03ca69847561f4e'

APP_ACCESS_TOKEN = '1565746170348414|Y3x7aojUcRjvKo8Fq99pssKGcco'

USER_ACCESS_TOKEN = 'CAAE8kkZCRPl0BAIZAv2UDV7Xn8uE1AglnsW4usg6iJJcN6EAPOcYwZBW3OH\
MEcBm4PDHZBygZBZBHXlSS5NhdqjmFoF4hcd1Rx4ftVwC8knjil4ZCAhFZBkkETnK1a9Xoyts6P8ld\
hSoipeQY1RrmFNZBeWU0O9QTrct4d3rXc0zoL1ow4cUuRbOy6937oDZCX31YZD'

USER_ACCESS_TOKEN3 = 'CAACEdEose0cBAIzWez4v4Do8Y0jJaTJZBuovH4NFYdvNiZB2zZApZAQDJFcAZC2A\
vhmAVoMP9ZBErWBdB01iFd9JYYX9VzgSw47ysVnPR7lzN8o10xcxAvbJvgYyGGRlA1VdCFZAyzgl7VaZCU5ktJ0n\
iQ1ZBS91dZBfZC6ZCkTDVAKmikTIsFu9uSq625D37N6ixeRO5JMevVnWBosOXlU5fqVW'

MONGO_PORT = 27017
HOST = 'localhost'

from py2neo import Graph
from py2neo import authenticate

authenticate("localhost:7474", "neo4j", "root")
graph = Graph("http://localhost:7474/db/data/")

#graph.create_uniqueness_constraint("Facebook", "name")
#graph.create_uniqueness_constraint("Group", "id")
#graph.create_uniqueness_constraint("Page", "id")
#graph.create_uniqueness_constraint("User", "id")
#graph.create_uniqueness_constraint("Post", "id")
#graph.create_uniqueness_constraint("Comment", "id")
#graph.create_uniqueness_constraint("Twitter", "name")


# ############################################## Initialization Stuff ############################################### #


graph_app = facebook.GraphAPI(access_token=APP_ACCESS_TOKEN, version='2.3')
graph_app2 = facebook.GraphAPI(access_token=APP_ACCESS_TOKEN, version='2.3')
graph_app3 = facebook.GraphAPI(access_token=APP_ACCESS_TOKEN, version='2.3')

graph_user = facebook.GraphAPI(access_token=USER_ACCESS_TOKEN, version='2.3')
graph_user2 = facebook.GraphAPI(access_token=USER_ACCESS_TOKEN, version='2.3')
graph_user3 = facebook.GraphAPI(access_token=USER_ACCESS_TOKEN, version='2.3')

client = MongoClient(port=MONGO_PORT, host=HOST)
client2 = MongoClient(port=MONGO_PORT, host=HOST)
client3 = MongoClient(port=MONGO_PORT, host=HOST)


db = client.fb_database
db.posts.create_index("id", unique=True)
db.pages.create_index("id", unique=True)
db.comments.create_index("id", unique=True)
db.users.create_index("id", unique=True)
db.groups.create_index("id", unique=True)


# ############################################# Search and Request Parameter Strings ################################ #


posts_request_string = '/feed?fields=id,name,from,shares,story,likes.limit(0).summary(true)\
            ,comments.limit(0).summary(true),actions,message,message_tags,story_tags,status_type,created_time\
            ,updated_time&limit=250'

feed_request_string = '/feed?fields=id,name,from,shares,story,likes.limit(0).summary(true)\
            ,comments.limit(0).summary(true),actions,message,message_tags,story_tags,status_type,created_time\
            ,updated_time&limit=250'

comments_request_string = '/comments?fields=id,from,message,attachment,can_remove,created_time,like_count\
            ,comment_count,user_likes,object,parent,message_tags,can_comment&limit=250'

likes_request_string = '/likes?limit=250'

events_request_string = 'end_time,description,cover,id,name,privacy,parent_group,start_time,timezone,\
                                        feed_targeting,is_date_only,owner,updated_time,ticket_uri'

events_attending_string = '/attending?limit=250'

group_members_string = '/members?limit=250'

group_files_string = ''

group_feed_string = '/feed?fields=id,name,from,shares,story,likes.limit(0).summary(true)\
            ,comments.limit(0).summary(true),actions,message,message_tags,story_tags,status_type,created_time\
            ,updated_time&limit=250'

event_feed_string = '/feed?fields=id,name,from,shares,story,likes.limit(0).summary(true)\
            ,comments.limit(0).summary(true),actions,message,message_tags,story_tags,status_type,created_time\
            ,updated_time&limit=250'

group_docs_string = ''

groups_request_string = 'cover,description,email,icon,id,link,name,owner,parent,privacy,updated_time,venue'

places_request_string = ''

placetopics_request_string = ''


################################################ TWITTER CONFIG ################################################

CONSUMER_KEY = 'GSyntmNWdme7tpGxrwuZlq31J'
CONSUMER_SECRET = 'yji6bc8yWLfSSb2MlHPhYcHcYASMmlLsAIyIkOdIFsy4UJuZES'
ACCESS_TOKEN = '3301735539-gZnWmQDt9KEUa6NoNWy5SGJvEMvuDEMnSpozyRs'
ACCESS_TOKEN_SECRET = 'bJo9uIiCJKxXtbi2HiCJrTsBYNUopgY7eHa1CHVsy5CmS'

CONSUMER_KEY2 = 'ohEuSqUQV3rUtwmX85TkXeUnZ'
CONSUMER_SECRET2 = 'rqfmBLzcziAVMJvjfLloMgOOgVcFuzXRWQmUBHvrAa2U6VzA93'
ACCESS_TOKEN2 = '1009808737-WIlu3cwYPVQMkg0SGuEMR4mbJYkg8J0KQAE1nTP'
ACCESS_TOKEN_SECRET2 = 'VkuYzZyQgOdk9HM5SAdSzs8Swq0YVb2dPcfnDUak5nbEx'


CONSUMER_KEY3="Kis5KiNc5CeuJ6iP6Ewep2Bqd"
CONSUMER_SECRET3="DTwDaLUlLvqOHZRtSPMBJDQYVpoRbqwiqjteYseauoV9eelhS4"
ACCESS_TOKEN3="238728289-TW3pRakRp9E8BVmCu3nLgykSoGIIppqnWVzWW8Dm"
ACCESS_TOKEN_SECRET3="VvtQzIIVKy3crdXmtPgPRRNQgl7PfXwr2EryDZunIWi0b"

db_tweet = client.tw_database

db_tweet.tweets.create_index("id_str", unique=True)
db_tweet.users.create_index("id_str", unique=True)