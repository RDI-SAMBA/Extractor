from settings import *

from .search import Searcher
from py2neo import Relationship

class FacebookUser(dict):
    def __init__(self, name, id_user):
        self['name'] = name
        self['id'] = id_user


    def persist_user(self, database_name):
        if (database_name == 'mongo'):
            db.users.replace_one({'id': self['id']}, self, upsert=True)
        elif (database_name == 'neo'):
            user = graph.merge_one("User", "id", str(self['id']))
            for key in self:
                user[key] = self[key]
            user.push()

#####################################################################################################################################################


class GroupMember(FacebookUser):
    def __init__(self, name, id_gm, group_id):
        super().__init__(name, id_gm)
        self.group_id = group_id

#####################################################################################################################################################

class EventAttendee(FacebookUser):
    def __init__(self, name, id_user, event_id):
        super().__init__(name, id_user)
        self.event_id = event_id


    def get_posts(self, page_id, graph):
        posts = super().get_edges(page_id, posts_request_string, graph)
        return posts
#####################################################################################################################################################


class Group(Searcher, dict):
    def get_posts(self, graph):
        searcher = Searcher()
        posts = searcher.get_edges(self['id'], group_feed_string, graph)
        return posts

    def get_group_members(self, group_id, graph):
        members = Searcher.get_edges(group_id, group_members_string, graph)
        for member in members:
            member['group_id'] = group_id
        return members


    def order_posts_by_number_comments(self, edges, size, reverse=True):
        with_comments_key = [post for post in edges if 'comments' in post]
        ordered_edges = Searcher.order_by(input_list=with_comments_key, key=lambda edge: edge['comments']['summary']['total_count'],
                                 size=size, reverse=reverse)
        return ordered_edges

    def order_posts_by_number_likes(self, edges, size, reverse=True):
        ordered_edges = Searcher.order_by(input_list=edges, key=lambda edge: edge['likes']['summary']['total_count'], size=size,
                                 reverse=reverse)
        return ordered_edges

    def order_posts_by_number_shares(self, edges, size, reverse=True):
        def get_edges_with_shares(edgez):
            with_edges = []
            for edge in edgez:
                if 'shares' in edge:
                    with_edges.append(edge)
            return with_edges

        edges_with_shares = get_edges_with_shares(edges)
        ordered_edges = Searcher.order_by(input_list=edges_with_shares, key=lambda edge: edge['shares']['count'], size=size,
                                 reverse=reverse)
        return ordered_edges

    def order_posts_by_created_time(self, edges, size, reverse=True):
        ordered_edges = Searcher.order_by(input_list=edges, key=lambda edge: edge['created_time'], size=size, reverse=reverse)
        return ordered_edges

    def remove_dup_members(self, edges):
        no_dups = []
        ids = [elem['composite_id'] for elem in edges]
        for i in range(len(edges)):
            if edges[i]['composite_id'] in ids[i+1:]:
                continue
            no_dups.append(edges[i])
        return no_dups


    def persist_group(self, database_name):

        if (database_name == 'mongo'):
            db.groups.replace_one({'id': self['id']}, self, upsert=True)
        elif (database_name == 'neo'):
            group = graph.merge_one("Group", "id", str(self['id']))
            for key in self:
                group[key] = self[key]
            group.push()

            if 'owner_id' in self and self['owner_type'] == 'page':
                owner_node = graph.find_one("Page", "id", str(self['owner_id']))
                owner_of_group = Relationship(group, "HAS OWNER", owner_node)
                graph.create_unique(owner_of_group)
            elif 'owner_id' in self:
                owner_node = graph.find_one("User", "id", str(self['owner_id']))
                owner_of_group = Relationship(group, "HAS OWNER", owner_node)
                graph.create_unique(owner_of_group)






#####################################################################################################################################################

