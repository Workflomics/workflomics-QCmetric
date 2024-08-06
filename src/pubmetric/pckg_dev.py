

import pandas as pd
import numpy as np
import json 
import random
import copy
import ast
from sklearn.model_selection import train_test_split
import sys
import os
import aiohttp
from tqdm import tqdm       
import igraph
from typing import Optional


sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), 'src')))
import pubmetric.data 


def parse_tuple_workflow(graph: igraph.Graph, pmid_edges: list): # for reading rated dataset
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

        source = next(vs['name'] for vs in graph.vs if vs['pmid']== source_pmid) # transfering numbering to random steps
        target = next(vs['name'] for vs in graph.vs if vs['pmid']== target_pmid)

        edges.append( (source, target ) )

        steps[source] = source_pmid # there is some repetition here but 
        steps[target] = target_pmid

    random_workflow = {
        'edges': edges,
        'steps': steps,
        'pmid_edges': pmid_edges
    }

    return random_workflow   



## tag : next step 
def generate_random_workflow(graph: igraph.Graph, workflow: dict, tool_list: Optional[list] = None, random_seed: int = 42, retain_degree: bool = True) -> list:  # TODO: must be updated to work with the new workflow format
    """
    Generates a workflow of the same structure as the given workflow, but where each tool is replaced with a randomly picked one from the given set.

    :param tool_list: List of tools to pick from. Generally this should be all tools in the domain.
    :param workflow: Dictionary representing the workflow.

    :return: List of tuples representing a workflow where each tool has been replaced by another, random, one.  
    """

    np.random.seed(random_seed)

    steps = workflow['steps']
    edges = workflow['edges']

    # I want it to have the same structure and the same degree. 

    random_steps = {}
    random_edges = []
    random_pmid_edges = []


    pmid_mapping = {}
    for step in list(steps.items()):
        pmid = step[1]
        if pmid in pmid_mapping.keys():
            continue
        if retain_degree:
            degree = next(vs.degree() for vs in graph.vs if vs['pmid']==pmid) # TODO: replace the old list comprehension with next
            # Binning degrees (1-50 is 50, 51-100 is 100 etc), so the random tools are a bit more fairly chosen
            binned_degree = ((degree + 49) // 50) * 50
            tool_list = [vs['pmid'] for vs in graph.vs if  (binned_degree - 50) < vs.degree() <= (binned_degree + 50)]
            print('nr tools to choose from at degree', degree, len(tool_list))

        
        random_pmid = np.random.choice(tool_list)
        pmid_mapping[pmid] = random_pmid

    for edge in edges:
        source = edge[0]
        target = edge[1]

        random_source_pmid = pmid_mapping[steps[source]]
        random_target_pmid = pmid_mapping[steps[target]]
        
        random_source = next(vs['name'] for vs in graph.vs if vs['pmid']== random_source_pmid) + f'_{source.split("_")[1]}' # transfering numbering to random steps
        random_target = next(vs['name'] for vs in graph.vs if vs['pmid']== random_target_pmid) + f'_{target.split("_")[1]}'

        random_edges.append( (random_source, random_target ) )
        random_pmid_edges.append( (random_source_pmid, random_target_pmid) )

        random_steps[random_source] = random_source_pmid # there is some repetition here but 
        random_steps[random_target] = random_target_pmid


    random_workflow = {
        'edges': random_edges,
        'steps': random_steps,
        'pmid_edges': random_pmid_edges
    }

    return random_workflow




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
   


def stratified_split(data, test_size=0.2, random_state=42):
    """
    splits the annotated dataset from the APE in the wild paper into 4 different bins based on rating
    """
    rating_bins = [0, 1, 2, 3]

    for d in data:
        if d['ratingAvg'] == 0:
            d['rating_bin'] = '0'
        elif d['ratingAvg'] > 0 and d['ratingAvg'] < 1:
            d['rating_bin'] = '0-1'
        elif d['ratingAvg'] >= 1 and d['ratingAvg'] < 2:
            d['rating_bin'] = '1-2'
        elif d['ratingAvg'] >= 2 and d['ratingAvg'] <= 3:
            d['rating_bin'] = '2-3'

    ratings = np.array([d['ratingAvg'] for d in data])
    rating_bins = np.array([d['rating_bin'] for d in data])

    # Perform stratified split
    train_data, test_data, train_ratings, test_ratings = train_test_split(data, ratings, test_size=test_size, stratify=rating_bins, random_state=random_state)

    json_test = json.dumps(test_data, indent=4)
    with open('test_rated.json', 'w') as json_file:
        json_file.write(json_test)

    json_train = json.dumps(train_data, indent=4)
    with open('train_rated.json', 'w') as json_file:
        json_file.write(json_train)
    return train_data, test_data


def stratified_split_usecases(usecases, test_size=0.2, randomseed=42):
    """
    splits the annotated dataset from the APE in the wild paper into bins based on usecases. No longer used. 
    """
    random.seed(randomseed)# make sure it is always same 
    train_set = []
    test_set = []
    
    # Shuffle and split each usecase group
    for usecase, items in usecases.items():
        random.shuffle(items)
        split_point = int(len(items) * (1 - test_size))
        train_set.extend(items[:split_point])
        test_set.extend(items[split_point:])

    json_test = json.dumps(test_set, indent=4)
    # Optionally, save to a file
    with open('test_usecases.json', 'w') as json_file:
        json_file.write(json_test)

    json_train = json.dumps(train_set, indent=4)
    # Optionally, save to a file
    with open('train_usecases.json', 'w') as json_file:
        json_file.write(json_train)
    
    return train_set, test_set




def parse_xml(file_paths, metadata_filename):
    """ Function to parse the xml files from the APE in the wild paper. 
    Saving each workflow as a list of tuples instead, along with other meta data in a dictionary """
    
    usecases = []
    id_ = 1

    for i, file_path in enumerate(file_paths):
        xls = pd.ExcelFile(file_path)
        
        for sheet_name in xls.sheet_names:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            
            for index, row in df.iterrows():
                
                workflow_steps = row[3].split(' -> ')
                workflow_tuples = [(workflow_steps[j], workflow_steps[j+1]) for j in range(len(workflow_steps) - 1)]
                
                pmid_workflow_tuples = convert_workflow_to_pmid_tuples([workflow_tuples], metadata_filename)[0] # expects and outputs list
                
                usecase_data = {
                    'ratingAvg': float(row[0]),
                    'expert1': float(row[1]),
                    'expert2': float(row[2]),
                    'workflow': workflow_tuples,
                    'pmid_workflow': pmid_workflow_tuples,
                    'usecase': i,
                    'scenario': sheet_name,
                    'id': id_ # creating a unique id to make deleting duplicates easier
                }
                id_ += 1
                usecases.append(usecase_data)

    json_data = json.dumps(usecases, indent=4)
    with open('usecases_rated.json', 'w') as json_file:
        json_file.write(json_data)

    return usecases


def parse_xml_unseparated_usecases(file_paths):
    """ parsing xml files split bu usecases without metadata. Old."""
    usecases = []

    for i, file_path in enumerate(file_paths, start=1):
        df = pd.read_excel(file_path, sheet_name=0)
        for index, row in df.iterrows():
            workflow_steps = row[3].split(' -> ')
            workflow_tuples = [(workflow_steps[j], workflow_steps[j+1]) for j in range(len(workflow_steps) - 1)]
            usecase_data = {
                'ratingAvg': float(row[0]),
                'expert1': float(row[1]),
                'expert2': float(row[2]),
                'workflow': workflow_tuples,
                'usecase': i
            }
            usecases.append(usecase_data)

    data = {"usecases": usecases}

    # print(data)
    # Convert to JSON string
    json_data = json.dumps(data, indent=4)


    # Optionally, save to a file
    with open('ratingsOfusecases_tuples.json', 'w') as json_file:
        json_file.write(json_data)

    return data


def pmid_name_converter(id_, metadata_filename): # TODO change to json 
    """ 
    Retrieves a list of all of the pmids for the primary publications in the data file 
    
    Parameters
    ----------
    id : str or int [needs to be int to count as pmid]
        the id (pmid or name) you want to switch to the other type (name or pmid)
    filename : str
        the name of the json file from which the script retrieves the pmids
    """
    with open(metadata_filename, "r") as f:
        metadata_file = json.load(f)

    tools = metadata_file['tools']
    
    if type(id) == int: # pmid
        try:
            name = [tool['name'] for tool in tools if tool['pmid'] == id_]
            return name
        except:
            return None
    else:
        try: 
            pmid = [tool['pmid'] for tool in tools if tool['name'] == id_]
            return pmid[0]
        except:
            print(f"No available pmid for {id_}")
            return None
        


def convert_workflow_to_pmid_tuples(workflows, metadata_filename):
    """ given a workflow represented as a list of tuples (edges) where the source and targets are tool names, this function converts them to tuples of PmIDs"""

    pmid_workflows = []
    for workflow in workflows:
        pmid_edges = []
        for edge in workflow:
            pmid_edges.append( ( pmid_name_converter(edge[0], metadata_filename), pmid_name_converter(edge[1], metadata_filename) ) )
        pmid_workflows.append(pmid_edges)

    return pmid_workflows

def avg_rating(repeated_workflows, workflow_json, metadata_filename =''):
    """calculates the average rating for workflows that are repeated within the dataset""" #TODO: Look at how much these vary for each expert  
    repeated_workflow_ratings = {
        workflow: [ next(item['ratingAvg'] for item in workflow_json if item['id'] == id_) for id_ in ids]
        for workflow, ids in repeated_workflows.items()
    }

    new_workflow_json = copy.deepcopy(workflow_json)
    for workflow, ids in repeated_workflows.items():
        for id_ in ids:
            for item in workflow_json:
                if item['id'] == id_:
                    new_workflow_json.remove(item)
    
    new_workflow_json_repeated = []
    for workflow, ids in repeated_workflows.items():
        new_workflow_json_repeated.append({'ratingAvg': float(np.mean(repeated_workflow_ratings[workflow])), 
                                  'workflow': ast.literal_eval(workflow),
                                  'pmid_workflow': convert_workflow_to_pmid_tuples([ast.literal_eval(workflow)], metadata_filename)[0]})


    return [new_workflow_json, new_workflow_json_repeated, new_workflow_json + new_workflow_json_repeated]

def unique_workflows(workflow_json, metadata_filename):
    """ 
    Takes all workflows in the APE in the wild dataset and returns only the unique ones, where repeated workflows are given the average rating of all ratings they recieved. 
    """
    all_workflows = {workflow['id']: str(sorted(workflow['workflow'])) for workflow in workflow_json} # making them sorted lists, so they arte hashable
    unique_workflows = {}
    repeated_workflows = {}

    for id_, workflow in all_workflows.items():
        if workflow not in unique_workflows.values() and  workflow not in repeated_workflows.values()  :
            unique_workflows[id_] = workflow
        else:
            if workflow in repeated_workflows.values(): # add new instance to 
                repeated_workflows[workflow].append(id_)
            else:
                repeated_workflows[workflow] = [id_]

            # Remove original form unique_workflows and move it to repeated
            original_id = next(key for key, value in unique_workflows.items() if value == workflow)
            del unique_workflows[original_id]
            repeated_workflows[workflow].append(original_id)
            

    return avg_rating(repeated_workflows, workflow_json, metadata_filename)



def get_pmids_from_file(filename: str) -> list:
    """
    Retrieves a list of all PMIDs for the primary publications in the specified meta data JSON file.

    :param filename: str
        The name of the JSON file from which to retrieve the PMIDs.

    :return: list
        List of PMIDs extracted from the JSON file.
    """

    with open(filename, "r") as f:
        metadata_file = json.load(f)
    tools = metadata_file['tools']

    return [tool['pmid'] for tool in tools]


async def get_citations(filename):
    """ download citations for all tools in the meta data file"""
    pmids = get_pmids_from_file(filename)
    async with aiohttp.ClientSession() as session:
        citation_list = []
        for article_id in tqdm(pmids, desc='Downloading citations from EuropePMC'):
            citation_ids = await pubmetric.data.europepmc_request(session, article_id)
            citation_list.append(citation_ids)
        return citation_list