import os 
from pubmetric.workflow import parse_cwl, parse_undocumented_workflows
import pickle


def test_parse_cwl_workflow_update(shared_datadir):
    graph_path = os.path.join(shared_datadir, "graph.pkl") # do I have to load it every time?
    with open(graph_path, 'rb') as f:
        graph = pickle.load(f) 
    cwl_filename = os.path.join(shared_datadir, "candidate_workflow_repeated_tool.cwl")
    workflow = parse_cwl(graph =graph, cwl_filename=cwl_filename)  
    
    assert workflow['edges'] == [('XTandem_01', 'ProteinProphet_02'), ('ProteinProphet_02', 'StPeter_04'), ('XTandem_03', 'StPeter_04')]


def test_parse_undocumented_workflows(shared_datadir):
    cwl_filename = os.path.join(shared_datadir, "candidate_workflow_repeated_tool.cwl")
    graph_path = os.path.join(shared_datadir, "graph.pkl") # do I have to load it every time? TODO
    with open(graph_path, 'rb') as f:
        graph = pickle.load(f) 

    workflow = parse_cwl(graph =graph, cwl_filename=cwl_filename)   
    undoc_workflow = parse_undocumented_workflows(graph =graph, cwl_filename=cwl_filename)   
    
    assert workflow['edges'] == [('XTandem_01', 'ProteinProphet_02'), ('ProteinProphet_02', 'StPeter_04'), ('XTandem_03', 'StPeter_04')]
    assert workflow == undoc_workflow

