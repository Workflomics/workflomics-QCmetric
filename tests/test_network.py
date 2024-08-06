import asyncio
from pubmetric import network 
from example_graph import citation_graph, edges, tools, cocitation_expected_nodes, citation_expected_nodes, included_tools, cocitation_graph

def test_citation_network_testsize(shared_datadir): 
    graph = asyncio.run(network.create_citation_network(load_graph=False, test_size=20, inpath=shared_datadir))
    assert len(graph.vs['pmid']) > 0 

def test_load_citation_network(shared_datadir):
    graph = asyncio.run(network.create_citation_network(load_graph=True, inpath = shared_datadir)) 
    assert len(graph.vs['pmid']) > 1200

def test_create_cocitation_graph():
    incuded_tools = [tool for tool in citation_graph.vs['name'] if tool in tools]    
    graph = network.create_cocitation_graph(citation_graph, incuded_tools)
    assert sorted(cocitation_expected_nodes) == sorted(graph.vs['name'])

def test_create_graph():
    graph = network.create_graph(edges, included_tools , cocitation=False)
    print(graph.vs.attributes())
    assert sorted(citation_expected_nodes) == sorted(graph.vs['name'])

def test_get_citation_data():
    citation_test_tools = {'tools':[{'pmid':'14632076'}]} # Protein prophet, in mock metadata file structure 
    citation_test_edges = asyncio.run(network.get_citation_data(citation_test_tools))
    assert len(citation_test_edges) >= 2900 # it has 2965 citations currently (August 2024)

def test_invert_graph_weights():
    inverted_graph = network.add_inverted_edge_weights(cocitation_graph)
    assert sorted(inverted_graph.es['inverted_weight']) == sorted([0.5, 1.0, 1.0])
    assert inverted_graph.es.attributes() == ['weight', 'inverted_weight']