class Event(Searcher, dict):

    def get_posts(self, graph):
        searcher = Searcher()
        posts = searcher.get_edges(self['id'], event_feed_string, graph)
        return posts

    def get_event_attending(self, event_id, graph):
        attending_users = Searcher.get_edges(event_id, events_attending_string, graph)
        return attending_users
    pass

    def order_posts_by_number_comments(self, edges, size, reverse=True):
        with_comments_key = [post for post in edges if 'comments' in post]
        ordered_edges = Searcher.order_by(input_list=with_comments_key, key=lambda edge: edge['comments']['summary']['total_count'],
                                 size=size, reverse=reverse)
        return ordered_edges

    def order_posts_by_number_likes(self, edges, size, reverse=True):
        ordered_edges = Searcher.order_by(input_list=edges, key=lambda edge: edge['likes']['summary']['total_count'], size=size,
                                 reverse=reverse)
        return ordered_edges

    def order_posts_by_number_shares(self, edges, size, reverse=True):
        def get_edges_with_shares(edgez):
            with_edges = []
            for edge in edgez:
                if 'shares' in edge:
                    with_edges.append(edge)
            return with_edges

        edges_with_shares = get_edges_with_shares(edges)
        ordered_edges = Searcher.order_by(input_list=edges_with_shares, key=lambda edge: edge['shares']['count'], size=size,
                                 reverse=reverse)
        return ordered_edges

    def order_posts_by_created_time(self, edges, size, reverse=True):
        ordered_edges = Searcher.order_by(input_list=edges, key=lambda edge: edge['created_time'], size=size, reverse=reverse)
        return ordered_edges

    def persist_event(self, database_name):

        if (database_name == 'mongo'):
            db.events.replace_one({'id': self['id']}, self, upsert=True)
        elif (database_name == 'neo'):
            event = graph.merge_one("Event", "id", str(self['id']))
            for key in self:
                event[key] = self[key]
            event.push()

            if 'owner_id' in self and self['owner_type'] == 'page':
                owner_node = graph.find_one("Page", "id", str(self['owner_id']))
                owner_of_event = Relationship(event, "HAS OWNER", owner_node)
                graph.create_unique(owner_of_event)
            elif 'owner_id' in self:
                owner_node = graph.find_one("User", "id", str(self['owner_id']))
                owner_of_event = Relationship(event, "HAS OWNER", owner_node)
                graph.create_unique(owner_of_event)

#####################################################################################################################################################


class Page(FacebookUser, Searcher, dict):
    def get_posts(self, graph):
        searcher = Searcher()
        posts = searcher.get_edges(self['id'], posts_request_string, graph)
        return posts

    def get_page(self, graph):
        page = None
        while True:
            try:
                page = graph.get_object(self['id'])
                break
            except:
                pass
        return page

    def order_posts_by_number_comments(self, edges, size, reverse=True):
        with_comments_key = [post for post in edges if 'comments' in post]
        ordered_edges = Searcher.order_by(input_list=with_comments_key, key=lambda edge: edge['comments']['summary']['total_count'],
                                 size=size, reverse=reverse)
        return ordered_edges

    def order_posts_by_number_likes(self, edges, size, reverse=True):
        ordered_edges = Searcher.order_by(input_list=edges, key=lambda edge: edge['likes']['summary']['total_count'], size=size,
                                 reverse=reverse)
        return ordered_edges

    def order_posts_by_number_shares(self, edges, size, reverse=True):
        def get_edges_with_shares(edgez):
            with_edges = []
            for edge in edgez:
                if 'shares' in edge:
                    with_edges.append(edge)
            return with_edges

        edges_with_shares = get_edges_with_shares(self, edges)
        ordered_edges = Searcher.order_by(input_list=edges_with_shares, key=lambda edge: edge['shares']['count'], size=size,
                                 reverse=reverse)
        return ordered_edges

    def order_posts_by_created_time(self, edges, size, reverse=True):
        ordered_edges = Searcher.order_by(input_list=edges, key=lambda edge: edge['created_time'], size=size, reverse=reverse)
        return ordered_edges

    def persist_page(self, database_name):

        if (database_name == 'mongo'):
            db.pages.replace_one({'id': self['id']}, self, upsert=True)
        elif (database_name == 'neo'):
            loc = ""
            if self['location']:
                loc = self['location']
                location = graph.merge_one("Location", "page_id", str(self['id']))
                for key in self['location']:
                    location[key] = self['location'][key]
                location.push()
            self.pop('location')

            cat_list = []
            if self['category_list']:
                cat_list = self['category_list']
                category_list = graph.merge_one("Category List", "page_id", str(self['id']))
                category_list['name'] = 'Category List'
                category_list['page_name'] = self['name']
                category_list.push()

                for category in self['category_list']:
                    c = graph.merge_one("Category", "id", str(category['id']))
                    for key in category:
                        c[key] = category[key]
                    c.push()

                    a_category = Relationship(category_list, "INCLUDES", c)
                    graph.create_unique(a_category)
            self.pop('category_list')

            page = graph.merge_one("Page", "id", str(self['id']))
            for key in self:
                page[key] = self[key]
            page.push()

            if loc:
                page_has_location = Relationship(page, "IS LOCATED", location)
                graph.create_unique(page_has_location)

            if cat_list:
                page_has_categories = Relationship(page, "HAS CATEGORIES", category_list)
                graph.create_unique(page_has_categories)


