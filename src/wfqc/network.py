"""
Bibliographic graph creation
"""
import os
from tqdm import tqdm       
import pickle
from datetime import datetime
import json
import aiohttp
import asyncio              
import nest_asyncio         # For jupyter asyncio compatibility 
nest_asyncio.apply()        # Automatically takes into account how jupyter handles running event loops
import igraph 
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), 'src')))
import wfqc.data 

# TODO: import jsonpath_ng.ext      # More efficient json processing look into if actually computationally more efficient 




# TODO: question: testSize is threaded through so many different functions, is this normal? 
# TODO: now the default for topicID is at the bottom of the fucntions calling it, I think it should be at the top. 
async def download_data(outpath: str, testSize: int, topicID: str, filepath: str = None) -> tuple:
    """
    Runs all methods to download meta data for software tools in bio.tools; Downloads tools from specified domain, retrieves citations for PMIDs, 
    and generates co-citation network edges.

    :param outpath: str
        Path to directory where output files should be saved.
    :param testSize: int
        Determines the number of tools downloaded.
    :param topicID: str
        The ID to which the downloaded tools belong, e.g., "Proteomics" or "DNA" as defined by EDAM ontology. 
    :param filepath: str, optional
        Filepath to an existing metadata JSON file.

    :return: tuple
        A tuple containing edges (list) and citation data (dict).
    """
    # Randomly picks out a subset of the pmids
    if testSize != '': 
        print(f"Creating test-cocitation network of size {testSize}.")

    # Retrieve the data 
    tool_metadata = wfqc.data.get_tool_metadata(outpath=outpath, topicID=topicID, testSize= testSize, filename=filepath) #TODO: gettollmetadata needs testsize
 
    edges = []
    citation_json ={
        "tools" : []
    }

    # Get citations for each tool, and generate edges between them. Should it be separate function?
    for tool in tqdm(tool_metadata['tools'], desc="Downloading citations from PMIDs"): 
        pmid = str(tool['pmid']) # EuropePMC requires str TODO: make sure pmids are immideately made into strings           

        async with aiohttp.ClientSession() as session: 
            citations = await wfqc.data.europepmc_request(session, pmid) 
            for citation in citations:
                edges.append((citation, pmid)) # citations pointing to tools

            # TODO: check why this is not generated correctly
            citation_json['tools'].append({ # should I be recreating basically the same file, or should I jsut add the citation data to the og one?
                'pmid': pmid,
                'name': tool['name'],
                'pubDate': tool['pubDate'],
                'nrCitations': len(citations),
                'citations': citations
            })

    filepath = outpath + '/' + f"citations{topicID}.json" # renamed from "edges{topicID}.json", any problems? 
    
    with open(filepath, 'w') as f:
        json.dump(citation_json, f)
    
    return edges, citation_json





def cocitation_graph(graph: igraph.Graph, vertices, inverted_weights: bool =False) -> igraph.Graph:
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


#TODO: only use one of nodes or vertices, not both, to be clear. 
#TODO: tag: inlcuded_tools are here too
# should I be sending the entire tool dictionary or just the included tools. No. TODO: only send included tools - several methods use this, find optimal placement
def create_graph(edges: list, tool_dictionary: dict, cocitation: bool = True) -> igraph.Graph:
    """
    Creates a bibliographic graph from a list of edges and ensures there are no self loops or multiples of edges.
    Removes disconnected nodes

    :param edges: List of edges (tuples) representing connections between nodes in the graph.
    :param tool_dictionary: Dictionary containing metadata about tools, including PMIDs.
    :param cocitation: Flag indicating whether to make the graph a cocitation graph or not.

    :return: Tuple containing:
        - graph: igraph.Graph object of the processed graph.
        - included_tools: List of PMIDs for tools included in the final graph.
        - node_degree_dict: Dictionary mapping node names to their respective degrees in the graph.
    """
    
    # Finding unique edges by converting list to a set (because tuples are hashable) and back to list.
    unq_edges = list(set(edges)) 

    included_tools = [tool['pmid'] for tool in tool_dictionary['tools']] 
    
    print(f"{len(unq_edges)} unique out of {len(edges)} edges total!")

    # Creating a directed graph with unique edges
    raw_graph = igraph.Graph.TupleList(unq_edges, directed=True)


    # Removing self citations
    graph = raw_graph.simplify(multiple=True, loops=True, combine_edges=None)

    # Removing disconnected vertices (that are not tools) that do not have information value for the (current) metric
    print("Removing citations with degree less or equal to 1 (Non co-citations).")
    vertices_to_remove = [v.index for v in graph.vs if v.degree() <= 1 and v['name'] not in included_tools]
    graph.delete_vertices(vertices_to_remove)
    vertices_to_remove = [v.index for v in graph.vs if v.degree() == 0]
    graph.delete_vertices(vertices_to_remove)

    # Stats about node degrees: TODO: this does NOT have to be done here. Move outside of this function!
    node_degrees = graph.degree(graph.vs)
    node_names = [v['name'] for v in graph.vs]
    node_degree_dict = dict(zip(node_names, node_degrees))

    # Thresholding graph and removing non-tool nodes with node degrees greater than 20
    threshold = 20
    vertices_to_remove = [v for v in graph.vs if v.degree() > threshold and v['name'] not in included_tools]
    graph.delete_vertices(vertices_to_remove)

    print(f'Number of vertices removed with degree threshold {threshold}: {len(vertices_to_remove)}')

