import igraph
import numpy as np
import math
import statistics

def get_node_ids(graph: igraph.Graph, key:str= "name") -> dict:
    """"
    Maps node names to their igraph IDs.

    :param graph: igraph.Graph 
    :param key: String indicating which of ID and name shoudl be used as key in the mapping dictionary

    :return: Dictionary mapping names to igraph IDs

    :raises ValueError: if the key is not either name or index TODO: should I have this restiction? could have other mappings 
    """
    if key == 'name':
        return {v['name']:v.index for v in graph.vs}
    elif key == 'index':
        return {v.index:v['name'] for v in graph.vs}
    else:
        raise ValueError("Not a valid key")


def get_graph_edge_weight(graph: igraph.Graph, edge: tuple) -> float:
    """
    Retrieves the weight of an edge between a pair of nodes. 

    :param graph: igraph.Graph object with weighted edges
    :param edge: A tuple of node names

    :return: A float representing the weight of a graph
    """

    id_dict = get_node_ids(graph) # TODO: cnat regen this every time. Move out? 

    if edge[0] not in graph.vs['name'] or edge[1] not in graph.vs['name']:
        return None # if either node is not in the graph, then the weight is None
    try:
        source = edge[0]
        target = edge[1]
        weight = graph.es.find(_between=((id_dict[source],), (id_dict[target],)))['weight']
    except:
        weight = 0.0 # if node are in the graph but they are not connected, then the weight of an edge between them is None

    return float(weight)




def invert_edge_weights(graph: igraph.Graph) -> igraph.Graph:
    """
    Inverts all edge weights in a graph

    :param graph: igraph.Graph to be inverted

    :return: igraph.Graph which has been inverted

    """
    inverted_graph = graph.copy()

    for edge in inverted_graph.es:
        current_weight = edge["weight"]
        inverted_weight = 1.0 / current_weight 
        edge["weight"] = inverted_weight 

    return inverted_graph  


def sum_metric(graph: igraph.Graph, workflow: list, normalise: bool=True) -> float:
    """
    Calculates the sum (or average if normalised) of edge weights within a workflow.

    :param graph: An igraph.Graph co-citation graph.
    :param workflow: List of edges (tuples of tool PmIDs) representing the workflow.
    :param normalise: Boolean flag indicating whether to normalise the metric.

    :return: Float value of the sum metric.
    """

    weights = []
    print(graph.es.attributes())
    for edge in workflow:
        print(edge)
        weights.append(get_graph_edge_weight(graph, edge))

    if weights:
        if normalise:
            avg_cocite = sum(weights) / len(weights) 
        else:
            avg_cocite = sum(weights)  
        return float(avg_cocite)
    else:
        return 0.0  # If workflow is empty, return 0 as default score

def log_sum_metric(graph: igraph.Graph, workflow: list, normalise: bool=True) -> float:
    """
    Calculates the sum (or average if normalised) of the logarithm of edge weights.

    :param graph: An igraph.Graph object representing the co-citation graph.
    :param workflow: List of edges (tuples of tool PmIDs) representing the workflow.
    :param normalise: Boolean flag indicating whether to normalise the metric (default=True).

    :return: Float value of the log sum metric.
    """
    weights = []
    
    for edge in workflow:
        try:
            weight = get_graph_edge_weight(graph, edge)
            if weight: 
                weights.append(math.log(weight + 1))  # Log of weight + 1 to avoid -inf
        except:
            continue  # Skip edge if it's not in the graph or other exception occurs

    if weights:
        if normalise:
            avg_cocite = sum(weights) / len(weights)  # Average log cocitation when normalised
        else:
            avg_cocite = sum(weights)  # Total log cocitation when not normalised
        return avg_cocite
    else:
        return 0.0  # If no valid weights were calculated, return 0.0 as default score


