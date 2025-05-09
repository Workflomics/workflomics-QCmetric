"""Various for the calculation of tool-level and workflow-level metric scores, their transformation, aggregation and the addition of optional attributes"""
import math
import statistics
from typing import Union, Optional, Tuple

import igraph
import numpy as np


# General functions for interation with graph

def get_node_ids(graph: igraph.Graph, key:str= "pmid") -> dict:
    """"
    Maps node names to their igraph IDs.

    :param graph: igraph.Graph
    :param key: String indicating which of ID and name shoudl be used as key in the mapping dictionary

    :return: Dictionary mapping names to igraph IDs

    :raises ValueError: if the key is not either name or index
    """
    if key == 'pmid':
        return {v['pmid']:v.index for v in graph.vs}
    elif key == 'name':
        return {v['name']:v.index for v in graph.vs}
    elif key == 'index':
        return {v.index:v['pmid'] for v in graph.vs}
    else:
        raise ValueError("Not a valid key")


def get_graph_edge_weight(graph: igraph.Graph,
                        edge: tuple,
                        id_dict: dict,
                        key: str = 'pmid',
                        transform: Optional[str] = None,
                        age_adjustment: bool = False,
                        degree_adjustment: bool = False) -> Union[float, None]:
    """
    Retrieves and optionally adjusts the weight of an edge between two nodes in a graph.

    :param graph: igraph.Graph object representing the graph with weighted edges.
    :param edge: Tuple containing the identifiers (e.g., node names or PMIDs) of
        the two nodes forming the edge.
    :param id_dict: Dictionary mapping node identifiers to their corresponding
        indices in the graph.
    :param key: String specifying the attribute key used to identify nodes in
        the graph. Default is 'pmid'.
    :param transform: Optional string specifying a transformation to apply to
        the edge weight (e.g., "log" or "sqrt"). Default is None.
    :param age_adjustment: Boolean indicating whether to adjust the weight based
        on the age of the nodes. Default is False.
    :param degree_adjustment: Boolean indicating whether to adjust the weight
        based on the degree of the nodes. Default is False.

    :return: Float representing the (possibly adjusted and transformed) weight of
        the edge in the graph.
        Returns None if the nodes do not exist in the graph. Returns 0.0 if the
        edge does not exist in the graph.

    :raises KeyError: If node identifiers in the edge are not found in the id_dict.
    :raises ValueError: If the edge cannot be found in the graph.
    """


    if edge[0] not in graph.vs[key] or edge[1] not in graph.vs[key]:
        return None # If either node is not in the graph, the weight is None
    try:
        source = edge[0]
        target = edge[1]
        weight = graph.es.find(_between=((id_dict[source],), (id_dict[target],)))['weight']
    except (KeyError, ValueError):
        weight = 0.0  # If nodes are in the graph but not connected, the weight between them is 0

    # Transform
    if transform:
        weight = transform_weight(weight=weight, transform = transform)

    # Adjust
    if age_adjustment:
        weight = age_adjust_weight(edge=edge, weight=weight, graph=graph)
    if degree_adjustment:
        weight = degree_adjust_weight(edge=edge, weight=weight, graph=graph, id_dict=id_dict)

    return float(weight)

def calculate_desirability(score: float,
                           thresholds: Tuple[int, int],
                           inverted:bool = False,
                           transform: bool = True,
                           steepness: float = 10.0,
                           midpoint: float = 0.2) -> float:
    """
    Calculates the desirability score of a given score based on specified upper and lower
        thresholds and a steepness parameter.

    :param score: The score for which the desirability score is to be calculated.
    :param thresholds: A tuple containing two integers, representing the lower and upper
        bounds of the desirability range.
    :param steepness: A float controlling how rapidly the desirability increases. Higher
        values increase steepness.
    :param midpoint: A float determining where the rapid increase starts. Should be
        between 0 and 1.

    :return: A float representing the desirability score. Returns 0 if the score is below
        the lower threshold, 1 if the score is above or equal to the upper threshold, and
        a value between 0 and 1 if the score is within the range, scaled according to the
        steepness and midpoint.
    """
    bottom, top = thresholds

    if inverted:
        score = top - score

    if score < bottom:
        return 0
    elif score >= top:
        return 1
    else:
        normalised_score = (score - bottom) / (top - bottom)
        if transform:
            # Sigmoid function with an adjustable midpoint, for high resolution in the beginnning
            return round(1 / (1 + math.exp(-steepness * (normalised_score - midpoint))), 2)
        return normalised_score


# Tool level metric