class Page_Category(dict):
    def __init__(self, id_page, name):
        self['name'] = name
        self['id']= id_page

class Location():
    pass

#####################################################################################################################################################


class Comment(Searcher, dict):
    def get_comments(self, post_id, graph):
        comments = Searcher.get_edges(post_id, comments_request_string, graph)
        return comments

    def get_likes(self, post_id, graph):
        likes = Searcher.get_edges(post_id, likes_request_string, graph)
        return likes

    def order_comments_by_number_comments(self, comments, size, reverse=True):
        ordered_comments = Searcher.order_by(input_list=comments, key=lambda comment: comment['comment_count'], size=size,
                                    reverse=reverse)
        return ordered_comments


    def order_comments_by_number_likes(self, comments, size, reverse=True):
        ordered_comments = Searcher.order_by(input_list=comments, key=lambda comment: comment['like_count'], size=size,
                                    reverse=reverse)
        return ordered_comments


    def order_comments_by_created_time(self, comments, size, reverse=True):
        ordered_comments = Searcher.order_by(input_list=comments, key=lambda comment: comment['created_time'], size=size,
                                    reverse=reverse)
        return ordered_comments

    def has_comments(self, node_id, graph):
        response = {}
        while True:
            try:
                response = graph.request(node_id+'/comments?fields=id&limit=1')
                break
            except:
                pass
        if response['data']:
            return True
        return False


    def persist_comment(self, database_name):
        if ('from' in self and 'category' in self['from']):

            p = Page(self['from']['name'], self['from']['id'])
            page = p.get_page(graph_app)
            for key in page:
                if not (type(page[key]) == dict or (type(page[key]) == list)):
                    p[key] = page[key]

            category_list = []
            if 'category_list' in page:

                for category in page['category_list']:
                    ctg = Page_Category(category['id'], category['name'])
                    category_list.append(ctg)
            p['category_list'] = category_list

            location = {}
            if 'location' in page:
                for key in page['location']:
                    location[key] = page['location'][key]
            p['location'] = location


            p.persist_page(database_name)


        elif('from' in self and 'category' not in self['from']):
            user = FacebookUser(self['from']['name'], self['from']['id'])
            user.persist_user(database_name)



        if (database_name == 'mongo'):
            if 'from' in self:
                self['id_user'] = self['from']['id']
                self.pop('from')
            db.comments.replace_one({'id': self['id']}, self, upsert=True)
        elif (database_name == 'neo'):

            if 'from' in self:
                self['id_user'] = self['from']['id']
                self.pop('from')

            cmt = graph.merge_one("Comment", "id", str(self['id']))
            for key in self:
                cmt[key] = self[key]
            cmt.push()

            user_node = graph.find_one("User", "id", str(self['id_user']))

            if user_node is None:
                user_node = graph.find_one("Page", "id", str(self['id_user']))

            page_id = str(self['post_id']).split('_')[0]
            if user_node['id'] != page_id:
                usr_publish_comment = Relationship(user_node, "PUBLISHED COMMENT", cmt)
                graph.create_unique(usr_publish_comment)

            post_node = graph.merge_one("Post", "id", str(self['post_id']))
            post_has_comment = Relationship(post_node, "HAS COMMENT", cmt)
            graph.create_unique(post_has_comment)


