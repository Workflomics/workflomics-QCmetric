import pytest
from wfqc import network as nw
import igraph
import numpy as np
import json
import os
import asyncio
import shutil
### Creating a test network to confirm the functions are working ###

# Define the nodes 
tools = ['TA', 'TB', 'TC', 'TD', # connected cluster - included in final graph 
        # Separate cluster - included in final graph 
         'TE', 'TF',
        # Single disconnected cited - not included in final graph 
         'TG', 
        # Single disconnected not cited - not included in final graph 
         'TH']

citations = ['CA', 'CB', 'CC', 'CD', 'CE', 'CF', 'CG', 'CH', 'CI', 'CJ', 'CK', 'CL', 'CM', 'CN', 'CO', 'CP', 'CQ']


edges = [

    # Single citations of tools
    ('CA', 'TA'), ('CB', 'TB'), ('CC', 'TC'), ('CD', 'TD'), 
    ('CE', 'TE'), ('CF', 'TF'), ('CG', 'TG'),

    # Citations to multiple tools
    ('CJ', 'TA'), ('CJ', 'TB'),  
    ('CK', 'TA'), ('CK', 'TB'), ('CK', 'TC'),
    ('CL', 'TA'), ('CL', 'TB'), ('CL', 'TC'), ('CL', 'TD'), 
    
    # Duplicate edges
    ('CP', 'TE'), ('CP', 'TE'),

    # Tools citing each other
    ('TB', 'TC'), 

    # Tools citing themselves
    ('TA', 'TA'),

    # Disconnected cluster
    ('CQ', 'TE'), ('CQ', 'TF'), ('CO', 'TE'),
    ('CO', 'TF') 
]

nodes_in_final_network = ['TA', 'TB', 'TC', 'TD', 'TE', 'TF', 'CJ', 'CK', 'CL', 'CO', 'CQ' ]
tools_in_final_network = ['TA', 'TB', 'TC', 'TD', 'TE', 'TF']


Graph = igraph.Graph.TupleList(edges, directed=True)


#### TESTING ###


def test_testsize_citation_network(): # TODO: test on  fake data 
    G = nw.create_citation_network(loadData=False, testSize=50) # TODO: if no data then make data or ask if make data?
    assert len(G.vs['name']) > 0 

def test_load_citation_network(shared_datadir):
    inpath = os.path.join(shared_datadir, "out")
    G = nw.create_citation_network(loadData=True, inpath = inpath) # TODO: if no data then make data or ask if make data?
    assert len(G.vs['name']) > 0 


def test_cocitation_graph():
    incuded_tools = [tool for tool in Graph.vs['name'] if tool in tools] #could do interrsection    
    G = nw.cocitation_graph(Graph,incuded_tools)
    assert sorted(tools_in_final_network) == sorted(G.vs['name'])

def test_create_graph():
    G, included_tools, node_degree_dict = nw.create_graph(edges, tools, includeCitationNodes=True)
    print(np.sort(nodes_in_final_network), np.sort(G.vs['name']))
    assert sorted(nodes_in_final_network) == sorted(G.vs['name'])

# def test_download_data():
#     outpath = temp # then deleate 
#     edges, included_tools = asyncio.run(nw.download_data(outpath,testSize= 10,randomSeed = 42, topicID ="topic_0121"))
#     with open(outpath + '/tool_metadata_topic_*', "r") as f:
#         metadata_file = json.load(f)
#     tools_in_metafile = metadata_file['tools']['name']
#         # delete teh out dir
#     assert ['Comet', 'PeptideProphet', 'ProteinProphet', 'msconvert', 'ms_amanda'] in tools_in_metafile



def test_download_data():
    outpath = "temp_test_directory"
    
    try:
        # Create the directory
        os.makedirs(outpath, exist_ok=True)
        
        # Download the data
        edges, included_tools = asyncio.run(
            nw.download_data(outpath, testSize=10, randomSeed=42, topicID="topic_0121")
        )
        
        # Find the metadata file
        metadata_files = [f for f in os.listdir(outpath) if f.startswith('tool_metadata_topic_')]
        assert len(metadata_files) > 0, "No metadata files found."
        
        metadata_file_path = os.path.join(outpath, metadata_files[0])
        with open(metadata_file_path, "r") as f:
            metadata_file = json.load(f)
        
        tools_in_metafile = metadata_file['tools']['name']
        assert set(['Comet', 'PeptideProphet', 'ProteinProphet', 'msconvert', 'ms_amanda']).issubset(tools_in_metafile), \
            "Expected tools not found in metadata file."
    finally:
        # Delete the directory and its contents
        shutil.rmtree(outpath)