def tool_average_sum(graph: igraph.Graph,
                     workflow: dict,
                     aggregation_method: str = "sum",
                     transform: Optional[str] = None,
                     age_adjustment: bool = False,
                     degree_adjustment: bool = False,
                     workflow_lvl_metric:str="workflow_average") -> float:
    """
    Calculates the sum or average of edge weights per tool within a workflow.

    :param graph: igraph.Graph object representing a co-citation graph.
    :param workflow: Dictionary containing workflow data. # TODO: Reference the specific schema used for this.
    :param aggregation_method: String specifying the method for aggregating edge weights.
        Options are "sum" or "product". Default is "sum".
    :param transform: Optional string specifying a transformation to apply to edge weights
        (e.g., "log" or "sqrt"). Default is None.
    :param age_adjustment: Boolean indicating whether to adjust edge weights based on the
        age of the nodes. Default is False.
    :param degree_adjustment: Boolean indicating whether to adjust edge weights based on
        the degree of the nodes. Default is False.

    :return: Dictionary where keys are workflow steps and values are the aggregated metric
        scores for each step.

    :raises ValueError: If the workflow is empty or if an invalid aggregation method is provided.
    """

    if workflow_lvl_metric == 'workflow_average':
        workflow_score = workflow_average(graph=graph, workflow=workflow)
    else:
        workflow_score = complete_average(graph=graph, workflow=workflow)

    workflow_desirability = calculate_desirability(score=workflow_score, thresholds=[0, 400])

    steps = list(workflow['steps'].keys())
    edges = workflow['edges']

    if not edges: # If it is an empty workflow
        return {}
    if len(edges) == 1:
        return {steps[0]: 1*workflow_desirability, steps[1]:1*workflow_desirability}

    id_dict = get_node_ids(graph)

    step_scores = {}
    for step in steps:
        score = []
        for edge in edges:
            if step in edge:
                pmid_source = next(
                    pmid
                    for step_id, pmid in workflow['steps'].items()
                    if step_id == edge[0]
                )

                pmid_target = next(
                    pmid
                    for step_id, pmid in workflow['steps'].items()
                    if step_id == edge[1]
                )
                edge = (pmid_source, pmid_target)
                weight = get_graph_edge_weight(
                            graph=graph,
                            edge=edge,
                            id_dict=id_dict,
                            transform=transform,
                            age_adjustment=age_adjustment,
                            degree_adjustment=degree_adjustment
                        ) or 0.0

                score.append(weight)
        if score:
            if aggregation_method == "sum":
                step_scores[step] = round(float(sum(score)/len(score))*workflow_desirability, 2)
            if aggregation_method == "product":
                nonzero_scores = [w for w in score if w!=0]  #only use nonzero weights
                if nonzero_scores:
                    step_scores[step] = round(
                        float(np.prod(nonzero_scores) / len(score)) * workflow_desirability,
                        2
                    )
                return 0.0  # If there are no weights
        else:
            step_scores[step] = 0

    return step_scores

# Workflow level metrics
def shortest_path(graph: igraph.Graph, workflow: list, weighted: bool = True) -> dict:
    """
    Computes shortest paths between each pair of nodes that have an edge in the workflow.

    :param graph: An igraph.Graph co-citation graph.
    :param workflow: List of edges (tuples of tool PmIDs) representing the workflow.
    :param weighted: Boolean indicating whether to compute weighted shortest paths
        (True) or unweighted (False).

    :return: Dictionary where keys are node pairs and values are shortest path distances.
    """
    if not workflow:
        return 0

    id_dict = get_node_ids(graph)

    distances = []

    for edge in workflow:
        u, v = edge

        u_index = id_dict.get(u, None)
        v_index = id_dict.get(v, None)

        if not u_index or not v_index:
            distances.append(10)
            continue

        if weighted:
            path_length = graph.get_shortest_paths(u_index,
                                                   to=v_index,
                                                   weights=graph.es["inverted_weight"],
                                                   output="epath") or 10
        else:
            path_length = graph.get_shortest_paths(u_index, to=v_index, output="epath")
        distances.append(len(path_length[0]))

    avg_distance = sum(distances)/len(workflow)
    return 1/avg_distance if avg_distance != 0 else 0