#####################################################################################################################################################

class Post(Searcher, dict):
    def get_comments(self, graph):
        searcher = Searcher()
        comments = searcher.get_edges(self['id'], comments_request_string, graph)
        return comments


    def get_likes(self, graph):
        searcher = Searcher()
        likes = searcher.get_edges(self['id'], likes_request_string, graph)
        return likes


    def order_comments_by_number_comments(self, comments, size, reverse=True):
        ordered_comments = Searcher.order_by(input_list=comments, key=lambda comment: comment['comment_count'], size=size,
                                    reverse=reverse)
        return ordered_comments


    def order_comments_by_number_likes(self, comments, size, reverse=True):
        ordered_comments = Searcher.order_by(input_list=comments, key=lambda comment: comment['like_count'], size=size,
                                    reverse=reverse)
        return ordered_comments


    def order_comments_by_created_time(self, comments, size, reverse=True):
        ordered_comments = Searcher.order_by(input_list=comments, key=lambda comment: comment['created_time'], size=size,
                                    reverse=reverse)
        return ordered_comments

    def has_comments(self, graph):
        response = {}
        while True:
            try:
                response = graph.request(self['id'] +'/comments?fields=id&limit=1')
                break
            except:
                pass
        if response['data']:
            return True
        return False

    def persist_post(self, database_name):

        if ('from' in self and 'category' in self['from']):

            p = Page(self['from']['name'], self['from']['id'])
            page = p.get_page(graph_app)
            for key in page:
                if not (type(page[key]) == dict or (type(page[key]) == list)):
                    p[key] = page[key]

            category_list = []
            if 'category_list' in page:

                for category in page['category_list']:
                    ctg = Page_Category(category['id'], category['name'])
                    category_list.append(ctg)
            p['category_list'] = category_list

            location = {}
            if 'location' in page:
                for key in page['location']:
                    location[key] = page['location'][key]
            p['location'] = location

            p.persist_page(database_name)


        elif('from' in self and 'category' not in self['from']):
            user = FacebookUser(self['from']['name'], self['from']['id'])
            user.persist_user(database_name)




        if (database_name == 'mongo'):
            if 'from' in self:
                self['id_user'] = self['from']['id']
                self.pop('from')
            db.posts.replace_one({'id': self['id']}, self, upsert=True)
        elif (database_name == 'neo'):

            if 'from' in self:
                self['id_user'] = self['from']['id']
                self.pop('from')

            pst = graph.merge_one("Post", "id", str(self['parent_id']))
            for key in self:
                pst[key] = self[key]
            pst.push()



            user_node = graph.find_one("User", "id", str(self['id_user']))

            if user_node is None:

                user_node = graph.find_one("Page", "id", str(self['id_user']))

            if user_node['id'] != str(self['parent_id']):

                usr_publish_post = Relationship(user_node, "PUBLISHED POST", pst)
                graph.create_unique(usr_publish_post)


            posts_node = graph.find_one("Posts", "parent_id", str(self['parent_id']))
            post_in_posts = Relationship(posts_node, "HAS POST", pst)
            graph.create_unique(post_in_posts)
