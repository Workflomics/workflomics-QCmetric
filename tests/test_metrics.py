
from pubmetric.metrics import *
from pubmetric.workflow import parse_cwl_workflows
from pubmetric.network import create_citation_network
from datetime import datetime
import os
import math
import pickle
import asyncio
from example_graph import cocitation_graph, expected_edge_weights, pmid_workflow, dictionary_workflow
 
# def test_tool_level_average_sum(shared_datadir): #TODO update for new format
#     cwl_filename = os.path.join(shared_datadir, "candidate_workflow_repeated_tool.cwl")
#     graph_path = os.path.join(shared_datadir, "graph.pkl") # do I have to load it every time?
#     with open(graph_path, 'rb') as f:
#         graph = pickle.load(f) 
#     workflow = parse_cwl_workflows(graph=graph , cwl_filename=cwl_filename)  

#     graph = asyncio.run(create_citation_network(inpath=shared_datadir, test_size=20))
#     tool_scores = tool_average_sum(graph, workflow)
#     assert list(tool_scores.keys()) == ['ProteinProphet_02', 'StPeter_04', 'XTandem_01', 'XTandem_03'] # note this only tests the format is right 

# The rest of the tests are based on the example graph
def test_get_graph_edge_weight():
    for edge, expected_weight in expected_edge_weights.items():
        weight = get_graph_edge_weight(cocitation_graph, edge)
        assert weight == expected_weight

def test_workflow_level_average_sum():
    # obs see the problem here where this metrics prefers single edged nw with good connection (msConvert to Comet for ex will always be best then)
    assert workflow_average_sum(graph=cocitation_graph, workflow=pmid_workflow) == (2 + 1 + 0) / 3
    assert workflow_average_sum(graph=cocitation_graph, workflow=[('TA', 'TB')] ) == 0/1 # not connected

def test_connectivity():
    score = connectivity(cocitation_graph, workflow= dictionary_workflow)
    assert score == ( 2 + 2 + 1 + 0 + 0 + 0 ) / 6 

def test_workflow_weighted_connectivity():
    factor = 2
    score = workflow_weighted_connectivity(cocitation_graph, workflow=dictionary_workflow, factor=factor )
    assert score == ( 2 + 2 + 1 + 0 + 0 + 0 ) / 6 - 1 + factor* 1 # factor multiplied by workflow_average_sum score

def test_sqrt_workflow_average_sum():
    sqrt_score = transformed_workflow_average_sum(cocitation_graph, workflow=pmid_workflow, transform='sqrt')
    assert sqrt_score == round(( math.sqrt(2) + math.sqrt(1) + math.sqrt(0) ) / 3, 3)

def test_log_workflow_average_sum():
    log_score = transformed_workflow_average_sum(cocitation_graph, workflow=pmid_workflow, transform='log') #TODO pass dictinary to all- extract pmids within functions
    assert log_score == round((math.log(2 + 1) + math.log(1 + 1) + math.log(0 + 1)) / 3, 3)

def test_degree_workflow_average_sum():
    assert degree_workflow_average_sum(graph=cocitation_graph, workflow=pmid_workflow) == round((2 / (1.5) + 1 / (1.5) + 0/1 ) / 3, 3)

def test_workflow_edge_product():
    assert workflow_edge_product(graph=cocitation_graph, workflow=pmid_workflow) == round(2*1/3,3) # 0 values are not included

def test_log_workflow_edge_product():
    assert log_workflow_edge_product(graph=cocitation_graph, workflow=pmid_workflow) == round(math.log(2+1) * math.log(1+1)/3, 3) # 0 values are not included

def test_workflow_average_sum_age():
    TA_age = datetime.now().year-2015
    TC_age = datetime.now().year-2017
    TD_age = datetime.now().year-2018
    assert workflow_average_sum_age(graph=cocitation_graph, workflow=pmid_workflow) == round(( 2 / ((TA_age + TC_age) / 2)  +  1 / ((TC_age + TD_age) / 2) ) / 3, 3)

def test_connectivity_age():
    TA_age = datetime.now().year-2015
    TC_age = datetime.now().year-2017
    TD_age = datetime.now().year-2018
    score = connectivity_age(cocitation_graph, workflow= dictionary_workflow)
    assert score ==  round(( 2 / ((TA_age + TC_age) / 2)  +  2 / ((TA_age + TC_age) / 2)  + 1 / ((TD_age + TC_age) / 2)  ) / 6, 3)

def test_connectivity_min():
    score = connectivity_min(cocitation_graph, workflow= dictionary_workflow)
    assert score == ( ( 2 + 2 + 1 + 0 + 0 + 0 ) / 6 ) * 1 # since 1 is the nonzero min 

def test_connectivity_citation():
    TA_cite = 1
    TC_cite = 3
    TD_cite = 4
    score = connectivity_citation(cocitation_graph, workflow= dictionary_workflow)
    assert score == round(( 2 / ((TA_cite + TC_cite) / 2) + 2 / ((TA_cite + TC_cite) / 2) + 1 / ((TC_cite + TD_cite) / 2) + 0 + 0 + 0 ) / 6, 3)

def test_citations():
    score = citations(cocitation_graph, workflow= dictionary_workflow)
    assert score == statistics.median([1, 1, 3, 4]) # TA is counted twice. Cant argue what is more or less reasonable as it is not a reasonable metric