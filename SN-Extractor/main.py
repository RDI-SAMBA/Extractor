from social_network_miner import SocialNetworkMiner
from settings import *
from multiprocessing.context import Process
from time import sleep

if __name__ == '__main__':
    try:/home/mahdi/workspace
        search_list = input("enter a '-' separated list of search words: ")
        
        
        database_name = None
        while not (database_name == 'neo' or database_name == 'mongo'):
            database_name = input("enter a database name ('mongo' or 'neo') : ")
            database_name = database_name.rstrip().lstrip().lower()
        
        ind = False
        while not ind:
            social_networks = input("enter a '-' separated list of social networks: ")
            sns = social_networks.split('-')
            ind = True
            for social_network in sns:
                sn = str(social_network).rstrip().lstrip().lower()
                if not (sn == 'facebook' or sn =='twitter'):
                    ind = False
                    break
            continue
            
        
        if database_name == 'neo':
            sn_node = graph.merge_one("SN", "name", "SOCIALNETWORKS")
    
    
        processes = []
        for social_network in sns:
            sn = SocialNetworkMiner.factory(social_network.lstrip().rstrip().lower())
            p = Process(target=sn.get_data_from_sn, args=(search_list, database_name,))
            processes.append(p)
    
        for p in processes:
            p.start()
            
    
        for p in processes:
            p.join()
    except Exception as e:
        print(e)