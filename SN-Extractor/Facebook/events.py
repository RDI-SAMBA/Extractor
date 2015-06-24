
from .entities import *



class EventSearcher(Searcher):
    def search_events(self, search_term, graph):
        events = []
        while True:
            try:
                events = graph.request('search', args={'q': search_term, 'type': 'event', 'limit': '1000'})['data']
                break
            except:
                pass
        for event in events[:10]:
            e = graph.get_object(event['id'])
            if 'description' in e:
                event['description'] = e['description']
            if 'privacy' in e:
                event['privacy'] = e['privacy']
            if 'owner' in e:
                event['owner'] = e['owner']
        return events


    def run_facebook_events(self, search_string, database_name):

        if database_name == 'neo':
            events_node = graph.merge_one("Events", "name", "EVENTS")
            facebook_node = graph.find_one("Facebook", "name", 'FACEBOOK')
            facebook_has_events = Relationship(facebook_node, "HAS EVENTS", events_node)
            graph.create_unique(facebook_has_events)

        evts = []
        list_words = str(search_string).split('-')

        for word in list_words:
            results = self.search_events(word, graph=graph_user)
            evts.append(results)



        grp =[]
        searcher = Searcher()
        for gp in evts:
            gp = searcher.remove_duplicates(gp)
            groupsss = []
            for g in gp:
                b = False
                lwn = g['name'].split(' ')
                for word in list_words:
                    word = word.lstrip().rstrip().lower()
                    if len(word.split(' ')) > 1:
                        if word.lstrip().rstrip().lower() in g['name'].lower():
                            b = True
                    else:
                        for n in lwn:
                            if str(word).lstrip().rstrip().lower() == str(n).lower():
                                b = True
                if b:
                    groupsss.append(g)
            grp.append(groupsss)

        d = int(10/len(list_words))+1
        events = []
        for g in grp:
            for l in g[0:d]:
                events.append(l)


        events = searcher.remove_duplicates(events)

        print('------------------ POPULAR EVENTS FOR {} ON FACEBOOK ------------------ \n'.format(search_string))
        for event in events:
            print('Id :', event['id'], 'Name :', event['name'])

        i = 1
        for event in events:
            e = Event()
            for key in event:
                if not (type(event[key]) == dict or (type(event[key]) == list)):
                    e[key] = event[key]


            if 'owner' in event:
                if 'category' in event['owner']:
                    e['owner_type'] = 'page'
                    page = graph_app.get_object(id=event['owner']['id'])
                    p = Page(page['name'], page['id'])
                    for key in page:
                        if not (type(page[key]) == dict or (type(page[key]) == list)):
                            p[key] = page[key]

                    category_list = []
                    if 'category_list' in page:

                        for category in page['category_list']:
                            ctg = Page_Category(category['id'], category['name'])
                            category_list.append(ctg)

                    if 'cover' in page:
                        p['cover_url'] = page['cover']['source']

                    location = {}
                    if 'location' in page:

                        for key in page['location']:
                            location[key] = page['location'][key]

                    p['location'] = location
                    p['category_list'] = category_list

                else:
                    e['owner_type'] = 'user'
                    user = FacebookUser(event['owner']['name'], event['owner']['id'])

                e['owner_id'] = event['owner']['id']

            if 'owner_type' in e:
                if e['owner_type'] == 'user':
                    user.persist_user(database_name)
                elif e['owner_type'] == 'page':
                    p.persist_page(database_name)


            e.persist_event(database_name)

            if database_name == 'neo':
                posts_node = graph.merge_one("Posts", "parent_id", str(e['id']))
                posts_node['name'] = 'Posts'
                posts_node.push()
                event_node = graph.find_one("Event", "id", str(e['id']))

                event_in_events = Relationship(events_node, "HAS EVENT", event_node)
                graph.create_unique(event_in_events)

                event_has_posts = Relationship(event_node, "HAS POSTS", posts_node)
                graph.create_unique(event_has_posts)

            if database_name == 'mongo':
                if e['owner_type'] == 'page':
                    db.pages.replace_one({'id': p['id']}, p, upsert=True)
                elif e['owner_type'] == 'user':
                    db.users.replace_one({'id': user['id']}, user, upsert=True)

            print("Event {} was persisted".format(i))

            posts = e.get_posts(graph_user)

            j = 1
            for post in posts:

                p = Post()
                for key in post:
                    if not (type(post[key]) == dict or (type(post[key]) == list)):
                        p[key] = post[key]

                if 'likes' in post:
                    p['likes'] = post['likes']['summary']['total_count']

                if 'comments' in post:
                    p['comment_count'] = post['comments']['summary']['total_count']

                if 'shares' in post:
                    p['shares'] = post['shares']['count']

                if 'from' in post:
                    p['from'] = post['from']

                p['parent_id'] = e['id']

                p.persist_post(database_name)

                print("Post {} in event {} was persisted".format(j, i))

                comments = p.get_comments(graph_user)

                k = 1
                for comment in comments:
                    c = Comment()
                    for key in comment:
                        if not (type(comment[key]) == dict or (type(comment[key]) ==  list)):
                            c[key] = comment[key]

                    if 'from' in comment:
                        c['from'] = comment['from']

                    c['post_id'] = p['id']

                    c.persist_comment(database_name)

                    print("Comment {} in post {} in event {} was persisted".format(k, j, i))

                    k += 1

                j += 1
            i += 1