"""
Bibliographic graph creation
"""
import os
from tqdm import tqdm       
import pickle
from datetime import datetime
import json
import aiohttp
import igraph 
import sys
from typing import Optional

sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), 'src')))
import pubmetric.data 
from pubmetric.log import log_with_timestamp


def add_graph_attributes(graph: igraph.Graph, metadata_file: dict):
    """
    Implement now that you know how it works
    """

    for edge in graph.es:
        current_weight = edge["weight"]
        inverted_weight = 1.0 / current_weight if current_weight != 0 else float('inf')
        edge["inverted_weight"] = inverted_weight
         
         # add edge normalisation here

    for vertex in graph.vs:
        pmid = vertex["name"]
        tool_metadata = next((tmd for tmd in metadata_file['tools'] if tmd['pmid'] == pmid))

        vertex['pmid'] = pmid
        vertex["name"] = tool_metadata['name']  # changing name to name 
        vertex["age"] = datetime.now().year - int(tool_metadata.get('pubDate') or (datetime.now().year - 100)) # default 100 years if publication is None
        vertex["nr_citations"] = tool_metadata['nrCitations'] 

    return graph

def add_inverted_edge_weights(graph: igraph.Graph) -> igraph.Graph:
    """
    Adds an 'inverted_weight' attribute to all edges in the graph.

    :param graph: igraph.Graph to which inverted weights will be added

    :return: igraph.Graph with the added 'inverted_weight' attribute
    """
    inverted_graph = graph.copy()

    for edge in inverted_graph.es:
        current_weight = edge["weight"]
        inverted_weight = 1.0 / current_weight if current_weight != 0 else float('inf')
        edge["inverted_weight"] = inverted_weight

    return inverted_graph

def normalise_weight(graph_stats: list, weight: float):
    return

def add_norm_edge_weights(graph: igraph.Graph) -> igraph.Graph:
    """
    Adds an 'inverted_weight' attribute to all edges in the graph.

    :param graph: igraph.Graph to which inverted weights will be added

    :return: igraph.Graph with the added 'inverted_weight' attribute
    """
    normalised_graph = graph.copy() # TODO: should I copy or just update?

    ### calculate graph stats to norm:
    graph_stats = []
    # ... populate graph_stats

    for edge in normalised_graph.es:
        current_weight = edge["weight"]
        norm_weight = normalise_weight(graph_stats, current_weight)
        edge["norm_weight"] = norm_weight

    return normalised_graph


# TODO: why is optional working some times and sometimes not? why do I sometimes have to write None gosh 
# TODO: Rename
async def get_citation_data(metadata_file: list, topic_id:  Optional[str] = None, outpath: Optional[str]= None) -> tuple:
    """
    Runs all methods to download meta data for software tools in bio.tools; Downloads tools from specified domain, retrieves citations for PMIDs, 
    and generates co-citation network edges.

    :param outpath: Path to directory where output files should be saved.
    :param topic_id: The ID to which the downloaded tools belong, e.g., "Proteomics" or "DNA" as defined by EDAM ontology. 
    :param included_tools: A list of the pmids for the tools for which citations should be downloaded.

    :return: tuple
        A tuple containing edges (list) and citation data (dict).
    """
    # Get citations for each tool, and generate edges between them.

    edges = []

    for tool in tqdm(metadata_file['tools'], desc="Downloading citations from PMIDs"): 
        pmid = tool['pmid']
        async with aiohttp.ClientSession() as session: 
            citations = await pubmetric.data.europepmc_request(session, pmid) 
            for citation in citations:
                edges.append((citation, pmid)) # citations pointing to tools
            tool['nrCitations'] = len(citations) # adding the number of citations as an attribute in the metadatafile

    return edges