def workflow_average(graph: igraph.Graph,
                     workflow: Union[list, dict],
                     aggregation_method: str = "sum",
                     transform: Optional[str] = None,
                     age_adjustment: bool = False,
                     degree_adjustment: bool = False) -> float:
    """
    Calculates the sum or average of edge weights within a workflow.

    :param graph: igraph.Graph object representing a co-citation graph.
    :param workflow: List of edges (tuples of tool PMIDs) or a dictionary containing workflow data
        with a 'pmid_edges' key.
    :param aggregation_method: String specifying the method for aggregating edge weights. Options
        are "sum" or "product". Default is "sum".
    :param transform: Optional string specifying a transformation to apply to edge weights
        (e.g., "log" or "sqrt"). Default is None.
    :param age_adjustment: Boolean indicating whether to adjust edge weights based on the age of
        the nodes. Default is False.
    :param degree_adjustment: Boolean indicating whether to adjust edge weights based on the degree
        of the nodes. Default is False.

    :return: Float value representing the average or aggregated sum of edge weights within the
        workflow. 
             Returns 0 if the workflow is empty or if there are no weights.
    """

    if not workflow: # if there are no edges
        return 0

    if isinstance(workflow, dict):
        workflow = workflow['pmid_edges']

    # Get a mapping to the igraph ids
    id_dict = get_node_ids(graph)

    aggregated_weight = []
    for edge in workflow:
        weight = get_graph_edge_weight(
                    graph=graph,
                    edge=edge,
                    id_dict=id_dict,
                    transform=transform,
                    age_adjustment=age_adjustment,
                    degree_adjustment=degree_adjustment
                ) or 0.0  
        aggregated_weight.append(weight)

    if aggregation_method == "sum":
        return round(float(sum(aggregated_weight)/len(workflow)), 2)
    if aggregation_method == "product":
        nonzero_weights = [w for w in aggregated_weight if w!=0]  #only use nonzero weights
        if nonzero_weights:
            score =  np.prod(nonzero_weights) / len(workflow)
            return round(float(score), 2)
        return 0.0  # If there are no weights

def complete_average(graph: igraph.Graph,
                    workflow: Union[dict,list],
                    factor: int = 4,
                    aggregation_method: str = "sum",
                    transform: Optional[str] = None,
                    age_adjustment: bool = False,
                    degree_adjustment: bool = False) -> float:
    # obs the repeated workflows will have a disadvantage because there is no edge between them which defaults to 0. This must be adjusted for in the devision of edges! TODO
    """
    Calculates the sum of the edge weights between all possible pairs of tools in a workflow.
    Named after the degree of connectivity - how close it is to being a complete graph - though this is weighted.

    :param graph: igraph.Graph object representing a co-citation graph.
    :param workflow: List of edges (tuples of tool PMIDs) or a dictionary containing workflow data TODO ref schema
        with a 'pmid_edges' key.
    :param aggregation_method: String specifying the method for aggregating edge weights. Options
        are "sum" or "product". Default is "sum".
    :param transform: Optional string specifying a transformation to apply to edge weights
        (e.g., "log" or "sqrt"). Default is None.
    :param age_adjustment: Boolean indicating whether to adjust edge weights based on the age of
        the nodes. Default is False.
    :param degree_adjustment: Boolean indicating whether to adjust edge weights based on the degree
        of the nodes. Default is False.

    :return: Float value representing the average or aggregated sum of edge weights within the
        workflow. 
             Returns 0 if the workflow is empty or if there are no weights.
    """

    if isinstance(workflow, dict):
        step_names = list(workflow['steps'].keys())
        edges = workflow['edges']
    elif isinstance(workflow, list):
        step_names = list(set(element for tup in workflow for element in tup))
        edges = workflow
    else:
        raise TypeError("Workflow must be a list or a dictionary")

    nr_steps = len(step_names)
    nr_edges = len(edges)
    if nr_edges <1: # if there is only one tool there can be no edges
        return 0.0
    workflow_graph =  igraph.Graph.TupleList(edges, directed=False, weights=False)
    workflow_id_dict = get_node_ids(workflow_graph, key='name')
    full_graph_id_dict = get_node_ids(graph)
    
    aggregated_weight = []
    for i in range( nr_steps ):
        for j in range(i + 1, nr_steps ):
            if isinstance(workflow, dict):
                edge = (workflow['steps'][step_names[i]], workflow['steps'][step_names[j]])
            else:
                edge = (step_names[i], step_names[j])
            weight = get_graph_edge_weight(
                graph=graph,
                edge=edge,
                id_dict=full_graph_id_dict,
                transform=transform,
                age_adjustment=age_adjustment,
                degree_adjustment=degree_adjustment
            ) or 0.0
            u_index = workflow_id_dict.get(step_names[i], None)
            v_index = workflow_id_dict.get(step_names[j], None)
            
            path = workflow_graph.get_shortest_paths(u_index, to=v_index, output="epath") or None # if there is none then sth is wrong
            path_length= len(path[0])
            normalised_weight = weight / factor**(float(path_length)-1) if path_length else 0
            aggregated_weight.append(normalised_weight)

    if aggregation_method == "sum":
        return round(float(sum(aggregated_weight)/nr_edges), 2)
    if aggregation_method == "product":
        nonzero_weights = [w for w in aggregated_weight if w!=0]  #only use nonzero weights
        if nonzero_weights:
            score =  np.prod(nonzero_weights) /nr_edges
            return round(float(score), 2)
        return 0.0  # If there are no weights

