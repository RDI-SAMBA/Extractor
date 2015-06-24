from .entities import *

class PageSearcher(Searcher):
    def search_pages(self, search_string, graph):
        pages = []
        while True:
            try:
                pages = graph.request('search', args={'q': search_string, 'type': 'page',
                                                      'fields': 'id,likes,name'})['data']
                break
            except:
                pass
        return pages

    def get_pages(self, pages_ids, graph):
        pages = []
        i = 0
        while i < len(pages_ids):
            while True:
                try:
                    temp_list = graph.get_objects(ids=pages_ids[i:min(i+50, len(pages_ids))])
                    break
                except:
                    pass
            [pages.append(temp_list[idd]) for idd in temp_list]
            i += 50
        return pages

    def order_pages_by_likes(self, pages, size, reverse=True):
        ordered_pages = super(PageSearcher, self).order_by(input_list=pages, key=lambda page: page['likes'], size=size, reverse=reverse)
        return ordered_pages


    def order_pages_by_talking_about_count(self, pages, size, reverse=True):
        ordered_pages = super(PageSearcher, self).order_by(input_list=pages, key=lambda page: page['talking_about_count'], size=size, reverse=reverse)
        return ordered_pages


    def order_pages_by_were_here_count(self, pages, size, reverse=True):
            ordered_pages = super(PageSearcher, self).order_by(input_list=pages, key=lambda page: page['were_here_count'], size=size, reverse=reverse)
            return ordered_pages


    def order_pages_by_checkins(self, pages, size, reverse=True):
            ordered_pages = super(PageSearcher, self).order_by(input_list=pages, key=lambda page: page['checkins'], size=size, reverse=reverse)
            return ordered_pages

####################################################################################################################

    def run_facebook_pages(self, search_string, database_name):

        if database_name == 'neo':
            pages_node = graph.merge_one("Pages", "name", "PAGES")
            facebook_node = graph.find_one("Facebook", "name", 'FACEBOOK')
            facebook_has_pages = Relationship(facebook_node, "HAS PAGES", pages_node)
            graph.create_unique(facebook_has_pages)

        pages = []
        list_words = str(search_string).split('-')

        for word in list_words:
            results = self.search_pages(word, graph=graph_app)
            for result in results:
                pages.append(result)
        
        searcher = Searcher()
        pages = searcher.remove_duplicates(pages)
        pgs = pages
        pages =[]

        for pg in pgs:
            b = False
            lwn = pg['name'].split(' ')
            for word in list_words:
                word = word.lstrip().rstrip().lower()
                if len(word.split(' ')) > 1:
                    if word.lstrip().rstrip().lower() in pg['name'].lower():
                        b = True
                else:
                    for n in lwn:
                        if str(word).lstrip().rstrip().lower() == str(n).lower():
                            b = True
            if b:
                pages.append(pg)


        sorted_pages = searcher.order_by(pages, key=lambda page: page['likes'], size=10)
        sorted_pages = self.get_pages([page['id'] for page in sorted_pages], graph=graph_app)
        sorted_pages = searcher.order_by(sorted_pages, key=lambda page: page['likes'], size=10)

        print('------------------ POPULAR PAGES FOR {} ON FACEBOOK ------------------ \n'.format(search_string))
        for page in sorted_pages:
            print('Id :', page['id'], 'Name :', page['name'], 'Likes :', page['likes'])

        pages_list = []
        for page in sorted_pages:
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
            pages_list.append(p)

        i = 1
        for page in pages_list:

            page.persist_page(database_name)


            if database_name == 'neo':
                posts_node = graph.merge_one("Posts", "parent_id", str(page['id']))
                posts_node['name'] = 'Posts'
                posts_node.push()
                page_node = graph.find_one("Page", "id", str(page['id']))


                page_in_pages = Relationship(pages_node, "HAS PAGE", page_node)
                graph.create_unique(page_in_pages)


                page_has_posts = Relationship(page_node, "HAS POSTS", posts_node)
                graph.create_unique(page_has_posts)

            print ( "Page {} was persisted".format(i))


            posts = page.get_posts(graph_app)





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

                p['parent_id'] = page['id']

                p.persist_post(database_name)

                print("Post {} in page {} was persisted".format(j, i))


                comments = p.get_comments(graph_app)

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

                    print("Comment {} in post {} in page {} was persisted".format(k, j, i))


                    k += 1

                j += 1
            i += 1

