from cwl_utils.parser import load_document_by_uri 
       
import numpy as np
import json


def parse_workflows(cwl_filename: str, metadata_filename:str) -> list: 
    """
    Function that turns a CWL representation of a workflow into a list of node tuples (edges), where source and target is represented by the pmid of their repecitve primary publication. 

    :param cwl_filename: String representing the path to the CWL file
    :param metadata_filename: String representing the path to the bio.tools meta data file. Should adhere to the meta data file schema as defined in the pubmetric documentation TODO:add link. 

    :return: List of tuples representing the edges in the workflow.

    """
    cwl_obj = load_document_by_uri(cwl_filename)

    edges = []
    for step in cwl_obj.steps:
        step_id = step.id.split("#")[-1]
        for input_param in step.in_:
            if input_param.source:
                source_step_id = input_param.source.split('/')[-1].split("#")[-1]
                edges.append((source_step_id, step_id))
        for output_param in step.out:
            edges.append((step_id, output_param.split("/")[-1]))

    pairwise_connections = set()
    for source, target in edges:
        if "_out_" in source:
            tool_id = target.split("_")[0]
            for next_target, next_source in edges:
                if next_source == source:
                    pairwise_connections.add(( next_target.split("_")[0], tool_id)) # feels illogical to do it this way but thats how it turns out correct

    with open(metadata_filename, 'r') as f:
        metadata_file =  json.load(f)

    pmid_edges = []
    for edge in pairwise_connections:
        source_pmid = next((tool['pmid'] for tool in metadata_file['tools'] if tool['name'] == edge[0]), None)
        target_pmid = next((tool['pmid'] for tool in metadata_file['tools'] if tool['name'] == edge[1]), None)
        if source_pmid is not None and target_pmid is not None:
            pmid_edges.append((str(source_pmid), str(target_pmid)))


    return pmid_edges

def generate_random_workflow(tool_list: list, workflow:list) -> list: 
    """
    Generates a workflow of the same structure as the given workflow, but where each tool is replaced with a randomly picked one from the given set.

    :param tool_list: List of tools to pick from. Generally this should be all tools in the domain.
    :param workflow: List of tuples (edges) representing the workflow.

    :return: List of tuples representing a workflow where each tool has been replaced by another, random, one.  
    """
    workflow_tools = np.unique([element for tuple in workflow for element in tuple])
    nr_tools = len(workflow_tools)

    random_workflow = []
    random_workflow_tools = np.random.choice(tool_list, nr_tools)

    # Mapping original tools to the new ones and using the mapping to replace them. 
    tool_mapping = dict(zip(workflow_tools, random_workflow_tools))
    random_workflow = [(str(tool_mapping[edge[0]]), str(tool_mapping[edge[1]])) for edge in workflow]
    
    return random_workflow




### The following are just for APE parsing, should not be icluded in the final package? they are just string parsing so very ustable probably


def load_undoc_tool(cwl_filename: str) -> list:
    """
    String parsing chaos alternative to parse_workflows. Can parse any APE generated CWL_file. Relies on input and output naming conventions.

    :param cwl_filename: String representing the path to the CWL file

    :return: List of tuples ro unprocessed tool names.
    """
    with open(cwl_filename, "r") as f:
        cwl_string = f.read()

    steps_string = cwl_string.split("steps:\n")[1].split("outputs")[0]
    steps_list = steps_string.split('\n')
    steps_list  = [row for row in steps_list if not row.startswith('    ')]
    edge_list = []

    for i in range(len(steps_list)):
        if i+1 > len(steps_list)-1:
            continue
        
        if steps_list[i+1] != "":
            step_string = cwl_string.split(steps_list[i])[1].split(steps_list[i+1])[0]
        else:
            step_string = cwl_string.split(steps_list[i])[1].split("outputs:")[0]
        step_in_out = step_string.split("in:\n")[1].split("out:")

        step_in = step_in_out[0].split('\n')
        step_in = [s.split(':')[1].strip() for s in step_in if ':' in s]

        step_out = step_in_out[1].replace('[', '').replace(']', '').replace('\n', '').split(',')
        step_out = [s.strip() for s in step_out]
        
        for si in step_in:
            if "/" in si:
                si = si.split('/')[1]
            edge = (si, steps_list[i].split('_')[0])
            edge_list.append(edge)
        for so in step_out:
            
            edge = (steps_list[i].split('_')[0], so)
            edge_list.append(edge)
    return edge_list