def degree_norm_sum_metric(graph: igraph.Graph, workflow: list, normalise: bool=True) -> float:
    """
    Normalises edge weights by the average degree of the nodes and sums them up.

    :param graph: An igraph.Graph object representing the co-citation graph.
    :param workflow: List of edges (tuples of tool PmIDs) representing the workflow.
    :param normalise: Boolean flag indicating whether to normalise the metric (default=True).

    :return: Float value of the degree-normalised sum metric.
    """
    weights = []
    id_dict = get_node_ids(graph)

    for edge in workflow:
        if edge[0] not in graph.vs['name'] or edge[1] not in graph.vs['name']:
            weights.append(0)
            continue

        edge_weight = get_graph_edge_weight(graph, edge)
        if edge_weight is None:
            weights.append(0) # fair?
            continue

        source_degree = graph.vs[id_dict[edge[0]]].degree()
        target_degree = graph.vs[id_dict[edge[1]]].degree()

        avg_degree = np.mean([source_degree, target_degree])

        normalised_edge_weight = edge_weight / avg_degree

        weights.append(normalised_edge_weight)

    if not weights:
        return 0.0 

    if normalise:
        norm_score = sum(weights) / len(workflow)
    else:
        norm_score = sum(weights)  

    return float(norm_score)

def prod_metric(graph: igraph.Graph, workflow: list, normalise: bool=True) -> float:
    """
    Calculates the product (or normalised product) of edge weights in a workflow

    :param graph: An igraph.Graph object representing the co-citation graph.
    :param workflow: List of edges (tuples of tool PmIDs) representing the workflow.
    :param normalise: Boolean flag indicating whether to normalise the metric (default=True).

    :return: Float value of the product metric .
    """    
    weights = []
    
    for edge in workflow:
        weights.append( get_graph_edge_weight(graph, edge))

    calculated_weights = [w for w in weights if w] 
    if calculated_weights:
        if normalise:
            prod_weights = np.prod(calculated_weights)/len(weights)
        else:
            prod_weights = np.prod(calculated_weights)
        return float(prod_weights)
    else: 
        return 0.0 # empty workflow has score 0 
    

def logprod_metric(graph: igraph.Graph, workflow: list, normalise: bool=True) -> float:
    """ 
    Calculates the product (or normalised product) of the logarithm of the edge weights in a workflow

    :param graph: An igraph.Graph object representing the co-citation graph.
    :param workflow: List of edges (tuples of tool PmIDs) representing the workflow.
    :param normalise: Boolean flag indicating whether to normalise the metric.

    :return: Float value of the logarithmic product metric.
    """
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
        return float(round(prod_weights, 3))
    else: 
        return 0.0 # empty workflow has score 0 
    

def complete_tree(graph: igraph.Graph, workflow: list, normalise: bool=True) -> float:
    """
    Calculates the sum of the edge weights between all possible pairs of tools in a workflow. 

    :param graph: An igraph.Graph object representing the co-citation graph.
    :param workflow: List of edges (tuples of tool PmIDs) representing the workflow.
    :param normalise: Boolean flag indicating whether to normalise the metric.

    :return: Float value of the logarithmic product metric.
    """   
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
            weight = get_graph_edge_weight(graph, (tool_list[i], tool_list[j]))
            if weight:
                total_weight += weight
    if normalise:
        return total_weight/n
    else:
        return total_weight

#TODO: 1.change names - remove "metric" from the names? 2. Tree should perhaps be renamed 3make completesum not repeat code, rather call the completetree emtric again, or make it an option in the complete tree
def complete_sum(graph: igraph.Graph, workflow: list,  normalise:bool = True, factor:float = 1.0):
    """
    Combination metric of the sum_metric() and complete_tree() metrics, where the edges in the workflow are given more importance.

    :param graph: An igraph.Graph object representing the co-citation graph.
    :param workflow: List of edges (tuples of tool PmIDs) representing the workflow.
    :param normalise: Boolean flag indicating whether to normalise the metric.
    :param factor: Float value specifying how much extra weight the edges that are in the workflow are given relative to the rest of the edges between nodes.
        A factor of 0 gives no extra weight to the workflow edges and thus will give the same value as the regular complete_tree() metric. 

    :return: Float value of the complete three and sum combination metric.
    """   
    tools = set()
    for edge in workflow:
        if edge:
            tools.update(edge)  
    

    total_weight = 0
    tool_list = list(tools)
    n = len(tool_list)
    
    if n==0:
        return 0.0
    
    for i in range(n):
        for j in range(i + 1, n):
            weight = get_graph_edge_weight(graph, (tool_list[i], tool_list[j]))
            if weight:
                total_weight += weight

    if normalise:
        return float(total_weight/n + sum_metric(graph, workflow, normalise = normalise)*factor)
    else:
        return float(total_weight + sum_metric(graph, workflow, normalise = normalise)*factor)
    