def transform_weight(weight: int, transform: str) -> float:
    """
    Applies a mathematical transformation to the given weight.

    :param weight: Integer value representing the weight to be transformed.
    :param transform: String specifying the transformation to apply. 
        Options include "log" for logarithmic transformation and "sqrt" for
        square root transformation.
    :return: Transformed weight as a float.
    :raises ValueError: If an invalid transformation option is provided.
    """
    if transform == "log":
        return math.log(weight + 1)  # Log of weight + 1 to avoid -inf    
    elif transform == "sqrt":
        return math.sqrt(weight)
    else:
        raise ValueError("Invalid transformation option")

def degree_adjust_weight(edge: tuple, weight, graph: igraph.Graph, id_dict: dict) -> float:
    """
    Adjusts the weight of an edge based on the average degree of its connected nodes.

    :param edge: Tuple representing the edge (source, target).
    :param weight: Float value of the initial weight of the edge.
    :param graph: An igraph.Graph object representing the graph.
    :param id_dict: Dictionary mapping node identifiers to their indices in the graph.
    :return: Weight adjusted by the average degree of the connected nodes.
    """
    source_degree = graph.vs[id_dict[edge[0]]].degree()
    target_degree = graph.vs[id_dict[edge[1]]].degree()

    min_degree = max(1, min([source_degree, target_degree]))
    return weight / min_degree

def age_adjust_weight(edge: tuple,
                      weight: float,
                      graph: igraph.Graph,
                      default_age = 10,
                      key: str = 'pmid') -> float:
    """
    Adjusts the weight of an edge based on the age of its connected nodes.

    :param edge: Tuple representing the edge (source, target).
    :param weight: Float value of the initial weight of the edge.
    :param graph: An igraph.Graph object representing the graph.
    :param default_age: Integer value representing the default age to use if node age
        is not found. Default is 10.
    :param key: String specifying the attribute key to look up node age in the graph.
        Default is 'pmid'.
    :return: Weight adjusted by the minimum age of the connected nodes.
    """

    source_age = next((vs['age'] for vs in graph.vs if vs[key] == edge[0]), default_age)
    target_age = next((vs['age'] for vs in graph.vs if vs[key] == edge[1]), default_age)
    min_age = max(1, min([source_age, target_age]))
    return weight / min_age

def citation_adjusted_weight(edge: tuple,
                            weight: float,
                            graph: igraph.Graph,
                            default_nr_citations = 100,
                            key: str = 'pmid') -> float:
    """
    Adjusts the weight of an edge based on the number of citations of its connected nodes.

    :param edge: Tuple representing the edge (source, target).
    :param weight: Float value of the initial weight of the edge.
    :param graph: An igraph.Graph object representing the graph.
    :param default_nr_citations: Integer value representing the default number of citations
        to use if node citation count is not found. Default is 100.
    :param key: String specifying the attribute key to look up node citation count in the
        graph. Default is 'pmid'.
    :return: Weight adjusted by the minimum citation count of the connected nodes.
    """

    source_citations = next((vs['nr_citations']
                             for vs in graph.vs
                             if vs[key] == edge[0]),
                             default_nr_citations)
    target_citations = next((vs['nr_citations']
                             for vs in graph.vs
                             if vs[key] == edge[1]),
                             default_nr_citations)

    min_citations = max(1, min([source_citations, target_citations]))

    return weight / min_citations 

def median_citations(graph: igraph.Graph,
                     workflow:Union[dict,list],
                     default_nr_citations: int = 0) -> int:
    """
    Simply returns the median number citations of all of the primary publications 
        of tools in the workflow.

    :param graph: An igraph.Graph object representing the co-citation graph.
    :param workflow: List of edges (tuples of tool PmIDs) representing the workflow.
    :param default_nr_citations: An int representing the value one would like to use 
        for tools that dont have a recorded citation number. 

    :return: Integer value of the median number of citations.
    
    """
    if isinstance(workflow, dict):
        pmids = list(workflow['steps'].values())
    elif isinstance(workflow, list):
        pmids = list(set(element for tup in workflow for element in tup))
    else:
        raise TypeError

    total_citations = []

    if len(pmids)==0:
        return 0

    for pmid in pmids:
        citation_number = next((vs['nr_citations']
                                for vs in graph.vs
                                if vs['pmid'] == pmid),
                                default_nr_citations)
        if citation_number:
            total_citations.append(citation_number)

    if total_citations:
        return statistics.median(total_citations)
    return None