#not necessary since included tools nto used any longer?
    # Updating included_tools to only contain lists that are in the graph  
    included_tools = [tool for tool in included_tools if tool in graph.vs['name']] 

    # Convert graph to co-citation graph
    if cocitation:
        graph = cocitation_graph(graph, included_tools)


    return graph, included_tools, node_degree_dict
#TODO: fix nr output, can probably be minimised 


# TODO: topic int? filepath? rearrange order of param after importance. Loaddata should be false default. 
def create_citation_network(topicID: str = "topic_0121", testSize: str = '', randomSeed: int = 42, loadData: bool = True, filepath: str = None, outpath: str = None, inpath: str = '', save_files: bool = True) -> igraph.Graph:
    """
    Creates a citation network given a topic and returns a graph and the tools included in the graph.

    :param testSize: int
        Determines the number of tools downloaded.
    :param topicID: str
        The ID to which the downloaded tools belong, e.g., "Proteomics" or "DNA" as defined by EDAM ontology. 
    :param randomSeed: int, Specifies the seed used to randomly pick tools in a test run. Default is 42.
    :param loadData: bool
        Determines if an already generated graph is loaded or if it is recreated. 
    :param filepath: str
        Path to an already generated graph file.
    :param outpath: str
        Path to the output directory where newly generated graph files will be saved. If not provided,
        a timestamped directory will be created in the current working directory. TODO: make them all end up in a collective out dir
    :param inpath: str
        Path to the input directory where existing graph files are located.
    :param save_files: bool
        Determines if the newly generated graph is saved.

    :return: igraph.Graph
        The citation network graph created using igraph.


    """


    
    # Edge creation 
    # Load previously created data or recreate it

    if loadData: # TODO: pickle maybe is not the way to go in future, use json instead? 
        graph_path = f'{inpath}/graph{testSize}.pkl'        
        if os.path.isfile(graph_path): # should give option to specify these names
            print("Loading saved data.")
            with open(graph_path, 'rb') as f:
                graph = pickle.load(f) 

        else:
            print(f"File not found. Please check that '{graph_path}' is in your current directory and run again. Or set loadData = False to create a new graph. ")
            return 
   
    else:
         # Create output folder
        if outpath: 
            os.mkdir(outpath) 
        else:
            outpath =  f'out_{datetime.now().strftime("%Y%m%d%H%M")}'
            os.mkdir(outpath)

        # Downloading data
        edges, tool_dictionary = asyncio.run(download_data(outpath,testSize, topicID, filepath = filepath))

        # Creating the graph using igraph
        print("Creating citation graph using igraph.")

        graph, included_tools, node_degree_dict =  create_graph(edges, tool_dictionary)

      
        # Saving edges, graph and tools included in the graph 
        if save_files:
            graph_path = f'{outpath}/graph{testSize}.pkl'
            node_degree_dict_path = f'{outpath}/node_degree_dict{testSize}.pkl'

            print(f"Saving data to directory {outpath}.") 
            # and save them 
            #Do this nicer later? TODO: perhaps save them all in a json instead

            with open(graph_path, 'wb') as f:
                pickle.dump(graph, f)

            with open(node_degree_dict_path, 'wb') as f:
                pickle.dump(node_degree_dict, f)


    # returns a graph and the pmids of the tools included in the graph (tools connected by cocitations)
    return graph

