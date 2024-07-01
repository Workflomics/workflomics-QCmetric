"""
Graph creation
"""
import os
from tqdm import tqdm       
import pickle
import numpy as np
from datetime import datetime

import json
import aiohttp
import asyncio              # -"-
import nest_asyncio         # For jupyter asyncio compatibility 
nest_asyncio.apply()        # Automatically takes into account how jupyter handles running event loops


# TODO: import jsonpath_ng.ext      # More efficient json processing look into if actually computationally more efficient 
import igraph               # Used to create te citationa graph 

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), 'src')))

import wfqc.data 



async def download_data(outpath, testSize, randomSeed, topicID):
    # Retrieve the data 
    tool_metadata = wfqc.data.get_tool_metadata(outpath=outpath, topicID=topicID)
    pmids = [tool['pmid'] for tool in tool_metadata['tools']] # its a json now

    # Randomly picks out a subset of the pmids
    if testSize != '': 
        print(f"Creating test-cocitation network of size {testSize}. Random seed is {randomSeed}.")
        np.random.seed(randomSeed)
        pmids = np.random.choice(pmids, testSize)

    included_tools = []  
    edges = []
    citation_json ={
        "tools" : []
    }

    # Get citations for each tool, and generate edges between them. 
    for pmid in tqdm(pmids, desc="Processing PMIDs"): 
        pmid = str(pmid) # EuropePMC requires str            

        async with aiohttp.ClientSession() as session: 
            citations = await wfqc.data.europepmc_request(session, pmid) # CHECK!!
            for citation in citations:
               
                edges.append((citation, pmid)) # citations pointing to tools
                if pmid not in included_tools:
                    included_tools.append(pmid) 

            citation_json['tools'].append({ 
                'pmid': pmid,
                'nrCitations': len(citations),
                'citations': citations
            })

    filepath = outpath + '/' + f"edges{topicID}.json"
    
    with open(filepath, 'w') as f:
        json.dump(citation_json, f) # can I do that to make it a dict? # should I make it a json file with more info- like nr citaitons etc? 
    
    return edges, included_tools





def cocitation_graph(G, vertices, inverted_weights = False): # generate cocitation graph: TODO change function names 
    
    edges = [] # lsit of edges in new graph
    for i in range(len(vertices)):
        for j in range(i+1, len(vertices)):
            neighbors_of_first = set(G.neighbors(vertices[i]))
            neighbors_of_second = set(G.neighbors(vertices[j]))
            
            common_neighbors = neighbors_of_first.intersection(neighbors_of_second)
            weight = len(common_neighbors)


            # igraph crerates its own id, so getting back their og name to check if one of them cites the other. TODO: should these be included? 
            original_neighbors_of_first = [G.vs[id]['name'] for id in neighbors_of_first]
            original_neighbors_of_second = [G.vs[id]['name'] for id in neighbors_of_second]

            if vertices[i] in original_neighbors_of_second or vertices[j] in original_neighbors_of_first: # do we want these?
                weight += 1

            if weight> 0:
                if inverted_weights:
                    edges.append((vertices[i], vertices[j], (1 / weight) *100)) # append new edge and the weight, inverted to reflect closeness
                else:
                    edges.append((vertices[i], vertices[j], weight)) # append new edge and the weight, inverted to reflect closeness
    
    CO_G = igraph.Graph.TupleList(edges, directed=False, weights=True)

    return CO_G




def create_graph(edges, included_tools, includeCitationNodes = False):
    # Finding unique edges by converting list to a set (because tuples are hashable) and back to list.
    unq_edges = list(set(edges)) 
    
    print(f"{len(unq_edges)} unique out of {len(edges)} edges total!")

    # Creating a directed graph with unique edges
    G_raw = igraph.Graph.TupleList(unq_edges, directed=True)


    # Removing self citations
    G = G_raw.simplify(multiple=True, loops=True, combine_edges=None)

    # Removing disconnected vertices (that are not tools) that do not have information value for the (current) metric
    print("Removing citations with degree less or equal to 1 (Non co-citations).")
    vertices_to_remove = [v.index for v in G.vs if v.degree() <= 1 and v['name'] not in included_tools]
    G.delete_vertices(vertices_to_remove)
    vertices_to_remove = [v.index for v in G.vs if v.degree() == 0]
    G.delete_vertices(vertices_to_remove)

    # Stats about node degrees:
    node_degrees = G.degree(G.vs)
    node_names = [v['name'] for v in G.vs]
    node_degree_dict = dict(zip(node_names, node_degrees))

    # Thresholding graph and removing non-tool nodes with node degrees greater than 20
    threshold = 20
    vertices_to_remove = [v for v in G.vs if v.degree() > threshold and v['name'] not in included_tools]
    G.delete_vertices(vertices_to_remove)

    print(f'Number of vertices removed with degree threshold {threshold}: {len(vertices_to_remove)}')

#not necessary since included tools nto used any longer?
    # Updating included_tools to only contain lists that are in the graph  
    included_tools = [tool for tool in included_tools if tool in G.vs['name']] 

    # Convert G to co-citation graph
    if not includeCitationNodes:
        G = cocitation_graph(G, included_tools)


    return G, included_tools, node_degree_dict




def create_citation_network(topicID="topic_0121", testSize='', randomSeed=42, loadData=True, filePath='', outpath = None, inpath = '', saveFiles=True): # TODO: I just threw  code into this function- improve
    
    """
    Creates a citation network given a topic and returns a graph and the tools included in the graph

        
    Parameters
    ----------
    topicID : str, default "topic_0121" (proteomics) TODO: int? 
        The ID to which the tools belongs to, ex. "Proteomics" or "DNA" as defined by 
        EDAM ontology (visualisation: https://edamontology.github.io/edam-browser/#topic_0003)

    testSize : int or None, default None
        Determines the number of tools included in the citation graph.

    randomSeed : int, default 42
        Specifies what seed is used to randomly pick tools in a test run. 
    
    loadData : Boolean, default True
        Determines if already generated graph is loaded or if it is recreated.
    
    filePath : str  TODO: add filepath 
        Path to already generated graph

    saveFiles : Boolean, default True
        Determines if newly generated graph is saved. 

    """

    
    # Edge creation 
    # Load previously created data or recreate it

    if loadData: # TODO: pickle maybe is not the way to go in future, use json instead? 
        graph_path = f'{inpath}/graph{testSize}.pkl'        
        if os.path.isfile(graph_path): # should give option to specify these names
            print("Loading saved data.")
            with open(graph_path, 'rb') as f:
                G = pickle.load(f) 

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
        edges, included_tools = asyncio.run(download_data(outpath,testSize,randomSeed, topicID))

        # Creating the graph using igraph
        print("Creating citation graph using igraph.")

        G, included_tools, node_degree_dict =  create_graph(edges, included_tools)

      
        # Saving edges, graph and tools included in the graph 
        if saveFiles:
            graph_path = f'{outpath}/graph{testSize}.pkl'
            node_degree_dict_path = f'{outpath}/node_degree_dict{testSize}.pkl'

            print(f"Saving data to directory {outpath}.") # sould make these filenames dynamic
            # and save them 
            #Do this nicer later? TODO: perhaps save them all in a json instead

            with open(graph_path, 'wb') as f:
                pickle.dump(G, f)

            with open(node_degree_dict_path, 'wb') as f:
                pickle.dump(node_degree_dict, f)


    # returns a graph and the pmids of the tools included in the graph (tools connected by cocitations)
    return G

