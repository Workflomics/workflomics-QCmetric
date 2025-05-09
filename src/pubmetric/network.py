"""
Bibliographic graph creation
"""
import os
import sys
import math
import json
import pickle
from datetime import datetime
from collections import defaultdict
from typing import Optional, Union
import itertools
from multiprocessing import Pool

import igraph
from tqdm import tqdm

sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), 'src'))) #TODO this should not be necessary
import pubmetric.data
import pubmetric.log

def add_graph_attributes(graph: igraph.Graph, metadata_file: dict):
    """
    Adds attributes to the vertices and edges of the graph using metadata.

    :param graph: The co-citation igraph.Graph to be updated.
    :param metadata_file: Dictionary containing metadata with a 'tools' key. # TODO ref the schema  

    :return: The updated co-citaiton igraph.Graph with added vertex and edge attributes.
    """

    for edge in graph.es:
        current_weight = edge["weight"]
        inverted_weight = 1.0 / current_weight if current_weight != 0 else float('inf')
        edge["inverted_weight"] = inverted_weight

    for vertex in graph.vs:
        pmid = vertex["name"]
        tool_metadata = next((tmd for tmd in metadata_file['tools'] if tmd['pmid'] == pmid))

        vertex['pmid'] = pmid
        vertex["name"] = tool_metadata['name']  # changing name to name
        vertex["age"] = datetime.now().year - int(tool_metadata.get('publication_date')
                                                  or 50) # igraph requires that all arguments are of same type so we use 50 as none 
        vertex["nr_citations"] = tool_metadata['nr_citations']
        vertex['degree'] = vertex.degree()  # for compatibility with cytoscape,
                                            # and to retain full graph stats even 
                                            # if a subgraph is extracted
    return graph

def create_small_cocitation_graph(paper_citations: dict) -> igraph.Graph:
    """
    Creates a co-citation graph from a dictionary where keys are citations and values 
    are sets of papers it cites.

    :param paper_citations: Dictionary where keys are citation identifiers (PMIDs) and 
        values are sets of papers (bio.tools tools) (PMIDs). Like a document connected 
        to its terms. 
    :return: An igraph Graph object representing the co-citation network.
    """
    cocitation_counts = defaultdict(int)

    # Iterating over each _citation_ paper and the papers it is citing
    for citations in paper_citations.values():
        # Generating all unique pairs of co-citations for that citation
        for paper1, paper2 in itertools.combinations(citations, 2):
            if paper1 != paper2:  # To avoid self-pairs
                pair = tuple(sorted((paper1, paper2))) # sorted so the order does not matter
                cocitation_counts[pair] += 1 # collect the weight as a counter

    # Co-citation counts are converted to a weighted edge list to create the graph 
    edges = [(pair[0], pair[1], count) for pair, count in cocitation_counts.items()]
    cocitation_graph = igraph.Graph.TupleList(edges, directed=False, weights=True)

    return cocitation_graph

def create_cocitation_graph(paper_citations: dict,
                            num_processes: int = 2,
                            num_chunks: int = 10) -> igraph.Graph:
    """
    Creates a co-citation graph from a dictionary of paper citations by using MapReduce
    logic (splitting the data into chunks and temporarily saving them for parallel and
    sequential processing).

    :param paper_citations: Dictionary where keys are citation identifiers (PMIDs) and
        values are sets of papers cited by the key paper.
    :param num_processes: Number of parallel processes to use for processing each chunk.
        Default is 2.
    :param num_chunks: Number of chunks to divide the data into for sequential processing.
        Default is 10.

    :raises IOError: If there is an issue with reading or writing the chunk files.
    :raises ValueError: If the number of chunks or processes is less than 1.

    :return: An igraph Graph object representing the co-citation network.
    """    
    # Splitting the paper_citations dictionary into smaller chunks for sequential processing
    pubmetric.log.log_with_timestamp(
        f"Processing {len(paper_citations)} citations using {num_chunks} chunks "
        f"with {num_processes} parallel process(es) each."
    )
    chunk_size = math.ceil(len(paper_citations) / num_chunks)
    paper_citations_items = list(paper_citations.items())
    chunks =    [dict(paper_citations_items[i:i + chunk_size])
                for i in range(0, len(paper_citations_items), chunk_size)]

    all_partial_counts = []
    for i, chunk in tqdm(enumerate(chunks), total=num_chunks, desc="Processing chunks"):
        chunk_file = f"chunk_{i}.pkl"
        with Pool(processes=num_processes) as pool:
            partial_counts = pool.map(process_chunk, [chunk])

        # Saving partial counts to disk so memory does not run out
        with open(chunk_file, 'wb') as f:
            pickle.dump(partial_counts, f)
        all_partial_counts.append(chunk_file)

    # Combining all partial counts
    cocitation_counts = defaultdict(int)

    for chunk_file in all_partial_counts:
        with open(chunk_file, 'rb') as f:
            partial_counts = pickle.load(f)
        cocitation_counts = combine_counts([cocitation_counts] + partial_counts)
        os.remove(chunk_file)  # Remving chunk files

    edges = [(pair[0], pair[1], count) for pair, count in cocitation_counts.items()]

    # Create the co-citation graph
    cocitation_graph = igraph.Graph.TupleList(edges, directed=False, weights=True)

    return cocitation_graph

