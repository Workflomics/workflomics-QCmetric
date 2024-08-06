from cwl_utils.parser import load_document_by_uri 
       
import numpy as np
import json
import igraph 
from typing import Optional, Union


def parse_cwl_workflows(graph: igraph.Graph, cwl_filename: str) -> list:
    """
    Function that turns a CWL representation of a workflow into a list of node tuples (edges), where source and target is represented by the pmid of their repecitve primary publication. 

    :param cwl_filename: String representing the path to the CWL file
    :param metadata_filename: String representing the path to the bio.tools meta data file. Should adhere to the meta data file schema as defined in the pubmetric documentation TODO:add link. 

    :return: List of tuples representing the edges in the workflow.

    """

    #TODO: change to use graph instead of metadatafile
    cwl_obj = load_document_by_uri(cwl_filename)

    edges = []
    workflow_steps = {}
    # Extracting edges from the CWL
    for step in cwl_obj.steps:
        step_id = step.id.split("#")[-1]

        # Collecting all step names, and their corresponding pmids
        tool_name = step_id.split('_')[0]
        workflow_steps[step_id] = next((tool['pmid'] for tool in graph.vs if tool['name'] == tool_name), None)

        for input_param in step.in_:
            if input_param.source:
                source_step_id = input_param.source.split("#")[-1].split('/')[0]

                if "input_" not in source_step_id: # skips the edges between input and tools

                    edges.append((source_step_id, step_id))

    # Saving the edges in pmid format. 
    # OBS that this does not maintain the structure of the workflow if a tool is used more than once since both inctances link to the same pmid
    pmid_edges = []
    for edge in edges:
        source_pmid = next((tool['pmid'] for tool in graph.vs if tool['name'] == edge[0].split('_')[0]), None)
        target_pmid = next((tool['pmid'] for tool in graph.vs if tool['name'] == edge[1].split('_')[0]), None)

        pmid_edges.append((str(source_pmid), str(target_pmid)))

    workflow = {"edges": edges,
                "steps": workflow_steps, # steps and correspoding pmids
                "pmid_edges": pmid_edges # Dont know if this si necessary, but it is extracted often
    }
    return workflow






### The following are just for APE parsing, should not be icluded in the final package? they are just string parsing so very ustable probably

def parse_tuple_workflow(graph: igraph.Graph, pmid_edges: list):
    """"
    Takes a list of tuples of pmids and turns it into the format produced by the parse_cwl_workflows function. 
    Note that this representation does not take into account if a workflow has tool repetitions. 

    :param pmid_workflow: List of tuples of pmids 

    :return: Dictionary of tuples representing the edges in the workflow.

    """
    steps = {}
    edges = []

    for edge in pmid_edges:
        source_pmid = edge[0]
        target_pmid = edge[1]

        source = next((vs['name'] for vs in graph.vs if vs['pmid'] == source_pmid), None) # Transfering id to new tool 
        target = next((vs['name'] for vs in graph.vs if vs['pmid'] == target_pmid), None)

        edges.append( (source, target ) )

        steps[source] = source_pmid # there is some repetition here but 
        steps[target] = target_pmid

    workflow = {
        'edges': edges,
        'steps': steps,
        'pmid_edges': pmid_edges
    }

    return workflow   

def parse_undocumented_workflows(graph: igraph.Graph, cwl_filename: str) -> list: #TODO: OBS! this has the old pmid list structure. Change! 
    """
    Pipeline for processing CWL files by reading them line by line. 
    Requires certain naming conventions for input/output/tools (e.g. XTandem_out_1 ).. 
    
    :param graph: Cocitation graph
    :param cwl_filename: The path to the CWL file

    :return: Dictionary representing a workflow, where the sources and targets are PmIDs.

    """
    with open(cwl_filename, "r") as f:
        cwl_string = f.read()  

    steps_string = cwl_string.split("steps:\n")[1].split("outputs")[0]
    steps = steps_string.split('\n')
    steps = [row.strip(' ') for row in steps if not row.startswith('    ')]
    steps = [step for step in steps if step]


    edges = []
    step_dict = {}

    for i in range(len(steps)):
        if i == len(steps) -1: # for the last one, split with outputs
            step_string = cwl_string.split(steps[i])[1].split("outputs:")[0]
        else:
            step_string = cwl_string.split( steps[i] )[1].split( steps[i+1] )[0] # split between the two steps

        step_input = step_string.split('in:')[1].split('out:')[0].split('\n') # each row between input and output
        step_input = [inp.split(':')[1].split('/')[0] for inp in step_input if '/' in inp]

        step_edges = [ (inp.strip(), steps[i].strip(':')) for inp in step_input ]
        
        edges += step_edges 


    pmid_edges = []
    for edge in edges:
        source_pmid = next((tool['pmid'] for tool in graph.vs if tool['name'] == edge[0].split('_')[0]), None)
        target_pmid = next((tool['pmid'] for tool in graph.vs if tool['name'] == edge[1].split('_')[0]), None)

        pmid_edges.append((str(source_pmid), str(target_pmid)))

        step_dict[edge[0]] = source_pmid 
        step_dict[edge[1]] = target_pmid 

    workflow = {"edges": edges,
                "steps": step_dict, # steps and correspoding pmids
                "pmid_edges": pmid_edges # Dont know if this si necessary, but it is extracted often
    }
    return workflow 


def load_undoc_tool(cwl_filename: str) -> list:
    """
    String parsing chaos alternative to parse_workflows. Can parse any APE generated CWL_file. Relies on input and output naming conventions.

    :param cwl_filename: String representing the path to the CWL file

    :return: List of tuples ro unprocessed tool names.
    """
    with open(cwl_filename, "r") as f:
        cwl_string = f.read()

    steps_string = cwl_string.split("steps:\n")[1].split("outputs")[0]
    steps = steps_string.split('\n')
    steps  = [row for row in steps if not row.startswith('    ')]
    edge_list = []

    for i in range(len(steps)):
        if i+1 > len(steps)-1:
            continue
        
        if steps[i+1] != "":
            step_string = cwl_string.split(steps[i])[1].split(steps[i+1])[0]
        else:
            step_string = cwl_string.split(steps[i])[1].split("outputs:")[0]
        step_in_out = step_string.split("in:\n")[1].split("out:")

        step_in = step_in_out[0].split('\n')
        step_in = [s.split(':')[1].strip() for s in step_in if ':' in s]

        step_out = step_in_out[1].replace('[', '').replace(']', '').replace('\n', '').split(',')
        step_out = [s.strip() for s in step_out]
        
        for si in step_in:
            if "/" in si:
                si = si.split('/')[1]
            edge = (si, steps[i].split('_')[0])
            edge_list.append(edge)
        for so in step_out:
            
            edge = (steps[i].split('_')[0], so)
            edge_list.append(edge)


    return edge_list




