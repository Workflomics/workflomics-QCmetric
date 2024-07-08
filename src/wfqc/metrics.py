import igraph
import numpy as np
import math



def get_node_ids(graph: igraph.Graph, key:str= "name") -> dict:
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




def invert_edge_weights(G):
    inverted_G = G.copy()

    for edge in inverted_G.es:
        current_weight = edge["weight"]
        inverted_weight = 1.0 / current_weight 
        edge["weight"] = inverted_weight 

    return inverted_G  


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
    if not calculated_weights:
        return 0.0 # empty workflow has score 0 
        
    if normalise:
        norm_score = sum(calculated_weights)/len(weights) # avg cocitations
    else: 
        norm_score = sum(calculated_weights)
        
    return float(norm_score)        



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
            print(get_graph_edge_weight(graph, edge) + 1)
            print( math.log(get_graph_edge_weight(graph, edge) + 1)) 
            weights.append( math.log(get_graph_edge_weight(graph, edge) + 1)) # adding 1 to avoid - inf
        except:
            continue # if the edge does not exist 

    calculated_weights = [w for w in weights if w] 
    print(calculated_weights)
    if calculated_weights:
        if normalise:
            prod_weights = np.prod(calculated_weights)/len(weights)
            print(prod_weights)
        else:
            prod_weights  = np.prod(calculated_weights)
        return float(round(prod_weights, 3))
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


def complete_sum(G, workflow,  normalise = True):
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

    factor = 1
    if normalise:
        return total_weight/n + sum_metric(G, workflow, normalise = normalise)*factor
    else:
        return total_weight + sum_metric(G, workflow, normalise = normalise)*factor
    


def age_norm_sum_metric(graph, workflow, metadata_file, normalise = True):
    weights = []

    id_dict = get_node_ids(graph)

    for edge in workflow:

        if edge[0] not in graph.vs['name'] or edge[1] not in graph.vs['name']:
            weights.append(0)
            continue

        edge_weight = get_graph_edge_weight(graph, edge)

        source_age = [tool['pubDate'] for tool in metadata_file['tools'] if tool['pmid'] == edge[0]]
        target_age = [tool['pubDate'] for tool in metadata_file['tools'] if tool['pmid'] == edge[1]]


        if source_age or target_age:        
            ages = [age for age in (source_age + target_age) if age ]
            
            
            avg_age = np.mean( ages ) # perhaps too harsh 

            normalised_edge_weight = edge_weight/ avg_age

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
    
def complete_tree_age_norm(graph, workflow, metadata_file, normalise=True):
    tools = set()
    for edge in workflow:
        if edge:
            tools.update(edge)
    
    total_weight = 0
    tool_list = list(tools)
    n = len(tool_list)
    
    if n == 0:
        return 0

    for i in range(n):
        for j in range(i + 1, n):
            edge = (tool_list[i], tool_list[j])
            
            if edge[0] not in graph.vs['name'] or edge[1] not in graph.vs['name']:
                continue

            edge_weight = get_graph_edge_weight(graph, edge)
            if not edge_weight:
                continue

            source_age = [tool['pubDate'] for tool in metadata_file['tools'] if tool['pmid'] == edge[0]]
            target_age = [tool['pubDate'] for tool in metadata_file['tools'] if tool['pmid'] == edge[1]]
            ages = [age for age in (source_age + target_age) if age]

            if ages:
                avg_age = np.mean(ages)
                normalised_edge_weight = edge_weight / avg_age
                total_weight += normalised_edge_weight
            else:
                continue # nrom bu mean?

    if normalise:
        return float(total_weight) / n
    else:
        return float(total_weight)
    


def mult_age_norm_sum_metric(graph, workflow, metadata_file, normalise = True):
    weights = []

    id_dict = get_node_ids(graph)

    for edge in workflow:

        if edge[0] not in graph.vs['name'] or edge[1] not in graph.vs['name']:
            weights.append(0)
            continue

        edge_weight = get_graph_edge_weight(graph, edge)

        source_age = [tool['pubDate'] for tool in metadata_file['tools'] if tool['pmid'] == edge[0]]
        target_age = [tool['pubDate'] for tool in metadata_file['tools'] if tool['pmid'] == edge[1]]

        ages = [age for age in (source_age + target_age) if age ]
        
        
        avg_age = np.mean( ages ) # perhaps too harsh 

        normalised_edge_weight = edge_weight* avg_age

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
    
def mult_complete_tree_age_norm(graph, workflow, metadata_file, normalise=True):
    tools = set()
    for edge in workflow:
        if edge:
            tools.update(edge)
    
    total_weight = 0
    tool_list = list(tools)
    n = len(tool_list)
    
    if n == 0:
        return 0

    for i in range(n):
        for j in range(i + 1, n):
            edge = (tool_list[i], tool_list[j])
            
            if edge[0] not in graph.vs['name'] or edge[1] not in graph.vs['name']:
                continue

            edge_weight = get_graph_edge_weight(graph, edge)
            if not edge_weight:
                continue

            source_age = [tool['pubDate'] for tool in metadata_file['tools'] if tool['pmid'] == edge[0]]
            target_age = [tool['pubDate'] for tool in metadata_file['tools'] if tool['pmid'] == edge[1]]
            ages = [age for age in (source_age + target_age) if age]

            if ages:
                avg_age = np.mean(ages)
                normalised_edge_weight = edge_weight * avg_age
                total_weight += normalised_edge_weight

    if normalise:
        return float(total_weight) / n
    else:
        return float(total_weight)
    

   