def extract_tool_connections(edges: list) -> set:
    """
    Extracts tool connections from a list of edges, identifying pairwise connections that bypass intermediate steps. 
    OBS: Involves string parsing, possibly not very reliable. 

    :param edges: List of tuples representing edges in a workflow.

    :return: A set of pairwise connections extracted from the original edges.

    """
    pairwise_connections = set()
    for source, target in edges:
        if "_out_" in target:
            for next_source, next_target in edges:
                if next_source == target:
                    pairwise_connections.add((source.lstrip(), next_target.lstrip()))
    return pairwise_connections

def reconnect_edges(missing_node, workflow): 
    """
    Given a workflow and a missing node, this identifies all edges in the original workflow containing that node and reconnects them.

    :param missing_node: The name of the node which does not have a PmID
    :param workflow:  List of tuples (edges) representing a workflow

    :return: New reconnected edges. OBS does not return the full reconnected workflow. See use in generate_pmid_edges()
    """
    reconnected_edges = []

    sources = [edge[0] for edge in workflow if missing_node == edge[1]]
    targets = [edge[1] for edge in workflow if missing_node == edge[0]]

    for source in sources:
        for target in targets:
            reconnected_edges.append((source, target))
    return reconnected_edges

def name_to_pmid(metadata_file: dict, name: str) -> str:
    """ 
    Given the meta data file and a tool name it returns the pmid for that tool
    
    :param metadata_file: THE metadatafile TODO: update with url
    :param name: name of tool for which you want to retrieve the pmid

    :return: String of the pmid, or None if no pmid is found (if the tool is not in the metadatafile)
    
    """ 
    pmid = next((tool['pmid'] for tool in metadata_file['tools'] if tool['name'] == name), None)
    return pmid
    

def generate_pmid_edges(metadata_filename: str, workflow:list, handle_missing:str = 'reconnect') -> list: # what should be the default?
    """
    Takes a workflow of names and generates the pmid version of the workflow, and handles missing PmID values. 

    :param metadata_filename: The file TODO add url.
    :param workflow: List of tuples (edges) representing a workflow, where the sources and targets are tool names. 
    :param handle_missing: Either 'reconnect', 'remove' or 'keep'. Specifying how to handle missing PmID values.

    :return: List of tuples (edges) representing a workflow, where the sources and targets are PmIDs.

    :raises ValueError: If handle missing is not one of 'reconnect', 'remove', 'keep'.
    """

    if handle_missing not in ['reconnect', 'remove', 'keep']:
        raise ValueError("Incorrect option for 'handle_missing' parameter choose one of 'reconnect', 'remove' or 'keep'.")


    with open(metadata_filename, 'r') as f:
        metadata_file = json.load(f)

    new_edges = []
    missing_tools = []
    pmid_name_mapping = {}
    reconnected_edges = []

    for edge in workflow:
        
        if handle_missing == 'reconnect':
            if edge[0] in missing_tools or edge[1] in missing_tools:
                continue
        
        source = edge[0]
        target = edge[1]

        source_pmid = name_to_pmid(metadata_file, source)
        target_pmid = name_to_pmid(metadata_file, target)

        pmid_name_mapping[source] = source_pmid
        pmid_name_mapping[target] = target_pmid

        if handle_missing == 'keep':
            new_edges.append((str(source_pmid), str(target_pmid)))
            continue

        if source_pmid is not None and target_pmid is not None: 
            new_edges.append((str(source_pmid), str(target_pmid)))
        else:
            if not source_pmid:
                missing_tools.append(source)
                if handle_missing == 'reconnect':
                    reconnected_edges.append(reconnect_edges(source, workflow))
            if not target_pmid:
                missing_tools.append(target)
                if handle_missing == 'reconnect': # otherwise they are skipped and effectively removed from the workflow. "remove" key 
                    reconnected_edges.append(reconnect_edges(target, workflow))


    if missing_tools:
        print(np.unique(missing_tools), "do(es) not have a pmid(s) and all edges to or from the node(s) will be excluded or reconnected.")

        pmid_reconnected_edges = [(pmid_name_mapping[name1], pmid_name_mapping[name2]) for sublist in reconnected_edges for  name1, name2 in sublist]
        new_edges = new_edges + pmid_reconnected_edges 

    return new_edges

def parse_undocumented_workflows(cwl_filename: str, metadata_filename:str) -> list:
    """
    Pipeline for processing CWL files by reading them line by line. 
    Requires certain naming conventions for input and output (e.g. XTandem_out_1 ) and for tools to be named according to the bio.tools documentation (e.g. XTandem_01). 

    :param metadata_filename: The file TODO add url.
    :param cwl_filename: The path to the CWL file

    :return: List of tuples (edges) representing a workflow, where the sources and targets are PmIDs.

    """
    edges = load_undoc_tool(cwl_filename)

    tool_edges = extract_tool_connections(edges)

    return generate_pmid_edges(metadata_filename, tool_edges, handle_missing='reconnect')

