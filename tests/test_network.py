from collections import defaultdict
import asyncio
from pubmetric import network 
import example_graph as ex_graph

def test_citation_network_testsize(shared_datadir):
    """Test creating a graph from scratch"""
    graph = asyncio.run(network.create_network(load_graph=False,
                                               test_size=20,
                                               inpath=shared_datadir))
    assert len(graph.vs['pmid']) > 0
    assert sorted(graph.es.attributes()) == sorted(['weight',
                                                    'inverted_weight'])
    assert sorted(graph.vs.attributes()) == sorted(['age',
                                                    'name',
                                                    'pmid',
                                                    'nr_citations',
                                                    'degree'])  

def test_load_citation_network(shared_datadir):
    """Test loading a citation graph and extracting information from it"""
    graph = asyncio.run(network.create_network(load_graph=True, inpath = shared_datadir))
    assert len(graph.vs['pmid']) > 1200

def test_create_cocitation_graph():
    """Tests generating the example graph from the paper_citations dictionary"""
    graph = network.create_cocitation_graph(paper_citations=ex_graph.paper_citations)
    assert sorted(ex_graph.cocitation_expected_nodes) == sorted(graph.vs['name'])

def test_create_cocitation_graph_sizes():
    """Tests generating the example graph from the paper_citations dictionary,
    using the batch creation and the simple creation for smaller graph to make sure they
    are the same"""
    big_graph = network.create_cocitation_graph(paper_citations=ex_graph.paper_citations)
    small_graph = network.create_small_cocitation_graph(paper_citations=ex_graph.paper_citations)
    assert sorted(ex_graph.cocitation_expected_nodes) == sorted(big_graph.vs['name'])
    assert sorted(ex_graph.cocitation_expected_nodes) == sorted(small_graph.vs['name'])
    assert big_graph.isomorphic(small_graph)


def test_combine_counts():
    counts_list = [
        {('A', 'B'): 1, ('B', 'C'): 2},
        {('A', 'B'): 3, ('D', 'E'): 4}
    ]
    expected = defaultdict(int, {('A', 'B'): 4, ('B', 'C'): 2, ('D', 'E'): 4})
    assert network.combine_counts(counts_list) == expected

def test_add_attributes():
    """Tests the attribute addition after the cocitation graph is created"""
    no_attribute_graph = network.create_cocitation_graph(ex_graph.paper_citations)
    attribute_graph = network.add_graph_attributes(graph=no_attribute_graph, metadata_file=ex_graph.tool_metadata)
    assert sorted(attribute_graph.es['inverted_weight']) == sorted([0.5, 1.0, 1.0])
    assert 'weight' in attribute_graph.es.attributes()
    assert 'inverted_weight' in attribute_graph.es.attributes()
    assert 'age' in attribute_graph.vs.attributes()
    assert 'pmid' in attribute_graph.vs.attributes()
    assert 'nr_citations' in attribute_graph.vs.attributes()
    assert 'degree' in attribute_graph.vs.attributes()