def age_norm_sum_metric(graph, workflow, metadata_file, normalise = True) -> float:
    """
    Normalises edge weights by the average ages of the nodes and sums them up.

    :param graph: An igraph.Graph object representing the co-citation graph.
    :param workflow: List of edges (tuples of tool PmIDs) representing the workflow.
    :param metadata_file: The dictionary of tool matadata. TODO: QUESTION: some specific way of referencing a file with a certain type/format of contents?
    :param normalise: Boolean flag indicating whether to normalise the metric (default=True).

    :return: Float value of the age-normalised sum metric.

    """
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
        return 0.0 # empty workflow has score 0 
    
def complete_tree_age_norm(graph, workflow, metadata_file, normalise=True):
    """
    Combination metric of the age_norm_sum_metric() and complete_tree() metrics, where the edges in the workflow are given more importance.

    :param graph: An igraph.Graph object representing the co-citation graph.
    :param workflow: List of edges (tuples of tool PmIDs) representing the workflow.
    :param metadata_file: The dictionary of tool matadata. TODO: QUESTION: some specific way of referencing a file with a certain type/format of contents?
    :param normalise: Boolean flag indicating whether to normalise the metric (default=True).

    :return: Float value of the age-normalised complete_tree() metric.

    """
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





def complete_min(graph, workflow,  normalise = True): 
    """
    The complete_tree() metric which punishes single bad links. 

    :param graph: An igraph.Graph object representing the co-citation graph.
    :param workflow: List of edges (tuples of tool PmIDs) representing the workflow.
    :param normalise: Boolean flag indicating whether to normalise the metric (default=True).

    :return: Float value of the bad edge penalising complete_tree() metric.

    """
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
            weight = get_graph_edge_weight(graph, (tool_list[i], tool_list[j]))
            if weight:
                total_weight.append(weight)
    if len(total_weight)==0:
        return 0
    
    if normalise:
        return sum(total_weight)*min(total_weight)/n
    else:
        return sum(total_weight)*min(total_weight)





def complete_citation(graph, workflow, citation_data_file, normalise = True):
    """
    A variation of the complete_tree() metric, where the edges are divided by the mean number of citations of the source and target.

    :param graph: An igraph.Graph object representing the co-citation graph.
    :param workflow: List of edges (tuples of tool PmIDs) representing the workflow.
    :param metadata_file:  A string of the name of the JSON file containing tool meta data. TODO: QUESTION: some specific way of referencing a file with a certain type/format of contents?
    :param normalise: Boolean flag indicating whether to normalise the metric (default=True).

    :return: Float value of the citation-normalised complete_tree() metric.

    """

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
            weight = get_graph_edge_weight(graph, (tool_list[i], tool_list[j]))
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
    

def citations(workflow:list, citation_data_file:str) -> int:
    """
    Simply returns the median number citations of all of the primary publications of tools in the workflow.
    
    :param graph: An igraph.Graph object representing the co-citation graph.
    :param workflow: List of edges (tuples of tool PmIDs) representing the workflow.
    :param citation_data_file: A string of the name of the JSON file containing citation data. TODO: QUESTION: some specific way of referencing a file with a certain type/format of contents?

    :return: Integer value of the median number of citations.
    
    """
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
        citation_number = [t['nrCitations'] for t in citation_data_file['tools'] if t['pmid'] == tool]
        if citation_number:
            total_citations.append(citation_number[0]) #TODO: this does not work if no results

    if total_citations:
        return statistics.median(total_citations)
    


### BELOW needs updates, not because it does not work, but because it is dumb


# TODO this shoudl just be an option in the previous metric, only diff is if multiplied or divided
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
    
def mult_complete_tree_age_norm(graph, workflow, metadata_file, normalise=True): # TODO this shoudl just be an option in the previous metric, only diff is if multiplied or divided
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
    

   
def sub_complete_tree_age_norm(graph, workflow, metadata_file, normalise=True): # TODO this shoudl just be an option in the previous metric, only diff is if subtracted from today or divided

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
    

  
def sub_complete_tree_age_norm(graph, workflow, metadata_file, normalise=True): #TODO: make this an option in above metric
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
    

    


