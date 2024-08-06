import os 
import igraph 
from pubmetric.workflow import *
import pickle


def test_parse_cwl_workflow_update(shared_datadir):
    graph_path = os.path.join(shared_datadir, "graph.pkl") # do I have to load it every time?
    with open(graph_path, 'rb') as f:
        graph = pickle.load(f) 
    cwl_filename = os.path.join(shared_datadir, "candidate_workflow_repeated_tool.cwl")
    workflow = parse_cwl_workflows(graph =graph, cwl_filename=cwl_filename)  
    
    assert workflow['edges'] == [('XTandem_01', 'ProteinProphet_02'), ('ProteinProphet_02', 'StPeter_04'), ('XTandem_03', 'StPeter_04')]


def test_parse_undocumented_workflows(shared_datadir):
    cwl_filename = os.path.join(shared_datadir, "candidate_workflow_repeated_tool.cwl")
    graph_path = os.path.join(shared_datadir, "graph.pkl") # do I have to load it every time? TODO
    with open(graph_path, 'rb') as f:
        graph = pickle.load(f) 

    workflow = parse_cwl_workflows(graph =graph, cwl_filename=cwl_filename)   
    undoc_workflow = parse_undocumented_workflows(graph =graph, cwl_filename=cwl_filename)   
    
    assert workflow['edges'] == [('XTandem_01', 'ProteinProphet_02'), ('ProteinProphet_02', 'StPeter_04'), ('XTandem_03', 'StPeter_04')]
    assert workflow == undoc_workflow




# def test_generate_pmid_edges(shared_datadir): # This is outdated now, dont know If i want to recreate it. TODO
#     metadata_filename = os.path.join(shared_datadir, "tool_metadata_test20_topic_0121_20250705.json")

#     name_workflow = [ ('XTandem', 'ProteinProphet'), ('XTandem', 'PeptideProphet'), ('ProteinProphet', 'StPeter'), ('PeptideProphet', 'StPeter') ]
#     expected_tuple_workflow = [('14976030','14632076' )  , ('14976030','12403597')  , ('14632076','29400476')  , ('12403597', '29400476')  ]
#                             # [ (XTandem, ProteinProphet), (XTandem, PeptideProphet), (ProteinProphet, StPeter), (PeptideProphet, StPeter) ]

#     faulty_name_workflow = [ ('XTandem', 'ProteinProphet'), ('XTandem', 'NotATOOL'), ('ProteinProphet', 'StPeter'), ('NotATOOL', 'StPeter') ]

#     reconnected_workflow = generate_pmid_edges(metadata_filename, name_workflow)
#     reconnected_faulty_workflow = generate_pmid_edges(metadata_filename, faulty_name_workflow, handle_missing='reconnect')
#     removed_faulty_workflow = generate_pmid_edges(metadata_filename, faulty_name_workflow, handle_missing='remove')
#     kept_faulty_workflow = generate_pmid_edges(metadata_filename, faulty_name_workflow, handle_missing='keep')

#     assert sorted(reconnected_workflow) == sorted(expected_tuple_workflow) # A wofklow where all PmIDs are in the metadatafile should not be changed
#     assert len(reconnected_faulty_workflow) == 3 # the two edges containing 'NotATOOL' should be turned into a single edge ('XTandem', 'StPeter')
#     assert len(removed_faulty_workflow) == 2 # the two edges containing 'NotATOOL' are removed
#     assert len(kept_faulty_workflow) == 4 and 'None' in kept_faulty_workflow[1] # the two edges containing 'NotATOOL' will contain a None 
#                                                 #TODO this should not be a string none but a none none