def create_cocitation_graph(graph: igraph.Graph, vertices, inverted_weights: bool = False) -> igraph.Graph:
    """
    Generates a co-citation network graph from a given bipartite (though edges between given vertices can occur and are handeled) 
    graph and a list of vertices/nodes that will make up the CITED vertices. All other vertices are considered CITATIONS. 
    The intersection between first neighbours of a pair of CITED vertices (that is, the number of shared CITATIONS) are turned into 
    the edge weight of the edge between the pair. 
    Only pairs with a non-zero intersection have an edge between them in the co.citation graph.

    :param graph: igraph.Graph
        The original graph containing citation relationships.
    :param vertices: list
        List of vertices (nodes) in the graph for which co-citation relationships are to be analysed.
    :param inverted_weights: bool
        If True, invert weights to reflect distance instead of similarity.

    :return: igraph.Graph
        A co-citation network graph (CO_G) with edges representing co-citation relationships.
    """
    
    edges = [] # list of edges in new graph
    for i in range(len(vertices)):
        for j in range(i+1, len(vertices)):
            neighbors_of_first = set(graph.neighbors(vertices[i]))
            neighbors_of_second = set(graph.neighbors(vertices[j]))
            
            common_neighbors = neighbors_of_first.intersection(neighbors_of_second)
            weight = len(common_neighbors)


            # igraph crerates its own id, so getting back their og name to check if one of them cites the other. TODO: should these even be included? 
            original_neighbors_of_first = [graph.vs[id]['name'] for id in neighbors_of_first]
            original_neighbors_of_second = [graph.vs[id]['name'] for id in neighbors_of_second]

            if vertices[i] in original_neighbors_of_second or vertices[j] in original_neighbors_of_first: 
                weight += 1

            if weight> 0:
                if inverted_weights:
                    edges.append((vertices[i], vertices[j], (1 / weight) *100)) # append new edge and the weight, inverted to reflect closeness
                else:
                    edges.append((vertices[i], vertices[j], weight)) # append new edge and the weight, inverted to reflect closeness
    
    cocitation_graph = igraph.Graph.TupleList(edges, directed=False, weights=True)

    return cocitation_graph

def create_graph(edges: list, included_tools: list, cocitation: bool = True, workflow_length_threshold: int = 20) -> igraph.Graph:
    """
    Creates a bibliographic graph from a list of edges and ensures there are no self loops or multiples of edges.
    Removes disconnected nodes

    :param edges: List of edges (tuples) representing connections between nodes in the graph.
    :param tool_dictionary: Dictionary containing metadata about tools, including PMIDs.
    :param cocitation: Flag indicating whether to make the graph a cocitation graph or not.
    :param workflow_length_threshold: Integer representing the maximum number of tools cited by a single publication for it to be considered a workflow citation, rather than e.g. a review paper citing numerous tools.

    :return: Tuple containing:
        - graph: igraph.Graph object of the processed graph.
        - included_tools: List of PMIDs for tools included in the final graph.
        - node_degree_dict: Dictionary mapping node names to their respective degrees in the graph.
    """

    unq_edges = list(set(edges))     
    log_with_timestamp(f"{len(unq_edges)} unique out of {len(edges)} edges total.")
    # Creating a directed graph with unique edges
    raw_graph = igraph.Graph.TupleList(unq_edges, directed=True)
    number_edges_raw = len(raw_graph.es)

    # Removing self citations (loops) and multiples of edges
    graph = raw_graph.simplify(multiple=True, loops=True, combine_edges=None)
    number_edges_simple = len(graph.es)
    log_with_timestamp(f"Removed {number_edges_raw - number_edges_simple} self loops and multiples of edges.")

    # Removing disconnected vertices (that are not tools)
    vertices_to_remove = [v.index for v in graph.vs if v.degree() <= 1 and v['name'] not in included_tools] # tag name
    nr_removed_vertices = len(vertices_to_remove)
    graph.delete_vertices(vertices_to_remove)

    # Removing disconnected tools 
    vertices_to_remove = [v.index for v in graph.vs if v.degree() == 0]
    nr_removed_vertices += len(vertices_to_remove)
    graph.delete_vertices(vertices_to_remove)
    log_with_timestamp(f"Removed {nr_removed_vertices} disconnected tools and citations (with degree less or equal to 1) in the 'bipartite' graph.")

    # Thresholding graph and removing non-tool nodes with node degrees greater than 20
    vertices_to_remove = [v for v in graph.vs if v.degree() > workflow_length_threshold and v['name'] not in included_tools]
    graph.delete_vertices(vertices_to_remove)
    log_with_timestamp(f'Number citation of vertices removed with degree threshold {workflow_length_threshold}: {len(vertices_to_remove)}')

    # Updating included_tools to only contain lists that are in the graph  
    included_tools = [tool for tool in included_tools if tool in graph.vs['name']] # tag name


    # Convert graph to co-citation graph
    if cocitation:
        graph = create_cocitation_graph(graph, included_tools)
        log_with_timestamp(f"Number of remaining tools/vertices is {len(graph.vs)}, and number of remaining edges are {len(graph.es)}")
        return graph
    else: 
        log_with_timestamp(f"Number of remaining tools vertices is {len(included_tools)}, total number of vertices is {len(graph.vs)}")
        return graph # TODO: Included tools can be recreated outside using the metadatafile, check that this is not a problem

