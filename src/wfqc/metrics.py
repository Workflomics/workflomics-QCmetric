import igraph
import numpy as np



def get_node_ids(graph: igraph.Graph, key= "name"):
    # connect names to igraph ids
    if key == 'name':
        return {v['name']:v.index for v in graph.vs}
    elif key == 'index':
        return {v.index:v['name'] for v in graph.vs}
    else:
        print("Not a valid key")
        return {}


def get_graph_edge_weight(graph, edge):

    id_dict = get_node_ids(graph)

    if edge[0] not in graph.vs['name'] or edge[1] not in graph.vs['name']:
        return None 
    try:
        source = edge[0]
        target = edge[1]
        weight = graph.es.find(_between=((id_dict[source],), (id_dict[target],)))['weight']
    except:
        weight = 0

    return weight


import math

def simple_sum_metric(graph, workflow):

    weights = []
    
    for edge in workflow:
        weights.append( get_graph_edge_weight(graph, edge))

    if weights:
        return sum([w for w in weights if w])
    else: 
        return 0 # empty workflow has score 0 

def sum_metric(graph, workflow, normalise = True):

    weights = []
    
    for edge in workflow:
        weights.append( get_graph_edge_weight(graph, edge))

    if weights:
        if normalise:
            avgcocite = sum([w for w in weights if w])/len(weights) # avg cocitations
        else:
            avgcocite = sum([w for w in weights if w])
        return avgcocite
    else: 
        return 0 # empty workflow has score 0 
    

def log_sum_metric(graph, workflow, normalise = True):

    weights = []
    
    for edge in workflow:
        try:
            weight = get_graph_edge_weight(graph, edge)
            if weight: # nvm there was some problem improting? 
                weights.append( math.log(weight + 1)) # adding 1 to avoid - inf
        except:
            continue # if that edge is not in the graph 

    calculated_weights = [w for w in weights if w] 
    if calculated_weights:
        if normalise:
            avgcocite = sum(calculated_weights)/len(weights) # avg cocitations
        else:
            avgcocite = sum(calculated_weights)
        return avgcocite
    else: 
        return 0 # empty workflow has score 0 


def degree_norm_sum_metric(graph, workflow, normalise = True):
    weights = []

    id_dict = get_node_ids(graph)

    for edge in workflow:

        if edge[0] not in graph.vs['name'] or edge[1] not in graph.vs['name']:
            weights.append(0)
            continue

        edge_weight = get_graph_edge_weight(graph, edge)

        source_degree = graph.vs[id_dict[edge[0]] ].degree() 
        target_degree = graph.vs[id_dict[edge[1]] ].degree() 

        avg_degree = np.mean( [source_degree, target_degree] ) # perhaps too harsh 

        normalised_edge_weight = edge_weight/ avg_degree

        weights.append(normalised_edge_weight)

    calculated_weights = [w for w in weights if w] 
    if calculated_weights:
        if normalise:
            norm_score = sum(calculated_weights)/len(weights) # avg cocitations
        else: 
            norm_score = sum(calculated_weights)
        return float(norm_score)
    else: 
        return 0 # empty workflow has score 0 



def prod_metric(graph, workflow, normalise = True):
    weights = []
    
    for edge in workflow:
        weights.append( get_graph_edge_weight(graph, edge))

    calculated_weights = [w for w in weights if w] 
    if calculated_weights:
        if normalise:
            prod_weights = np.prod(calculated_weights)/len(weights)
        else:
            prod_weights = np.prod(calculated_weights)
        return int(prod_weights)
    else: 
        return 0 # empty workflow has score 0 
    

def logprod_metric(graph, workflow, normalise = True):
    weights = []
    
    for edge in workflow:
        try:
            weights.append( math.log(get_graph_edge_weight(graph, edge) + 1)) # adding 1 to avoid - inf
        except:
            continue # if the edge does not exist 

    calculated_weights = [w for w in weights if w] 
    if calculated_weights:
        if normalise:
            prod_weights = np.prod(calculated_weights)/len(weights)
        else:
            prod_weights  = np.prod(calculated_weights)
        return int(prod_weights)
    else: 
        return 0 # empty workflow has score 0 
    

