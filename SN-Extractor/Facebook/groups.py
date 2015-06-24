from .entities import *


class GroupSearcher(Searcher):

    def get_open_groups(self, groups):
        open_groups = []
        for group in groups:
            if 'privacy' in group and group['privacy'] == 'OPEN':
                open_groups.append(group)
        return open_groups

    def order_groups_by_members(self, groups, size, reverse=True):
        ordered_groups = Searcher.order_by(input_list=groups, key=lambda group: group['member_count'], size=size, reverse=reverse)
        return ordered_groups

    def search_groups(self, search_term, graph):
        groups = []
        while True:
            try:
                groups = graph.request('search', args={'q': search_term, 'type': 'group', 'limit': '1000',
                                                       'fields': groups_request_string})['data']
                break
            except:
                pass
        return groups

    def run_facebook_groups(self, search_string, database_name):


        if database_name == 'neo':
            groups_node = graph.merge_one("Groups", "name", "GROUPS")
            facebook_node = graph.find_one("Facebook", "name", 'FACEBOOK')
            facebook_has_groups = Relationship(facebook_node, "HAS GROUPS", groups_node)
            graph.create_unique(facebook_has_groups)

        grps = []
        list_words = str(search_string).split('-')

        for word in list_words:
            results = self.search_groups(word, graph=graph_user)
            grps.append(results)


        grp =[]
        searcher = Searcher()
        for gp in grps:
            gp = searcher.remove_duplicates(gp)
            gp = self.get_open_groups(gp)
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
        groups = []
        for g in grp:
            for l in g[0:d]:
                groups.append(l)

        groups = searcher.remove_duplicates(groups)










        print('------------------ POPULAR GROUPS FOR {} ON FACEBOOK ------------------ \n'.format(search_string))
        for group in groups:
            print('Id :', group['id'], 'Name :', group['name'])


        i = 1
        for group in groups:
            g = Group()
            for key in group:
                if not (type(group[key]) == dict or (type(group[key]) == list)):
                    g[key] = group[key]

            if 'cover' in group:
                g['cover_url'] = group['cover']['source']

            if 'owner' in group:
                if 'category' in group['owner']:
                    g['owner_type'] = 'page'
                    page = graph_app.get_object(id=group['owner']['id'])
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
                    g['owner_type'] = 'user'
                    user = FacebookUser(group['owner']['name'], group['owner']['id'])

                g['owner_id'] = group['owner']['id']



            if 'owner_type' in g:
                if g['owner_type'] == 'user':
                    user.persist_user(database_name)
                elif g['owner_type'] == 'page':
                    p.persist_page(database_name)


            g.persist_group(database_name)

            if database_name == 'neo':
                posts_node = graph.merge_one("Posts", "parent_id", str(g['id']))
                posts_node['name'] = 'Posts'
                posts_node.push()
                group_node = graph.find_one("Group", "id", str(g['id']))


                group_in_groups = Relationship(groups_node, "HAS GROUP", group_node)
                graph.create_unique(group_in_groups)


                group_has_posts = Relationship(group_node, "HAS POSTS", posts_node)
                graph.create_unique( group_has_posts)

            if database_name == 'mongo':
                if g['owner_type'] == 'page':
                    db.pages.replace_one({'id': p['id']}, p, upsert=True)
                elif g['owner_type'] == 'user':
                    db.users.replace_one({'id': user['id']}, user, upsert=True)



            print("Group {} was persisted".format(i))

            posts = g.get_posts(graph_user)

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

                p['parent_id'] = g['id']

                p.persist_post(database_name)

                print("Post {} in group {} was persisted".format(j, i))

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

                    print("Comment {} in post {} in group {} was persisted".format(k, j, i))

                    k += 1

                j += 1
            i += 1