def sub_complete_tree_age_norm(graph, workflow, metadata_file, normalise=True):
    tools = set()
    for edge in workflow:
        if edge:
            tools.update(edge)
    
    total_weight = 0
    tool_list = list(tools)
    n = len(tool_list)
    
    if n == 0:
        return 0

    for i in range(n):
        for j in range(i + 1, n):
            edge = (tool_list[i], tool_list[j])
            
            if edge[0] not in graph.vs['name'] or edge[1] not in graph.vs['name']:
                continue

            edge_weight = get_graph_edge_weight(graph, edge)
            if not edge_weight:
                continue

            source_age = [tool['pubDate'] for tool in metadata_file['tools'] if tool['pmid'] == edge[0]]
            target_age = [tool['pubDate'] for tool in metadata_file['tools'] if tool['pmid'] == edge[1]]
            ages = [age for age in (source_age + target_age) if age]

            if ages:
                avg_age = np.mean(ages)
                normalised_edge_weight = edge_weight / (2025 - avg_age) # 2025 so no zero div
                total_weight += normalised_edge_weight
            else:
                continue # nrom bu mean?

    if normalise:
        return float(total_weight) / n
    else:
        return float(total_weight)
    



   
  
def sub_complete_tree_age_norm(graph, workflow, metadata_file, normalise=True): 
    tools = set()
    for edge in workflow:
        if edge:
            tools.update(edge)
    
    total_weight = 0
    tool_list = list(tools)
    n = len(tool_list)
    
    if n == 0:
        return 0

    for i in range(n):
        for j in range(i + 1, n):
            edge = (tool_list[i], tool_list[j])
            
            if edge[0] not in graph.vs['name'] or edge[1] not in graph.vs['name']:
                continue

            edge_weight = get_graph_edge_weight(graph, edge)
            if not edge_weight:
                continue

            source_age = [tool['pubDate'] for tool in metadata_file['tools'] if tool['pmid'] == edge[0]]
            target_age = [tool['pubDate'] for tool in metadata_file['tools'] if tool['pmid'] == edge[1]]
            ages = [age for age in (source_age + target_age) if age]

            if ages:
                avg_age = np.mean(ages)
                normalised_edge_weight = edge_weight / (2025 - avg_age) # 2025 so no zero div
                total_weight += normalised_edge_weight
            else:
                continue # nrom bu mean?

    if normalise:
        return float(total_weight) / n
    else:
        return float(total_weight)
    

    



def complete_min(G, workflow,  normalise = True): # punishes single bad link 
    tools = set()
    for edge in workflow:
        if edge:
            tools.update(edge)  
    

    total_weight = []
    tool_list = list(tools)
    n = len(tool_list)
    
    if n==0:
        return 0
    
    for i in range(n):
        for j in range(i + 1, n):
            weight = get_graph_edge_weight(G, (tool_list[i], tool_list[j]))
            if weight:
                total_weight.append(weight)
    if len(total_weight)==0:
        return 0
    
    if normalise:
        return sum(total_weight)*min(total_weight)/n
    else:
        return sum(total_weight)*min(total_weight)





def complete_citation(G, workflow, citation_data_file, normalise = True): # punishes single bad link 
    tools = set()
    for edge in workflow:
        if edge:
            tools.update(edge)  
    

    total_weight = []
    tool_list = list(tools)
    n = len(tool_list)
    
    if n==0:
        return 0
    
    for i in range(n):
        for j in range(i + 1, n):
            weight = get_graph_edge_weight(G, (tool_list[i], tool_list[j]))
            if weight:
                citations_source = [tool['nrCitations'] for tool in citation_data_file['tools'] if tool['pmid'] == tool_list[i]]
                citations_target = [tool['nrCitations'] for tool in citation_data_file['tools'] if tool['pmid'] == tool_list[j]]
                citations = [c for c in (citations_source + citations_target) if c]

                if citations:
                    total_weight.append(weight/citations)
                else:
                     total_weight.append(weight)
    if len(total_weight)==0:
        return 0
    
    if normalise:
        return sum(total_weight)*min(total_weight)/n
    else:
        return sum(total_weight)*min(total_weight)
    

def citations( workflow, citation_data_file, normalise = True):
    tools = set()
    for edge in workflow:
        if edge:
            tools.update(edge)  
    

    total_citations = []
    tool_list = list(tools)
    n = len(tool_list)
    
    if n==0:
        return 0
    
    for tool in tool_list:
        total_citations.append([t['nrCitations'] for t in citation_data_file['tools'] if t['pmid'] == tool])
    if normalise:
        return sum([c[0] for c in total_citations if c])/n
    else:
        return sum([c for c in total_citations if c])