def complete_tree(G, workflow,  normalise = True):
    tools = set()
    for edge in workflow:
        if edge:
            tools.update(edge)  
    

    total_weight = 0
    tool_list = list(tools)
    n = len(tool_list)
    
    if n==0:
        return 0
    
    for i in range(n):
        for j in range(i + 1, n):
            weight = get_graph_edge_weight(G, (tool_list[i], tool_list[j]))
            if weight:
                total_weight += weight
    if normalise:
        return total_weight/n
    else:
        return total_weight



























# ###
# def sum_metric_citation(graph, workflow): # cocitation metric 

#     """
#     Calculates the cocitation  metric for a given workflow and a given citation (OBS not cocitation) graph
    
#     Parameters
#     ----------
#     graph : igraph.Graph
#         Graph generated by igraph
#     workflow, list of tuples with pairs of strings TODO: how do I write this? does it matter I wont have this format later anyways? 
#         List of tuples of strings corresponding to the edges in the workflow. 

#     """
#     # List to  collect pairwise scores
#     score_list = [] # TODO: can predefine the list length, does not matter this is temporary?

#     for pair in workflow:
#         cocite_score = 0
#         neighbors_of_first = set(graph.neighbors(pair[0]))
#         neighbors_of_second = set(graph.neighbors(pair[1]))

#         # Count number of common neighbours
#         common_neighbors = neighbors_of_first.intersection(neighbors_of_second)
#         cocite_score = len(common_neighbors)
#         score_list.append(cocite_score)

#     # Then sum the scores or perform any other desired calculation
#     # now normalising by WF length
#     # maybe call this one "support", since that is basically what we have. 

#     return sum(score_list)/len(score_list), score_list



# def path_metric(G, workflow, included_tools): #TODO: how normalise this?
#     # shortest path == shortest path of the subpaths. Thus:

#     shortest_paths = []

#     for edge in workflow:
#         source = edge[0]
#         target = edge[1]

#         if source in included_tools and target in included_tools:
#             shortest_paths.append(G.get_shortest_paths(source, to = target))
#         else:
#             shortest_paths.append(None)


#     return shortest_paths


# def sum_metric(G, workflow, included_tools): # cocitation metric 

#     # shortest path == shortest path of the subpaths. Thus:

#     shortest_paths = []

#     for edge in workflow:
#         source = edge[0]
#         target = edge[1]

#         if source in included_tools and target in included_tools: # TODO: check: does igraph handle this already?
#             shortest_paths.append(igraph_weighted_shortest_path(G, source, target))
#         else:
#             shortest_paths.append(None) #none?
#         sum_paths = sum([i for i in shortest_paths if i != None])
#     return sum_paths/len(shortest_paths), shortest_paths




# def sum_shortest_path_metric(G, workflow, included_tools): # cocitation metric 

#     # shortest path == shortest path of the subpaths. Thus:

#     shortest_paths = []

#     for edge in workflow:
#         source = edge[0]
#         target = edge[1]

#         if source in included_tools and target in included_tools: # TODO: check: does igraph handle this already?
#             shortest_paths.append(igraph_weighted_shortest_path(G, source, target))
#         else:
#             shortest_paths.append(None) #none?
#     sum_paths = sum([i for i in shortest_paths if i != None])
#     return sum_paths/len(shortest_paths), shortest_paths




# def igraph_weighted_shortest_path(G, source, target):
#     try: 
#         results = G.get_shortest_paths(source, to=target, weights=G.es["weight"], output="epath")
#     except: # in case they are both in the graph but disconnected
#         results = None 

#     if results and len(results[0]) > 0:
#         distance = 0
#         for e in results[0]:
#             distance += G.es[e]["weight"]
#         return distance
#     else:
#         return None