# WHY is optional not working here, not specifying default none is the entire reason for having is aaghh 
async def create_citation_network(outpath: Optional[str] = None, test_size: Optional[int] = None, topic_id: Optional[str] = "topic_0121", random_seed: int = 42, load_graph: bool = False, inpath: str = '', save_files: bool = True, doi_lib_directory:str = '') -> igraph.Graph:
    """
    Creates a citation network given a topic and returns a graph and the tools included in the graph.


    :param topic_id: str
        The ID to which the downloaded tools belong, e.g., "Proteomics" or "DNA" as defined by EDAM ontology. 
    :param test_size: int
        Determines the number of tools downloaded.
    :param random_seed: int, Specifies the seed used to randomly pick tools in a test run. Default is 42.
    :param load_graph: bool
        Determines if an already generated graph is loaded or if it is recreated. Needs the parameter inpath to be specified.  
    :param filepath: str
        Path to an already generated graph file.
    :param outpath: str
        Path to the output directory where newly generated graph files will be saved. If not provided,
        a timestamped directory will be created in the current working directory. TODO: make them all end up in a collective out dir
    :param inpath: str
        Path to an existing folder containing the metadata file and graph. Will be used to load them if possible.
    :param save_files: bool
        Determines if the newly generated graph is saved.

    :return: igraph.Graph
        The citation network graph created using igraph.


    """
    
    if load_graph: 
        if not inpath: 
            log_with_timestamp('You need to provide a path to the graph you want to load')
            return  
            
        graph_path = f'{inpath}/graph.pkl'
        if os.path.isfile(graph_path): 
            with open(graph_path, 'rb') as f:
                graph = pickle.load(f) 
            log_with_timestamp(f"Graph loaded from {inpath}")
        else:
            log_with_timestamp(f"File not found. Please check that '{graph_path}' is the path to your graph and run again. Or set load_graph = False to create a new graph. ")
            return 
   
    else:
         # Create output folder
        if outpath: 
            os.mkdir(outpath) 
        else:
            if not os.path.isdir('outs'):
                os.mkdir('outs')
            outpath = f'outs/out_{datetime.now().strftime("%Y%m%d%H%M%S")}'
            os.mkdir(outpath)


        metadata_file = await pubmetric.data.get_tool_metadata(outpath=outpath, inpath=inpath, topic_id=topic_id, test_size=test_size, random_seed=random_seed, doi_lib_directory=doi_lib_directory)
        
        # Extract tool pmids which we use to greate the graph
        included_tools = list({tool['pmid'] for tool in metadata_file['tools']})

        # Downloading data
        edges = await get_citation_data(outpath=outpath, topic_id=topic_id, metadata_file=metadata_file) # this updates the metadata file with nr citations per tool


        # Saving the metadata file Make this optional 
        if test_size:
            metadata_file_name = f'tool_metadata_test{test_size}.json' # I removed date from the filename, it is inside if needed
        else: 
            metadata_file_name = 'tool_metadata.json' 

        print(os.path.join(outpath, metadata_file_name))   
        print(metadata_file['tools'][0]) 
        with open(os.path.join(outpath, metadata_file_name), 'w') as f: # save in the main output folder
                json.dump(metadata_file, f)


        # Creating the graph using igraph
        log_with_timestamp("Creating citation graph using igraph.")

        graph = create_graph(edges=edges, included_tools=included_tools) # tag graph creation

        log_with_timestamp('Adding graph attributes.') # This breaks if it is a non cocitation graph 
        graph = add_graph_attributes(graph=graph, metadata_file=metadata_file)


        # Saving edges, graph and tools included in the graph 
        if save_files:
            log_with_timestamp(f"Saving graph to directory {outpath}.")  # TODO outs should be collected in singel out folder

            graph_path = os.path.join(outpath, 'graph.pkl') 

            with open(graph_path, 'wb') as f: #
                pickle.dump(graph, f)

        # returns a graph and the pmids of the tools included in the graph (tools connected by cocitations)
        log_with_timestamp("Graph creation complete.") # TODO: timestapms for all updates?
        
    return graph

