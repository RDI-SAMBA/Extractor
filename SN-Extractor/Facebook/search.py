
class Searcher:
    def get_edges(self, node_id, request_string, graph):
        edges = []
        current_page = {}
        while 'data' not in current_page:
            try:
                current_page = graph.request(node_id+request_string)
            except:
                pass
        for edge in current_page['data']:
            edges.append(edge)
        # print(len(edges))
        while 'paging' in current_page and 'next' in current_page['paging']:
            temp_page = current_page
            current_page = {}
            while 'data' not in current_page:
                try:
                    current_page = graph.request(temp_page['paging']['next'][32:])
                except:
                    pass
            for edge in current_page['data']:
                edges.append(edge)
            #print(len(edges))
        return edges


    def order_by(self, input_list, key, size=10, reverse=True):
        sorted_result_list = sorted(input_list, key=key, reverse=reverse)
        sorted_result_list = sorted_result_list[0:size]
        return sorted_result_list


    def remove_duplicates(self, edges):
        no_dups = []
        ids = [elem['id'] for elem in edges]
        for i in range(len(edges)):
            if edges[i]['id'] in ids[i+1:]:
                continue
            no_dups.append(edges[i])
        return no_dups