def combine_counts(counts_list: list):
    """
    Combines multiple dictionaries of co-citation counts into a single dictionary 
    by summing the counts for each co-citation pair.

    :param counts_list: List of dictionaries where each dictionary contains
    co-citation pairs as keys and their counts as values.
    
    :return: A defaultdict object where each key is a co-citation pair and the
        value is the total count of that pair across all dictionaries.
    """
    combined_counts = defaultdict(int)
    for counts in counts_list:
        for pair, count in counts.items():
            combined_counts[pair] += count
    return combined_counts

def process_chunk(chunk: dict):
    """
    Processes a chunk of paper citations to count co-citations between papers.

    :param chunk: Dictionary where keys are citation identifiers (PMIDs) and values
        are sets of papers cited by the key paper within this chunk.
    
    :return: A defaultdict object where each key is a co-citation pair (sorted tuple)
        and the value is the count of co-citations for that pair within the chunk.
    """
    cocitation_counts = defaultdict(int)
    for citations in chunk.values():
        for paper1, paper2 in itertools.combinations(citations, 2):
            if paper1 != paper2:
                pair = tuple(sorted((paper1, paper2)))
                cocitation_counts[pair] += 1
    return cocitation_counts

async def create_network(outpath: Optional[str] = None,
                        test_size: Optional[int] = None,
                        topic_id: Optional[str] = "",
                        random_seed: int = 42,
                        load_graph: bool = False,
                        inpath: str = '',
                        save_files: bool = True,
                        tool_selection: Union[list, str, None]=None) -> igraph.Graph:
    """
    Creates a citation network given a topic and returns a graph and the tools 
    included in the graph.

    :param topic_id: The ID to which the downloaded tools belong,
        e.g., "Proteomics" or "DNA" as defined by EDAM ontology.
    :param test_size: Determines the maximum number of tools downloaded.
    :param random_seed: Specifies the seed used to randomly pick tools in a test run.
        Default is 42.
    :param load_graph: Determines if an already generated graph is loaded or if it
        is recreated.
    :param inpath: Path to an existing folder containing the metadata file and graph.
        Will be used to load them if possible.
    :param outpath: Path to the output directory where newly generated graph files
        will be saved. If not provided, a timestamped directory will be created in
        the current working directory.
    :param save_files: Determines if the newly generated graph is saved.

    :raises FileNotFoundError: If no inpath is given despite asking to load.
    :raises FileNotFoundError: If input directory is not found

    :return: The citation network graph created using igraph.
    """

    # Record start time of the function
    start_time = datetime.now()

    if load_graph:

        if not inpath:
            raise FileNotFoundError('In-path required for loading graph.')

        graph_path = os.path.join(inpath, 'graph.pkl')
        if os.path.isfile(graph_path):
            pubmetric.log.log_with_timestamp(f"Loading graph from {graph_path}.")
            with open(graph_path, 'rb') as f:
                graph = pickle.load(f)
            pubmetric.log.log_with_timestamp(f"Graph loaded from {graph_path}.")
        else:
            raise FileNotFoundError(f"File not found: {graph_path}.")

    else:
        # Create output directory
        if not outpath:
            outpath = f'out/out_{datetime.now().strftime("%Y%m%d%H%M%S")}'

        os.makedirs(outpath, exist_ok=True)
        pubmetric.log.log_with_timestamp(f"Output directory created at {outpath}.")
        pubmetric.log.log_with_timestamp("Downloading tool metadata from bio.tools")
        metadata_start_time = datetime.now()
        metadata_file = await pubmetric.data.get_tool_metadata(outpath=outpath, 
                                                               inpath=inpath, 
                                                               topic_id=topic_id, 
                                                               test_size=test_size, 
                                                               random_seed=random_seed)
        if tool_selection:
            if tool_selection == "full":
                selected_tools = pubmetric.data.download_domain_annotations(
                                                                annotations="full", 
                                                                tools=metadata_file["tools"])
                if not selected_tools:
                    raise ValueError("No tools were downloaded; please check the download source.")
            elif tool_selection == "workflomics":
                selected_tools = pubmetric.data.download_domain_annotations(
                                                                annotations="workflomics",
                                                                tools=metadata_file["tools"])
                if not selected_tools:
                    raise ValueError("No tools were downloaded; please check the download source.")
            elif isinstance(tool_selection, (list, set)):
                tool_selection_set = set(tool_selection)
                selected_tools = [tool
                                  for tool in metadata_file['tools']
                                  if tool['name'] in tool_selection_set]
                if not selected_tools:
                    raise ValueError(
                        "No matching tools found; check the tool names in tool_selection.")
            else:
                raise TypeError(
                    "Invalid type for tool_selection. Expected str, list, or set.")

            pubmetric.log.log_with_timestamp("Selecting specified subsection of tools")
            pubmetric.log.log_with_timestamp(f"Number of selected tools: {len(selected_tools)}")
            metadata_file['tools'] = selected_tools
            tool_selection = True

        metadata_file_name = (
            f'tool_metadata_test{test_size}.json'
            if test_size
            else 'tool_metadata.json'
        )
        metadata_file_path = os.path.join(outpath, metadata_file_name)
        pubmetric.log.log_with_timestamp(f"Saving metadata file to {metadata_file_path}.")
        with open(metadata_file_path, 'w', encoding='utf-8') as f:
            json.dump(metadata_file, f)
        pubmetric.log.step_timer(metadata_start_time, "Fetching and saving metadata")

        # Download paper citations
        pubmetric.log.log_with_timestamp("Downloading citations.")
        citation_start_time = datetime.now()
        paper_citations = await pubmetric.data.process_citation_data(metadata_file=metadata_file, 
                                                                     inpath=inpath, outpath=outpath)
        pubmetric.log.step_timer(citation_start_time, "Downloading citations")
        # Create co-citation graph
        pubmetric.log.log_with_timestamp("Creating co-citation graph.")
        graph_creation_start_time = datetime.now()

        if len(paper_citations)>20_000:
            graph = create_cocitation_graph(paper_citations)
        else:
            graph = create_small_cocitation_graph(paper_citations)

        pubmetric.log.step_timer(graph_creation_start_time, "Creating co-citation graph")

        # Add graph attributes
        pubmetric.log.log_with_timestamp("Adding graph attributes.")
        attribute_start_time = datetime.now()
        graph = add_graph_attributes(graph=graph, metadata_file=metadata_file)

        pubmetric.log.step_timer(attribute_start_time, "Adding graph attributes")

        # Save graph
        if save_files:
            pubmetric.log.log_with_timestamp("Saving graph.")
            graph_path = os.path.join(outpath, 'graph.pkl')
            with open(graph_path, 'wb') as f:
                pickle.dump(graph, f)
        pubmetric.log.log_with_timestamp(f"Graph creation complete. Graph contains"
                                         f"{len(graph.vs)} vertices and {len(graph.es)} edges.")

    pubmetric.log.step_timer(start_time, "Complete data download and graph creation")

    # Graph level attributes
    graph["creation_date"] = datetime.now()
    graph["topic"] = topic_id
    graph["tool_selection"] = tool_selection
    graph["graph_creation_time"] = datetime.now() - start_time # TODO not func? 

    return graph
